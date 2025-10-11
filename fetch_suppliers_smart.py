#!/usr/bin/env python3
"""
Enhanced Google Places API supplier fetcher with intelligent keyword-based search.
Optimizes location search by using relevant place types derived from keywords.
"""

import requests
import json
import argparse
import hashlib
from datetime import datetime
from typing import List, Dict, Tuple
import time

# Google Places API key
API_KEY = "AIzaSyA1u6qkB1hak2JWSgB6JURDnMEgSnPbEEA"

# Keyword to place type mapping
KEYWORD_TO_PLACE_TYPES = {
    # Industrial & Manufacturing
    'industrial': ['store', 'hardware_store', 'home_goods_store'],
    'manufacturing': ['store', 'hardware_store'],
    'supplier': ['store', 'hardware_store', 'home_goods_store'],
    'distributor': ['store', 'hardware_store'],
    'wholesaler': ['store'],

    # Electronics
    'electronics': ['electronics_store', 'store'],
    'semiconductor': ['electronics_store', 'store'],
    'component': ['electronics_store', 'hardware_store', 'store'],

    # Materials
    'plastic': ['hardware_store', 'store'],
    'metal': ['hardware_store', 'store'],
    'steel': ['hardware_store', 'store'],
    'aluminum': ['hardware_store', 'store'],
    'wood': ['hardware_store', 'store'],
    'chemical': ['store'],

    # Hardware & Tools
    'hardware': ['hardware_store', 'store'],
    'tool': ['hardware_store', 'store'],
    'equipment': ['store', 'hardware_store'],
    'machinery': ['store'],

    # Specialty
    'gasket': ['hardware_store', 'store'],
    'fastener': ['hardware_store', 'store'],
    'valve': ['hardware_store', 'store'],
    'pump': ['hardware_store', 'store'],
    'bearing': ['hardware_store', 'store'],

    # Building materials
    'building': ['hardware_store', 'home_goods_store', 'store'],
    'construction': ['hardware_store', 'store'],
    'plumbing': ['hardware_store', 'plumber', 'store'],
    'electrical': ['electrician', 'electronics_store', 'hardware_store', 'store'],
    'hvac': ['store'],
}


def extract_place_types_from_keywords(keywords: str) -> List[str]:
    """
    Extract relevant Google Place types from search keywords.

    Args:
        keywords: Search keywords (e.g., "industrial plastic supplier")

    Returns:
        List of relevant place types for Google Places API
    """
    keywords_lower = keywords.lower()
    place_types = set()

    # Check each keyword mapping
    for keyword, types in KEYWORD_TO_PLACE_TYPES.items():
        if keyword in keywords_lower:
            place_types.update(types)

    # Default fallback if no matches
    if not place_types:
        place_types = {'store', 'hardware_store'}

    return list(place_types)


def generate_supplier_id(name: str) -> str:
    """Generate a unique supplier ID from the name."""
    return hashlib.md5(name.encode()).hexdigest()[:16]


def extract_state_from_address(address_components: List[Dict]) -> str:
    """Extract state abbreviation from address components."""
    for component in address_components:
        if "administrative_area_level_1" in component.get("types", []):
            return component.get("short_name", "")
    return ""


def extract_country_from_address(address_components: List[Dict]) -> str:
    """Extract country code from address components."""
    for component in address_components:
        if "country" in component.get("types", []):
            return component.get("short_name", "")
    return ""


def extract_domain_from_website(website: str) -> str:
    """Extract domain from website URL."""
    if not website:
        return ""
    # Remove protocol
    domain = website.replace("http://", "").replace("https://", "")
    # Remove path
    domain = domain.split("/")[0]
    # Remove www
    domain = domain.replace("www.", "")
    return domain


