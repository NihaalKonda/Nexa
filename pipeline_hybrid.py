#!/usr/bin/env python3
"""
Hybrid Pipeline: Combines existing suppliers with location-based discovery

Strategy:
1. Load existing vetted suppliers (high quality)
2. Discover nearby suppliers from location (local options)
3. Merge and deduplicate
4. Prioritize suppliers by quality score
5. Run product extraction on combined list

Usage:
  python pipeline_hybrid.py \
    --keywords "PETG plastic sheets" \
    --location "37.7749,-122.4194" \
    --existing-suppliers data/suppliers.json \
    --max-local-suppliers 5 \
    --max-total-suppliers 15 \
    --max-pages 10
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Set

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
    sys.exit(1)


def load_existing_suppliers(suppliers_file: str) -> List[Dict]:
    """Load existing suppliers from JSON file."""
    try:
        with open(suppliers_file, 'r') as f:
            suppliers = json.load(f)
        print(f"✓ Loaded {len(suppliers)} existing suppliers from {suppliers_file}")
        return suppliers
    except FileNotFoundError:
        print(f"⚠ No existing suppliers file found at {suppliers_file}")
        return []
    except Exception as e:
        print(f"✗ Error loading suppliers: {e}")
        return []


def score_supplier_quality(supplier: Dict) -> int:
    """
    Score supplier quality based on various factors.
    Higher score = better quality/more reliable.

    Returns:
        Quality score (0-100)
    """
    score = 50  # Base score

    # Check domain quality indicators
    domain = supplier.get('domain', '').lower()

    # Known high-quality suppliers get bonus
    known_quality = [
        'mcmaster.com', 'grainger.com', 'usplastic.com',
        'professionalplastics.com', 'fastenal.com', 'mscdirect.com',
        'digikey.com', 'mouser.com', 'arrow.com', 'avnet.com'
    ]

    if any(kq in domain for kq in known_quality):
        score += 30

    # Source indicates quality
    sources = supplier.get('sources', [])
    if 'PUBLIC' in sources:
        score += 10  # Vetted public suppliers
    if 'MANUAL_ADDITION' in sources:
        score += 15  # Manually added = vetted
    if 'GOOGLE_PLACES_API' in sources:
        score += 5   # Local discovery = less vetted

    # Domain characteristics
    if not domain.startswith('www.'):
        score += 5  # Clean domain

    # Has country/state info
    if supplier.get('country'):
        score += 5
    if supplier.get('state'):
        score += 5

    return min(score, 100)  # Cap at 100


def merge_suppliers(
    existing: List[Dict],
    new: List[Dict],
    max_total: int = 20
) -> List[Dict]:
    """
    Merge existing and new suppliers, deduplicate, and prioritize by quality.

    Args:
        existing: Existing vetted suppliers
        new: New location-based suppliers
        max_total: Maximum total suppliers to return

    Returns:
        Merged and prioritized supplier list
    """
    # Deduplicate by domain
    seen_domains = set()
    merged = []

    # Add existing suppliers first (higher priority)
    for supplier in existing:
        domain = supplier.get('domain', '').lower()
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            supplier['quality_score'] = score_supplier_quality(supplier)
            merged.append(supplier)

    # Add new suppliers
    for supplier in new:
        domain = supplier.get('domain', '').lower()
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            supplier['quality_score'] = score_supplier_quality(supplier)
            merged.append(supplier)

    # Sort by quality score (highest first)
    merged.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    # Limit to max_total
    return merged[:max_total]


def run_hybrid_pipeline(
    keywords: str,
    location: str = None,
    radius: int = 50000,
    existing_suppliers_file: str = "data/suppliers.json",
    max_local_suppliers: int = 5,
    max_total_suppliers: int = 15,
    max_pages: int = 5,
    delay: float = 1.0,
    output_dir: str = "data/results"
) -> Dict:
    """
    Run hybrid pipeline combining existing + location-based suppliers.
    """
    print("\n" + "=" * 80)
    print("HYBRID PIPELINE - EXISTING + LOCATION-BASED SUPPLIER DISCOVERY")
    print("=" * 80)

    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()

    stats = {
        'start_time': datetime.utcnow().isoformat() + 'Z',
        'keywords': keywords,
        'location': location
    }

    # =========================================================================
    # STEP 1: Load Existing Suppliers
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: LOADING EXISTING SUPPLIERS")
    print("=" * 80)

    existing_suppliers = load_existing_suppliers(existing_suppliers_file)
    stats['existing_suppliers'] = len(existing_suppliers)

    # =========================================================================
    # STEP 2: Discover Location-Based Suppliers (if location provided)
    # =========================================================================
    new_suppliers = []

    if location:
        print("\n" + "=" * 80)
        print("STEP 2: DISCOVERING LOCAL SUPPLIERS")
        print("=" * 80)

        new_suppliers = fetch_suppliers_from_location(
            keywords=keywords,
            location=location,
            radius=radius,
            max_results=max_local_suppliers
        )
        stats['new_suppliers'] = len(new_suppliers)
    else:
        print("\n⚠ No location provided, skipping local discovery")
        stats['new_suppliers'] = 0

    # =========================================================================
    # STEP 3: Merge and Prioritize Suppliers
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: MERGING & PRIORITIZING SUPPLIERS")
    print("=" * 80)

    all_suppliers = merge_suppliers(
        existing_suppliers,
        new_suppliers,
        max_total=max_total_suppliers
    )

    print(f"\nFinal supplier list ({len(all_suppliers)} total):")
    print(f"{'Rank':<6} {'Quality':<8} {'Name':<40} {'Source'}")
    print("-" * 80)
    for idx, supplier in enumerate(all_suppliers[:10], 1):
        quality = supplier.get('quality_score', 0)
        name = supplier.get('name', 'Unknown')[:38]
        source = supplier.get('sources', ['Unknown'])[0]
        print(f"{idx:<6} {quality:<8} {name:<40} {source}")

    if len(all_suppliers) > 10:
        print(f"... and {len(all_suppliers) - 10} more")

    # Save merged suppliers
    suppliers_file = os.path.join(output_dir, 'suppliers_merged.json')
    with open(suppliers_file, 'w') as f:
        json.dump(all_suppliers, f, indent=2)
    print(f"\n✓ Saved merged suppliers to: {suppliers_file}")

    stats['total_suppliers'] = len(all_suppliers)

    # =========================================================================
    # STEP 4: Expand Keywords
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: EXPANDING KEYWORDS")
    print("=" * 80)

    keyword_terms = expand_keywords(keywords)
    print(f"Expanded '{keywords}' to {len(keyword_terms)} terms")
    print(f"Sample terms: {keyword_terms[:10]}")
    stats['keyword_terms'] = len(keyword_terms)

    # =========================================================================
    # STEP 5: Crawl Suppliers & Extract Products
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 5: CRAWLING SUPPLIERS & EXTRACTING PRODUCTS")
    print("=" * 80)

    products = []
    processed_suppliers = 0

    for idx, supplier in enumerate(all_suppliers, 1):
        domain = supplier['domain']
        quality = supplier.get('quality_score', 0)

        print(f"\n[{idx}/{len(all_suppliers)}] Processing: {supplier['name']} ({domain})")
        print(f"Quality Score: {quality}/100")
        print("-" * 80)

        try:
            # Discover product URLs
            print(f"  Discovering product URLs...")
            product_urls = discover_product_urls(domain, cap=max_pages * 2)

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
                        product['supplier_id'] = supplier['supplier_id']
                        product['supplier_quality'] = quality

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
    # STEP 6: Score & Save Products
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 6: SCORING & SAVING PRODUCTS")
    print("=" * 80)

    if products:
        # Score products (with supplier quality boost)
        scored_products = score_products(products, keyword_terms)

        # Boost score based on supplier quality
        for product in scored_products:
            supplier_quality = product.get('supplier_quality', 50)
            quality_boost = (supplier_quality - 50) * 0.1  # ±5 points max
            product['score'] = product.get('score', 0) + quality_boost

        # Re-sort after quality boost
        scored_products.sort(key=lambda x: x.get('score', 0), reverse=True)

        print(f"\nTop 10 products by relevance score:")
        for i, product in enumerate(scored_products[:10], 1):
            supplier_q = product.get('supplier_quality', 0)
            print(f"  {i}. {product['name'][:60]}")
            print(f"     Score: {product.get('score', 0):.2f} | Supplier Quality: {supplier_q}/100")
            print(f"     URL: {product.get('source_url', 'N/A')[:70]}")

        # Save results
        json_path = os.path.join(output_dir, 'products.json')
        csv_path = os.path.join(output_dir, 'products.csv')

        save_products(
            scored_products,
            json_path=json_path,
            csv_path=csv_path
        )

        # Create summary
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
    print("HYBRID PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.2f}s")
    print(f"Existing suppliers: {stats['existing_suppliers']}")
    print(f"New local suppliers: {stats['new_suppliers']}")
    print(f"Total merged suppliers: {stats['total_suppliers']}")
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
        description="Hybrid pipeline: Combine existing + location-based suppliers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use existing suppliers + discover local ones
  python pipeline_hybrid.py \\
    --keywords "PETG plastic sheets" \\
    --location "37.7749,-122.4194" \\
    --existing-suppliers data/suppliers.json \\
    --max-local-suppliers 5 \\
    --max-total-suppliers 15 \\
    --max-pages 10

  # Use only existing suppliers (no location)
  python pipeline_hybrid.py \\
    --keywords "industrial gaskets" \\
    --existing-suppliers data/suppliers.json \\
    --max-total-suppliers 10 \\
    --max-pages 8
        """
    )

    parser.add_argument(
        '--keywords',
        type=str,
        required=True,
        help='Search keywords (required)'
    )

    parser.add_argument(
        '--location',
        type=str,
        help='Location as lat,lng (optional - if omitted, uses only existing suppliers)'
    )

    parser.add_argument(
        '--radius',
        type=int,
        default=50000,
        help='Search radius in meters (default: 50000)'
    )

    parser.add_argument(
        '--existing-suppliers',
        type=str,
        default='data/suppliers.json',
        help='Path to existing suppliers JSON (default: data/suppliers.json)'
    )

    parser.add_argument(
        '--max-local-suppliers',
        type=int,
        default=5,
        help='Max new local suppliers to discover (default: 5)'
    )

    parser.add_argument(
        '--max-total-suppliers',
        type=int,
        default=15,
        help='Max total suppliers to process (default: 15)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=5,
        help='Max pages per supplier (default: 5)'
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
        default='data/results_hybrid',
        help='Output directory (default: data/results_hybrid)'
    )

    args = parser.parse_args()

    try:
        result = run_hybrid_pipeline(
            keywords=args.keywords,
            location=args.location,
            radius=args.radius,
            existing_suppliers_file=args.existing_suppliers,
            max_local_suppliers=args.max_local_suppliers,
            max_total_suppliers=args.max_total_suppliers,
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
