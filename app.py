from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import requests, json, pandas as pd, time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# 1. FLASK APP SETUP
# ============================================================
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# ============================================================
# 2. CLIENT SETUP
# ============================================================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

USASPENDING_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"


# ============================================================
# 3. GPT SEARCH FOR SUPPLIERS
# ============================================================
def search_suppliers(product, location, price_min, price_max):
    query = f"""
    Search the web for suppliers that sell **{product}** in **{location}**.
    Include local manufacturers, distributors, and wholesalers.
    Prefer suppliers offering prices between ${price_min} and ${price_max}.

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
                print("⚠️ Could not parse GPT output; returning formatted error.")
                suppliers = [{
                    "name": "Error: Could not parse supplier data",
                    "location": "N/A",
                    "product_title": "N/A",
                    "units_sold": "N/A",
                    "price_range": "N/A",
                    "website": "N/A",
                    "contact": "N/A",
                    "description": text[:200] + "..." if len(text) > 200 else text
                }]
        else:
            print("⚠️ No JSON found in GPT output; returning formatted error.")
            suppliers = [{
                "name": "Error: No supplier data found",
                "location": "N/A",
                "product_title": "N/A",
                "units_sold": "N/A",
                "price_range": "N/A",
                "website": "N/A",
                "contact": "N/A",
                "description": "The AI could not find suppliers matching your criteria. Try adjusting your search parameters."
            }]

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
                "time_period": [{"start_date": "2018-01-01", "end_date": "2025-10-11"}],
                "award_type_codes": ["A", "B", "C", "D"]
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency"],
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
# 6. COMBINE EVERYTHING
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

        return jsonify({
            "success": True,
            "count": len(suppliers),
            "suppliers": suppliers
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

        return jsonify({
            "success": True,
            "count": len(suppliers),
            "suppliers": suppliers
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