from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import requests, json, pandas as pd, time, re
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import numpy as np
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from rfp_generation.rfp_generator import generate_rfp_from_supplier

# Load environment variables
load_dotenv()

# Download VADER lexicon for sentiment analysis (only runs once if not already downloaded)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# ============================================================
# 1. FLASK APP SETUP
# ============================================================
app = Flask(__name__)
# Enable CORS for frontend communication with proper configuration
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5001",
            "http://10.173.105.175:3000",
            "http://10.173.105.175:3001"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# ============================================================
# 2. CLIENT SETUP
# ============================================================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

USASPENDING_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

# Initialize VADER sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()


# ============================================================
# 3. GPT SEARCH FOR SUPPLIERS
# ============================================================
def search_suppliers(product, location, price_min, price_max):
    query = f"""
    Search the web for suppliers that sell **{product}** in **{location}**.
    Include local manufacturers, distributors, and wholesalers.
    Prefer suppliers offering prices between ${price_min} and ${price_max}.
    If you can't find suppliers or are unsure, return none.

    For each supplier, include:
    - 'product_title': the specific item or SKU (e.g., "5052-H32 Aluminum Sheet 4x8")
    - 'units_sold': the unit of sale (e.g., "per sheet", "per pound", "per roll", "per foot") 
      — or, if available, the quantity currently in stock / available for purchase.
    - 'price_range': exact price if available or range (e.g., "$85 per sheet" or "$2.50–$3.00 per lb")
    - 'website': supplier’s main website
    - 'contact': email or phone number
    - 'description': short description of the supplier or product focus

    Return a valid JSON list:
    [
      {{
        "name": "Supplier Name",
        "location": "City, State",
        "product_title": "Specific product name",
        "units_sold": "Unit of sale or quantity available",
        "price_range": "$X - $Y per [unit]",
        "website": "https://example.com",
        "contact": "email or phone",
        "description": "short summary"
      }}
    ]
    Up to 30 suppliers - as many as possible.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that searches for suppliers and returns valid JSON."},
            {"role": "user", "content": query}
        ],
        max_tokens=2500,
        temperature=0.7,
    )

    text = response.choices[0].message.content

    # Try to extract JSON from the response
    try:
        # First, try to parse the entire response as JSON
        suppliers = json.loads(text)
    except Exception:
        # If that fails, try to find JSON within the text (GPT might add explanation text)
        import re
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            try:
                suppliers = json.loads(json_match.group(0))
            except Exception:
                print("⚠️ Could not parse GPT output; returning empty list.")
                suppliers = []
        else:
            print("⚠️ No JSON found in GPT output; returning empty list.")
            suppliers = []

    # Ensure all suppliers have required fields
    formatted_suppliers = []
    for supplier in suppliers:
        if isinstance(supplier, dict):
            formatted_suppliers.append({
                "name": supplier.get("name", "Unknown Supplier"),
                "location": supplier.get("location", "N/A"),
                "product_title": supplier.get("product_title", "N/A"),
                "units_sold": supplier.get("units_sold", "N/A"),
                "price_range": supplier.get("price_range", "N/A"),
                "website": supplier.get("website", "N/A"),
                "contact": supplier.get("contact", "N/A"),
                "description": supplier.get("description", "No description available")
            })

    return formatted_suppliers if formatted_suppliers else suppliers


# ============================================================
# 4. FETCH GOVERNMENT CONTRACTS
# ============================================================
def fetch_past_contracts(company_name):
    try:
        payload = {
            "filters": {
                "recipient_search_text": [company_name],
                "award_type_codes": ["A", "B", "C", "D"]
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Start Date", "End Date"],
            "limit": 3,
            "page": 1
        }
        r = requests.post(USASPENDING_URL, json=payload, timeout=10)
        data = r.json()
        results = data.get("results", [])
        if not results:
            return "None found"
        summary = []
        for award in results:
            agency = award.get("Awarding Agency")
            amt = award.get("Award Amount")
            start_date = award.get("Start Date")
            end_date = award.get("End Date")

            # Only include dates if both are available
            if start_date and end_date:
                summary.append(f"{agency}: ${amt:,.0f} ({start_date} - {end_date})")
            else:
                summary.append(f"{agency}: ${amt:,.0f}")
        return "; ".join(summary)
    except Exception as e:
        return f"Error: {e}"


# ============================================================
# 5. FETCH ONLINE REVIEWS & MENTIONS
# ============================================================
def fetch_web_reviews(company_name, location):
    query = f"""
    Search the web for reviews, customer feedback, or past project/contract mentions
    for the supplier **{company_name}** located near **{location}**.
    Include Google reviews, Yelp, BBB, or industry references.
    Summarize the overall reputation and any known contract/project mentions.
    Return a concise 2–4 sentence summary.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that searches for company reviews and reputation information."},
                {"role": "user", "content": query}
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error fetching reviews: {e}"