def fetch_place_details(place_id: str) -> Dict:
    """Fetch detailed information for a specific place."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,website,address_components,formatted_address,types",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("result", {})
    return {}


def search_nearby_places(
    query: str,
    location: str,
    radius: int = 50000,
    place_types: List[str] = None
) -> List[Dict]:
    """
    Search for places near a location using Text Search.

    Args:
        query: Search query
        location: Lat,lng coordinates
        radius: Search radius in meters
        place_types: List of place types to filter by

    Returns:
        List of place results
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    all_results = []

    # If place types specified, search for each type
    if place_types:
        for place_type in place_types[:3]:  # Limit to top 3 types to save API calls
            params = {
                "query": query,
                "location": location,
                "radius": radius,
                "type": place_type,
                "key": API_KEY
            }

            response = requests.get(url, params=params)

            if response.status_code != 200:
                print(f"  Warning: API returned status {response.status_code} for type '{place_type}'")
                continue

            data = response.json()

            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                print(f"  Warning: API status '{data.get('status')}' for type '{place_type}'")
                continue

            results = data.get("results", [])
            all_results.extend(results)
            print(f"  Found {len(results)} results for place type '{place_type}'")

            # Small delay between requests
            time.sleep(0.3)
    else:
        # No place types - do general search
        params = {
            "query": query,
            "location": location,
            "radius": radius,
            "key": API_KEY
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") in ["OK", "ZERO_RESULTS"]:
                all_results = data.get("results", [])

    # Deduplicate by place_id
    seen_ids = set()
    unique_results = []
    for result in all_results:
        place_id = result.get("place_id")
        if place_id and place_id not in seen_ids:
            seen_ids.add(place_id)
            unique_results.append(result)

    return unique_results


def fetch_suppliers_from_location(
    keywords: str,
    location: str,
    radius: int = 50000,
    max_results: int = 20
) -> List[Dict]:
    """
    Fetch suppliers from a location using intelligent keyword-based search.

    Args:
        keywords: Search keywords (e.g., "industrial plastic supplier")
        location: Lat,lng coordinates
        radius: Search radius in meters
        max_results: Maximum number of suppliers to return

    Returns:
        List of supplier dictionaries
    """
    print(f"\nAnalyzing keywords: '{keywords}'")

    # Extract relevant place types from keywords
    place_types = extract_place_types_from_keywords(keywords)
    print(f"Relevant place types: {place_types}")

    # Search for places
    print(f"\nSearching near location: {location} (radius: {radius}m)")
    places = search_nearby_places(keywords, location, radius, place_types)

    print(f"\nTotal unique places found: {len(places)}")

    suppliers = []
    seen_domains = set()

    for place in places:
        if len(suppliers) >= max_results:
            break

        # Fetch detailed information
        place_details = fetch_place_details(place["place_id"])

        name = place.get("name", "")
        website = place_details.get("website", "")
        domain = extract_domain_from_website(website)

        # Skip if no website/domain or duplicate
        if not domain or domain in seen_domains:
            continue

        seen_domains.add(domain)

        address_components = place_details.get("address_components", [])
        country = extract_country_from_address(address_components)
        state = extract_state_from_address(address_components)

        supplier = {
            "supplier_id": generate_supplier_id(name),
            "name": name,
            "domain": domain,
            "country": country,
            "state": state,
            "sources": ["GOOGLE_PLACES_API"],
            "last_seen_at": datetime.utcnow().isoformat() + "Z"
        }

        suppliers.append(supplier)
        print(f"  ✓ Added: {name} ({domain})")

        # Small delay to avoid rate limits
        time.sleep(0.1)

    return suppliers


def main():
    parser = argparse.ArgumentParser(
        description="Smart supplier fetcher using Google Places API with keyword-based optimization"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        required=True,
        help='Search keywords (e.g., "industrial plastic supplier", "electronics distributor")'
    )
    parser.add_argument(
        "--location",
        type=str,
        required=True,
        help='Location as lat,lng (e.g., "37.7749,-122.4194" for San Francisco)'
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=50000,
        help="Search radius in meters (default: 50000)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of suppliers to fetch (default: 20)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/suppliers_location.json",
        help="Output file path (default: data/suppliers_location.json)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("SMART SUPPLIER DISCOVERY - GOOGLE PLACES API")
    print("=" * 70)

    suppliers = fetch_suppliers_from_location(
        keywords=args.keywords,
        location=args.location,
        radius=args.radius,
        max_results=args.max_results
    )

    print(f"\n{'=' * 70}")
    print(f"RESULTS: Found {len(suppliers)} suppliers with valid websites")
    print("=" * 70)

    # Save to file
    with open(args.output, "w") as f:
        json.dump(suppliers, f, indent=2)

    print(f"\n✓ Saved to: {args.output}")

    # Show sample
    if suppliers:
        print(f"\nSample suppliers:")
        for supplier in suppliers[:5]:
            print(f"  • {supplier['name']} - {supplier['domain']} ({supplier['state']})")


if __name__ == "__main__":
    main()
