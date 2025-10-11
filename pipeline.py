#!/usr/bin/env python3
"""
Consolidated end-to-end pipeline:
1. Fetch suppliers from Google Places API based on location + keywords
2. Feed suppliers into the scraping pipeline
3. Extract products and generate insights

Usage:
  python pipeline.py --keywords "industrial plastic supplier" \\
    --location "37.7749,-122.4194" \\
    --radius 50000 \\
    --max-suppliers 10 \\
    --max-pages 5 \\
    --output-dir data/results
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import from fetch_suppliers_smart
from fetch_suppliers_smart import fetch_suppliers_from_location

# Import from existing pipeline
try:
    from keywords import expand_keywords
    from sitemap import discover_product_urls
    from product_extract import extract_product
    from specs_normalize import normalize_specifications
    from scorer import score_products
    from store import save_products, create_summary_report
except ImportError as e:
    print(f"Error: Could not import pipeline modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def save_suppliers(suppliers: List[Dict], output_path: str) -> None:
    """Save suppliers to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(suppliers, f, indent=2)
    print(f"✓ Saved {len(suppliers)} suppliers to: {output_path}")


def run_pipeline(
    keywords: str,
    location: str,
    radius: int = 50000,
    max_suppliers: int = 10,
    max_pages: int = 5,
    delay: float = 1.0,
    output_dir: str = "data/results"
) -> Dict:
    """
    Run the full end-to-end pipeline.

    Args:
        keywords: Search keywords for products and location search
        location: Lat,lng coordinates for location search
        radius: Search radius in meters
        max_suppliers: Maximum number of suppliers to fetch
        max_pages: Maximum pages to scrape per supplier
        delay: Delay between requests in seconds
        output_dir: Directory to save results

    Returns:
        Dictionary with pipeline results and stats
    """
    print("\n" + "=" * 80)
    print("CONSOLIDATED PIPELINE - LOCATION-BASED SUPPLIER DISCOVERY & PRODUCT EXTRACTION")
    print("=" * 80)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    start_time = time.time()
    stats = {
        'start_time': datetime.utcnow().isoformat() + 'Z',
        'keywords': keywords,
        'location': location,
        'radius': radius
    }

    # =========================================================================
    # STEP 1: Fetch Suppliers from Location
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: FETCHING SUPPLIERS FROM LOCATION")
    print("=" * 80)

    suppliers = fetch_suppliers_from_location(
        keywords=keywords,
        location=location,
        radius=radius,
        max_results=max_suppliers
    )

    if not suppliers:
        print("\n✗ No suppliers found. Exiting.")
        return {'error': 'No suppliers found', 'stats': stats}

    # Save suppliers
    suppliers_file = os.path.join(output_dir, 'suppliers.json')
    save_suppliers(suppliers, suppliers_file)

    stats['suppliers_found'] = len(suppliers)

    # =========================================================================
    # STEP 2: Expand Keywords
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: EXPANDING KEYWORDS")
    print("=" * 80)

    print(f"Base keyword: '{keywords}'")
    keyword_terms = expand_keywords(keywords)
    print(f"Expanded to {len(keyword_terms)} terms")
    print(f"Sample terms: {keyword_terms[:10]}")

    stats['keyword_terms'] = len(keyword_terms)

    # =========================================================================
    # STEP 3: Crawl Suppliers & Extract Products
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: CRAWLING SUPPLIERS & EXTRACTING PRODUCTS")
    print("=" * 80)

    products = []
    processed_suppliers = 0

    for idx, supplier in enumerate(suppliers, 1):
        domain = supplier['domain']
        print(f"\n[{idx}/{len(suppliers)}] Processing: {supplier['name']} ({domain})")
        print("-" * 80)

        try:
            # Discover product URLs from sitemap
            print(f"  Discovering product URLs from sitemap...")
            product_urls = discover_product_urls(domain, cap=max_pages * 2)  # Get more to filter

            if not product_urls:
                print(f"  ✗ No product URLs found")
                continue

            print(f"  ✓ Found {len(product_urls)} potential product URLs")

            # Extract products
            supplier_products = []

            for url_idx, url_data in enumerate(product_urls[:max_pages], 1):
                url = url_data['url']
                print(f"  [{url_idx}/{min(max_pages, len(product_urls))}] Extracting: {url}")

                try:
                    product = extract_product(url, keyword_terms)

                    if product:
                        # Set supplier ID
                        product['supplier_id'] = supplier['supplier_id']

                        # Normalize specifications
                        specs_canonical = normalize_specifications(product.get('specs_raw', {}))
                        product['specs_canonical'] = specs_canonical

                        supplier_products.append(product)

                        print(f"    ✓ Extracted: {product['name']}")
                    else:
                        print(f"    ✗ No product data extracted")

                except Exception as e:
                    print(f"    ✗ Error: {e}")

                # Politeness delay
                if delay > 0:
                    time.sleep(delay)

            products.extend(supplier_products)
            print(f"\n  Summary: Extracted {len(supplier_products)} products from {domain}")

        except Exception as e:
            print(f"  ✗ Error processing {domain}: {e}")

        processed_suppliers += 1

        # Brief delay between suppliers
        if delay > 0:
            time.sleep(delay * 2)

    stats['suppliers_processed'] = processed_suppliers
    stats['products_extracted'] = len(products)

    # =========================================================================
    # STEP 4: Score & Save Products
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: SCORING & SAVING PRODUCTS")
    print("=" * 80)

    if products:
        # Score products
        print(f"Scoring {len(products)} products...")
        scored_products = score_products(products, keyword_terms)

        print(f"\nTop 10 products by relevance score:")
        for i, product in enumerate(scored_products[:10], 1):
            print(f"  {i}. {product['name']}")
            print(f"     Score: {product.get('score', 0):.2f} | Supplier: {product.get('supplier_id', 'N/A')[:8]}")
            print(f"     URL: {product.get('url', 'N/A')}")

        # Save results
        json_path = os.path.join(output_dir, 'products.json')
        csv_path = os.path.join(output_dir, 'products.csv')

        save_products(
            scored_products,
            json_path=json_path,
            csv_path=csv_path
        )

        # Create summary report
        summary_path = os.path.join(output_dir, 'summary.json')
        create_summary_report(scored_products, summary_path)

        stats['products_saved'] = len(scored_products)

        print(f"\n✓ Results saved:")
        print(f"  • JSON: {json_path}")
        print(f"  • CSV: {csv_path}")
        print(f"  • Summary: {summary_path}")

    else:
        print("\n✗ No products were extracted from any supplier")
        stats['products_saved'] = 0

    # =========================================================================
    # Final Stats
    # =========================================================================
    end_time = time.time()
    duration = end_time - start_time

    stats['end_time'] = datetime.utcnow().isoformat() + 'Z'
    stats['duration_seconds'] = round(duration, 2)

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.2f}s")
    print(f"Suppliers found: {stats['suppliers_found']}")
    print(f"Suppliers processed: {stats['suppliers_processed']}")
    print(f"Products extracted: {stats['products_extracted']}")
    print(f"Products saved: {stats['products_saved']}")

    # Save stats
    stats_path = os.path.join(output_dir, 'pipeline_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nPipeline stats saved to: {stats_path}")

    return {'success': True, 'stats': stats}


def main():
    parser = argparse.ArgumentParser(
        description="End-to-end pipeline: Location-based supplier discovery + product extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find industrial plastic suppliers near San Francisco
  python pipeline.py --keywords "industrial plastic supplier" \\
    --location "37.7749,-122.4194" \\
    --radius 50000 \\
    --max-suppliers 10 \\
    --max-pages 5

  # Find electronics distributors near New York
  python pipeline.py --keywords "electronics distributor" \\
    --location "40.7128,-74.0060" \\
    --radius 30000 \\
    --max-suppliers 5 \\
    --max-pages 3 \\
    --output-dir data/nyc_results

  # Find hardware suppliers near Chicago with custom delay
  python pipeline.py --keywords "hardware supplier industrial" \\
    --location "41.8781,-87.6298" \\
    --radius 40000 \\
    --max-suppliers 8 \\
    --max-pages 4 \\
    --delay 2.0
        """
    )

    parser.add_argument(
        '--keywords',
        type=str,
        required=True,
        help='Search keywords for products and location search (e.g., "industrial plastic supplier")'
    )

    parser.add_argument(
        '--location',
        type=str,
        required=True,
        help='Location as lat,lng (e.g., "37.7749,-122.4194" for San Francisco)'
    )

    parser.add_argument(
        '--radius',
        type=int,
        default=50000,
        help='Search radius in meters (default: 50000 = 50km)'
    )

    parser.add_argument(
        '--max-suppliers',
        type=int,
        default=10,
        help='Maximum number of suppliers to fetch and process (default: 10)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=5,
        help='Maximum pages to scrape per supplier (default: 5)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/results',
        help='Output directory for results (default: data/results)'
    )

    args = parser.parse_args()

    try:
        result = run_pipeline(
            keywords=args.keywords,
            location=args.location,
            radius=args.radius,
            max_suppliers=args.max_suppliers,
            max_pages=args.max_pages,
            delay=args.delay,
            output_dir=args.output_dir
        )

        if result.get('success'):
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n✗ Pipeline cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