# ============================================================
# 6. RANKING SYSTEM
# ============================================================

# Initialize geocoder (reuse instance)
geolocator = Nominatim(user_agent="nexa_supplier_search")

def extract_price_from_range(price_range):
    """Extract numeric price from price range string"""
    try:
        # Extract all numbers from the price range
        numbers = re.findall(r'\d+\.?\d*', str(price_range))
        if not numbers:
            return None
        # If there's a range, take the average
        prices = [float(n) for n in numbers]
        return sum(prices) / len(prices)
    except:
        return None


def get_embedding(text):
    """Get OpenAI embedding for text"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    if vec1 is None or vec2 is None:
        return 0.0
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


def calculate_location_similarity(supplier_location, target_location):
    """Calculate location proximity score (0-1) using geodesic distance"""
    if not supplier_location or supplier_location == "N/A":
        return 0.3  # Default score for missing location

    try:
        # Geocode both locations
        location1 = geolocator.geocode(supplier_location, timeout=5)
        location2 = geolocator.geocode(target_location, timeout=5)

        if not location1 or not location2:
            # Fallback to string matching if geocoding fails
            if supplier_location.lower() == target_location.lower():
                return 1.0
            return 0.3

        # Get coordinates
        coords1 = (location1.latitude, location1.longitude)
        coords2 = (location2.latitude, location2.longitude)

        # Calculate distance in kilometers
        distance_km = geodesic(coords1, coords2).km

        # Score based on distance (closer = better)
        # 0 km = 1.0, 50 km = 0.8, 100 km = 0.6, 200 km = 0.4, 500+ km = 0.1
        if distance_km == 0:
            return 1.0
        elif distance_km < 50:
            return 1.0 - (distance_km / 50) * 0.2
        elif distance_km < 100:
            return 0.8 - ((distance_km - 50) / 50) * 0.2
        elif distance_km < 200:
            return 0.6 - ((distance_km - 100) / 100) * 0.2
        elif distance_km < 500:
            return 0.4 - ((distance_km - 200) / 300) * 0.3
        else:
            return 0.1

    except Exception as e:
        print(f"Geocoding error: {e}")
        # Fallback to string matching
        if supplier_location.lower() == target_location.lower():
            return 1.0
        return 0.3


def calculate_keyword_similarity(description, product_title, search_product):
    """Calculate keyword similarity score (0-1) using cosine similarity of embeddings"""
    if not description or description == "N/A":
        description = ""
    if not product_title or product_title == "N/A":
        product_title = ""

    # Combine description and product title
    supplier_text = f"{product_title} {description}".strip()

    if not supplier_text or not search_product:
        return 0.3

    # Get embeddings
    supplier_embedding = get_embedding(supplier_text)
    search_embedding = get_embedding(search_product)

    if supplier_embedding is None or search_embedding is None:
        # Fallback to simple keyword matching
        text = supplier_text.lower()
        search_keywords = search_product.lower().split()
        matches = sum(1 for keyword in search_keywords if keyword in text)
        return min(matches / len(search_keywords), 1.0) if search_keywords else 0.3

    # Calculate cosine similarity
    similarity = cosine_similarity(supplier_embedding, search_embedding)

    # Normalize to 0-1 (cosine similarity is already -1 to 1, but typically 0 to 1 for similar content)
    return max(0.0, min(1.0, similarity))


def calculate_contract_score(past_contracts):
    """Calculate government contract bonus score (0-1)"""
    if not past_contracts or past_contracts == "None found" or past_contracts == "None":
        return 0.0

    if "Error" in past_contracts:
        return 0.0

    # Count number of contracts mentioned (separated by semicolons)
    contract_count = len(past_contracts.split(';'))

    # More contracts = higher score, max out at 1.0
    return min(contract_count * 0.3, 1.0)


def calculate_review_score(reviews):
    """Calculate review strength score (0-1) using NLTK VADER sentiment analysis"""
    if not reviews or reviews == "None":
        return 0.5  # Neutral score for no reviews

    if "Error" in reviews:
        return 0.3

    try:
        # Use VADER sentiment analyzer
        sentiment_scores = sentiment_analyzer.polarity_scores(reviews)

        # Get compound score (-1 to 1, where -1 is most negative, 1 is most positive)
        compound_score = sentiment_scores['compound']

        # Normalize compound score to 0-1 range
        # Compound: -1 to 1 -> normalized: 0 to 1
        normalized_score = (compound_score + 1) / 2

        return max(0.0, min(1.0, normalized_score))

    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        # Fallback to neutral score
        return 0.5


def rank_suppliers(suppliers, search_product, search_location, price_min, price_max):
    """
    Rank suppliers based on multiple criteria and add a score to each.

    Scoring criteria (all normalized to 0-1):
    - Price proximity (30%): How close to the target price range
    - Location proximity (25%): How close to the target location (geodesic distance)
    - Keyword similarity (20%): Product/description match using embeddings
    - Government contracts (15%): Bonus for having government contracts
    - Review strength (10%): Quality of reviews/reputation

    Returns suppliers sorted by score (highest first)
    """
    target_price_mid = (price_min + price_max) / 2
    target_price_range = price_max - price_min

    for supplier in suppliers:
        scores = {
            'price': 0.0,
            'location': 0.0,
            'keywords': 0.0,
            'contracts': 0.0,
            'reviews': 0.0
        }

        # 1. Price proximity score (30%)
        supplier_price = extract_price_from_range(supplier.get('price_range', ''))
        if supplier_price:
            # Calculate how far from target range
            if price_min <= supplier_price <= price_max:
                # Perfect - within range
                price_deviation = abs(supplier_price - target_price_mid) / (target_price_range / 2) if target_price_range > 0 else 0
                scores['price'] = 1.0 - (price_deviation * 0.3)  # Small penalty for being away from midpoint
            else:
                # Outside range - penalize based on distance
                if supplier_price < price_min:
                    distance = price_min - supplier_price
                else:
                    distance = supplier_price - price_max
                # Normalize distance (further = lower score)
                scores['price'] = max(0, 1.0 - (distance / target_price_mid)) if target_price_mid > 0 else 0.3
        else:
            scores['price'] = 0.3  # Default for missing price

        # 2. Location proximity score (25%) - using geopy
        scores['location'] = calculate_location_similarity(
            supplier.get('location', ''),
            search_location
        )

        # 3. Keyword similarity score (20%) - using embeddings
        scores['keywords'] = calculate_keyword_similarity(
            supplier.get('description', ''),
            supplier.get('product_title', ''),
            search_product
        )

        # 4. Government contracts bonus (15%)
        scores['contracts'] = calculate_contract_score(
            supplier.get('past_contracts', '')
        )

        # 5. Review strength score (10%)
        scores['reviews'] = calculate_review_score(
            supplier.get('reviews_mentions', '')
        )

        # Calculate weighted total score (0-100)
        total_score = (
            scores['price'] * 30 +
            scores['location'] * 25 +
            scores['keywords'] * 20 +
            scores['contracts'] * 15 +
            scores['reviews'] * 10
        )

        # Add scores to supplier
        supplier['score'] = round(total_score, 1)
        supplier['score_breakdown'] = {
            'price': round(scores['price'] * 30, 1),
            'location': round(scores['location'] * 25, 1),
            'keywords': round(scores['keywords'] * 20, 1),
            'contracts': round(scores['contracts'] * 15, 1),
            'reviews': round(scores['reviews'] * 10, 1)
        }

    # Sort by score (highest first)
    suppliers.sort(key=lambda x: x.get('score', 0), reverse=True)

    return suppliers


# ============================================================
# 7. COMBINE EVERYTHING
# ============================================================
def get_suppliers_with_contracts_and_reviews(product, location, price_min, price_max):
    suppliers = search_suppliers(product, location, price_min, price_max)
    enriched = []

    for s in suppliers:
        name = s.get("name")
        print(f"🔍 Checking contracts and reviews for {name}...")

        # Add government past contracts
        contracts = fetch_past_contracts(name) if name else "None"

        # Add online reviews
        reviews = fetch_web_reviews(name, location) if name else "None"

        # Fill missing new fields if GPT skips them
        s["product_title"] = s.get("product_title", "N/A")
        s["units_sold"] = s.get("units_sold", "N/A")
        s["past_contracts"] = contracts
        s["reviews_mentions"] = reviews

        enriched.append(s)
        time.sleep(2)

    df = pd.DataFrame(enriched)
    df.to_csv("suppliers_with_contracts_reviews_units.csv", index=False)
    return df


# ============================================================
# 7. API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Backend API is running"})


@app.route('/api/search', methods=['POST'])
def api_search_suppliers():
    """
    Search for suppliers based on product, location, and price range.

    Request body:
    {
        "product": "aluminum sheets",
        "location": "Buffalo, New York",
        "price_min": 50,
        "price_max": 300
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['product', 'location', 'price_min', 'price_max']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        product = data['product']
        location = data['location']
        price_min = float(data['price_min'])
        price_max = float(data['price_max'])

        # Get suppliers
        suppliers = search_suppliers(product, location, price_min, price_max)

        # Rank suppliers by score
        ranked_suppliers = rank_suppliers(suppliers, product, location, price_min, price_max)

        return jsonify({
            "success": True,
            "count": len(ranked_suppliers),
            "suppliers": ranked_suppliers
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/search/detailed', methods=['POST'])
def api_search_suppliers_detailed():
    """
    Search for suppliers with contracts and reviews.

    Request body:
    {
        "product": "aluminum sheets",
        "location": "Buffalo, New York",
        "price_min": 50,
        "price_max": 300
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['product', 'location', 'price_min', 'price_max']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        product = data['product']
        location = data['location']
        price_min = float(data['price_min'])
        price_max = float(data['price_max'])

        # Get enriched suppliers
        df = get_suppliers_with_contracts_and_reviews(product, location, price_min, price_max)

        # Convert DataFrame to JSON
        suppliers = df.to_dict('records')

        # Rank suppliers by score
        ranked_suppliers = rank_suppliers(suppliers, product, location, price_min, price_max)

        return jsonify({
            "success": True,
            "count": len(ranked_suppliers),
            "suppliers": ranked_suppliers
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/contracts/<company_name>', methods=['GET'])
def api_get_contracts(company_name):
    """Get government contracts for a specific company"""
    try:
        contracts = fetch_past_contracts(company_name)
        return jsonify({
            "success": True,
            "company": company_name,
            "contracts": contracts
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/reviews', methods=['POST'])
def api_get_reviews():
    """
    Get reviews for a specific company.

    Request body:
    {
        "company_name": "Industrial Parts Co.",
        "location": "Buffalo, New York"
    }
    """
    try:
        data = request.get_json()

        if 'company_name' not in data or 'location' not in data:
            return jsonify({
                "error": "Missing required fields: company_name, location"
            }), 400

        company_name = data['company_name']
        location = data['location']

        reviews = fetch_web_reviews(company_name, location)

        return jsonify({
            "success": True,
            "company": company_name,
            "location": location,
            "reviews": reviews
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/rfp/generate', methods=['POST'])
def api_generate_rfp():
    """
    Generate RFP using GPT-4 with Jinja2 templates and export as PDF.

    Request body:
    {
        "supplier": {...},  # Supplier object from search results
        "search_data": {
            "product": "aluminum sheets",
            "location": "Buffalo, NY",
            "priceMin": "50",
            "priceMax": "300"
        },
        "rfp_requirements": {
            "title": "RFP for Aluminum Supply",
            "category": "Industrial Materials",
            "location": "Buffalo, NY",
            "deliveryDate": "2026-06-01",
            "budget": "$50,000 - $100,000",
            "standards": "ISO 9001, ASTM B209",
            "additionalRequirements": "...",
            "client_name": "Nexa",
            "submission_deadline": "December 15, 2025",
            "submission_email": "procurement@nexa.org",
            "contract_length": "1 year"
        }
    }
    """
    try:
        data = request.get_json()

        # Extract data
        supplier_data = data.get('supplier', {})
        search_data = data.get('search_data', {})
        rfp_requirements = data.get('rfp_requirements', {})

        # Create default supplier if none provided
        if not supplier_data or supplier_data is None:
            supplier_data = {
                "name": "To Be Determined",
                "location": rfp_requirements.get('location', 'N/A'),
                "product_title": search_data.get('product', rfp_requirements.get('title', 'Product')),
                "price_range": rfp_requirements.get('budget', 'N/A'),
                "website": "N/A",
                "contact": "N/A",
                "description": "Supplier to be determined through RFP process"
            }

        if not rfp_requirements.get('title'):
            return jsonify({
                "error": "RFP title is required"
            }), 400

        # Generate RFP using the existing Python module
        result = generate_rfp_from_supplier(
            supplier_data=supplier_data,
            search_data=search_data,
            rfp_requirements=rfp_requirements
        )

        return jsonify({
            "success": True,
            "markdown": result['markdown'],
            "pdf_filename": result['pdf_filename'],
            "pdf_content": result['pdf_content']
        })

    except Exception as e:
        print(f"RFP generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

# Old file-based download endpoint removed - RFPs are now stored in database
# Use Next.js API route /api/rfp/[rfpId] instead


@app.route('/api/rfp/regenerate-pdf', methods=['POST'])
def api_regenerate_pdf():
    """Regenerate PDF from markdown content"""
    try:
        data = request.json
        markdown_text = data.get('markdown', '')

        if not markdown_text:
            return jsonify({"error": "Markdown content is required"}), 400

        # Import the PDF generation function
        from rfp_generation.utils.pdf_utils import markdown_to_pdf_content
        import base64

        # Generate PDF from markdown
        pdf_bytes = markdown_to_pdf_content(markdown_text)

        # Encode to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        return jsonify({
            "success": True,
            "pdf_content": pdf_base64
        })

    except Exception as e:
        print(f"PDF regeneration error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


# ============================================================
# 8. RUN THE APP
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"

    print(f"🚀 Starting Nexa Backend API on port {port}")
    print(f"📍 Health check: http://localhost:{port}/api/health")
    print(f"🔍 Search endpoint: http://localhost:{port}/api/search")

    app.run(host="0.0.0.0", port=port, debug=debug)