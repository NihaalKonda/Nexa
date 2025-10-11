#!/usr/bin/env python3
"""
Improved Hybrid Pipeline with better product extraction.

Key improvements over pipeline_hybrid.py:
1. Uses sitemap_improved.py for better URL filtering
2. Uses product_extract_improved.py for quality validation
3. Filters out utility/category pages aggressively
4. Only extracts real product detail pages

Usage:
  python pipeline_hybrid_improved.py \\
    --keywords "PETG plastic sheets" \\
    --location "37.7749,-122.4194" \\
    --existing-suppliers data/suppliers.json \\
    --max-local-suppliers 5 \\
    --max-total-suppliers 10 \\
    --max-pages 10
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

# Import improved modules
try:
    from sitemap_improved import discover_product_urls_improved
    from product_extract_improved import extract_product_improved, is_valid_product
    from keywords import expand_keywords
    from specs_normalize import normalize_specifications
    from scorer import score_products
    from store import save_products, create_summary_report
except ImportError as e:
    print(f"Error: Could not import modules: {e}")
    sys.exit(1)

# Import fetch_suppliers_smart and merge logic from pipeline_hybrid
from fetch_suppliers_smart import fetch_suppliers_from_location


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
    """Score supplier quality (0-100)."""
    score = 50

    domain = supplier.get('domain', '').lower()

    known_quality = [
        'mcmaster.com', 'grainger.com', 'usplastic.com',
        'professionalplastics.com', 'fastenal.com', 'mscdirect.com',
        'digikey.com', 'mouser.com', 'arrow.com', 'avnet.com'
    ]

    if any(kq in domain for kq in known_quality):
        score += 30

    sources = supplier.get('sources', [])
    if 'PUBLIC' in sources:
        score += 10
    if 'MANUAL_ADDITION' in sources:
        score += 15
    if 'GOOGLE_PLACES_API' in sources:
        score += 5

    if supplier.get('country'):
        score += 5
    if supplier.get('state'):
        score += 5

    return min(score, 100)


def merge_suppliers(existing: List[Dict], new: List[Dict], max_total: int = 20, prioritize_local: bool = True) -> List[Dict]:
    """
    Merge and deduplicate suppliers.

    Args:
        existing: Existing vetted suppliers
        new: New location-based suppliers
        max_total: Maximum total suppliers
        prioritize_local: If True, prioritize newly discovered local suppliers first
    """
    seen_domains = set()
    merged = []

    # If prioritizing local suppliers, add them first
    if prioritize_local and new:
        print(f"\n💡 Prioritizing {len(new)} newly discovered local suppliers")
        for supplier in new:
            domain = supplier.get('domain', '').lower()
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                supplier['quality_score'] = score_supplier_quality(supplier)
                supplier['is_local'] = True  # Mark as local
                merged.append(supplier)

    # Then add existing suppliers
    for supplier in existing:
        domain = supplier.get('domain', '').lower()
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            supplier['quality_score'] = score_supplier_quality(supplier)
            supplier['is_local'] = False
            merged.append(supplier)

    # If not prioritizing local, add new suppliers after existing
    if not prioritize_local:
        for supplier in new:
            domain = supplier.get('domain', '').lower()
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                supplier['quality_score'] = score_supplier_quality(supplier)
                supplier['is_local'] = True
                merged.append(supplier)

    # Sort by quality score (but local already at top if prioritized)
    if not prioritize_local:
        merged.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    return merged[:max_total]


def run_improved_pipeline(
    keywords: str,
    location: str = None,
    radius: int = 50000,
    existing_suppliers_file: str = "data/suppliers.json",
    max_local_suppliers: int = 5,
    max_total_suppliers: int = 15,
    max_pages: int = 10,
    min_product_quality: int = 3,
    delay: float = 1.0,
    output_dir: str = "data/results_improved"
) -> Dict:
    """Run improved pipeline with better extraction."""

    print("\n" + "=" * 80)
    print("IMPROVED HYBRID PIPELINE - BETTER PRODUCT EXTRACTION")
    print("=" * 80)

    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()

    stats = {
        'start_time': datetime.utcnow().isoformat() + 'Z',
        'keywords': keywords,
        'location': location
    }

    # Step 1: Load existing suppliers
    print("\n" + "=" * 80)
    print("STEP 1: LOADING EXISTING SUPPLIERS")
    print("=" * 80)

    existing_suppliers = load_existing_suppliers(existing_suppliers_file)
    stats['existing_suppliers'] = len(existing_suppliers)

    # Step 2: Discover local suppliers
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
        print("\n⚠ No location provided, using only existing suppliers")
        stats['new_suppliers'] = 0

    # Step 3: Merge suppliers
    print("\n" + "=" * 80)
    print("STEP 3: MERGING & PRIORITIZING SUPPLIERS")
    print("=" * 80)

    # Prioritize local suppliers if location was provided
    prioritize_local = location is not None and len(new_suppliers) > 0
    all_suppliers = merge_suppliers(existing_suppliers, new_suppliers, max_total=max_total_suppliers, prioritize_local=prioritize_local)

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

    suppliers_file = os.path.join(output_dir, 'suppliers_merged.json')
    with open(suppliers_file, 'w') as f:
        json.dump(all_suppliers, f, indent=2)
    print(f"\n✓ Saved merged suppliers to: {suppliers_file}")

    stats['total_suppliers'] = len(all_suppliers)

    # Step 4: Expand keywords
    print("\n" + "=" * 80)
    print("STEP 4: EXPANDING KEYWORDS")
    print("=" * 80)

    keyword_terms = expand_keywords(keywords)
    print(f"Expanded '{keywords}' to {len(keyword_terms)} terms")
    print(f"Sample terms: {keyword_terms[:10]}")
    stats['keyword_terms'] = len(keyword_terms)

    # Step 5: Crawl with IMPROVED extraction
    print("\n" + "=" * 80)
    print("STEP 5: CRAWLING WITH IMPROVED EXTRACTION")
    print("=" * 80)
    print(f"Using improved URL filtering and product validation (min quality: {min_product_quality}/10)")

    products = []
    processed_suppliers = 0
    urls_attempted = 0
    urls_extracted = 0

    for idx, supplier in enumerate(all_suppliers, 1):
        domain = supplier['domain']
        quality = supplier.get('quality_score', 0)

        print(f"\n[{idx}/{len(all_suppliers)}] Processing: {supplier['name']} ({domain})")
        print(f"Quality Score: {quality}/100")
        print("-" * 80)

        try:
            # Use IMPROVED sitemap discovery
            print(f"  Discovering product URLs with improved filtering...")
            product_urls = discover_product_urls_improved(domain, cap=max_pages * 2)

            if not product_urls:
                print(f"  ✗ No product URLs found")
                continue

            print(f"  ✓ Found {len(product_urls)} product URLs")

            # Extract products with IMPROVED validation
            supplier_products = []

            for url_idx, url_data in enumerate(product_urls[:max_pages], 1):
                url = url_data['url']
                urls_attempted += 1

                print(f"  [{url_idx}/{min(max_pages, len(product_urls))}] Extracting: {url}")

                try:
                    # Use IMPROVED extraction with validation
                    product = extract_product_improved(url, keyword_terms, min_quality=min_product_quality)

                    if product:
                        product['supplier_id'] = supplier['supplier_id']
                        product['supplier_quality'] = quality

                        # Normalize specifications
                        specs_canonical = normalize_specifications(product.get('specs_raw', {}))
                        product['specs_canonical'] = specs_canonical

                        supplier_products.append(product)
                        urls_extracted += 1
                        print(f"    ✓ Product {len(supplier_products)}: {product['name']}")

                except Exception as e:
                    print(f"    ✗ Error: {e}")

                # Politeness delay
                if delay > 0:
                    time.sleep(delay)

            products.extend(supplier_products)
            print(f"\n  Summary: Extracted {len(supplier_products)} valid products from {domain}")

        except Exception as e:
            print(f"  ✗ Error processing {domain}: {e}")

        processed_suppliers += 1

        if delay > 0:
            time.sleep(delay * 2)

    stats['suppliers_processed'] = processed_suppliers
    stats['urls_attempted'] = urls_attempted
    stats['urls_extracted'] = urls_extracted
    stats['products_extracted'] = len(products)
    stats['extraction_success_rate'] = f"{(urls_extracted/urls_attempted*100):.1f}%" if urls_attempted > 0 else "0%"

    # Step 6: Score & Save
    print("\n" + "=" * 80)
    print("STEP 6: SCORING & SAVING PRODUCTS")
    print("=" * 80)

    if products:
        scored_products = score_products(products, keyword_terms)

        # Boost by supplier quality
        for product in scored_products:
            supplier_quality = product.get('supplier_quality', 50)
            quality_boost = (supplier_quality - 50) * 0.1
            product['score'] = product.get('score', 0) + quality_boost

        scored_products.sort(key=lambda x: x.get('score', 0), reverse=True)

        print(f"\nTop 10 products by relevance score:")
        for i, product in enumerate(scored_products[:10], 1):
            supplier_q = product.get('supplier_quality', 0)
            print(f"  {i}. {product['name'][:70]}")
            print(f"     Score: {product.get('score', 0):.2f} | Supplier Quality: {supplier_q}/100")
            if product.get('price_text'):
                print(f"     Price: {product['price_text']}")

        json_path = os.path.join(output_dir, 'products.json')
        csv_path = os.path.join(output_dir, 'products.csv')

        save_products(scored_products, json_path=json_path, csv_path=csv_path)

        summary_path = os.path.join(output_dir, 'summary.json')
        create_summary_report(scored_products, summary_path)

        stats['products_saved'] = len(scored_products)

        print(f"\n✓ Results saved:")
        print(f"  • JSON: {json_path}")
        print(f"  • CSV: {csv_path}")
        print(f"  • Summary: {summary_path}")

    else:
        print("\n✗ No valid products extracted")
        stats['products_saved'] = 0

    # Final stats
    end_time = time.time()
    duration = end_time - start_time

    stats['end_time'] = datetime.utcnow().isoformat() + 'Z'
    stats['duration_seconds'] = round(duration, 2)

    print("\n" + "=" * 80)
    print("IMPROVED PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.2f}s")
    print(f"Existing suppliers: {stats['existing_suppliers']}")
    print(f"New local suppliers: {stats['new_suppliers']}")
    print(f"Total merged suppliers: {stats['total_suppliers']}")
    print(f"Suppliers processed: {stats['suppliers_processed']}")
    print(f"URLs attempted: {stats['urls_attempted']}")
    print(f"URLs successfully extracted: {stats['urls_extracted']}")
    print(f"Extraction success rate: {stats['extraction_success_rate']}")
    print(f"Valid products extracted: {stats['products_extracted']}")
    print(f"Products saved: {stats['products_saved']}")

    stats_path = os.path.join(output_dir, 'pipeline_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nPipeline stats saved to: {stats_path}")

    return {'success': True, 'stats': stats}


def main():
    parser = argparse.ArgumentParser(
        description="Improved hybrid pipeline with better product extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--keywords', type=str, required=True, help='Search keywords')
    parser.add_argument('--location', type=str, help='Location as lat,lng (optional)')
    parser.add_argument('--radius', type=int, default=50000, help='Search radius in meters')
    parser.add_argument('--existing-suppliers', type=str, default='data/suppliers.json')
    parser.add_argument('--max-local-suppliers', type=int, default=5)
    parser.add_argument('--max-total-suppliers', type=int, default=15)
    parser.add_argument('--max-pages', type=int, default=10)
    parser.add_argument('--min-product-quality', type=int, default=3, help='Min quality score (0-10)')
    parser.add_argument('--delay', type=float, default=1.0)
    parser.add_argument('--output-dir', type=str, default='data/results_improved')

    args = parser.parse_args()

    try:
        result = run_improved_pipeline(
            keywords=args.keywords,
            location=args.location,
            radius=args.radius,
            existing_suppliers_file=args.existing_suppliers,
            max_local_suppliers=args.max_local_suppliers,
            max_total_suppliers=args.max_total_suppliers,
            max_pages=args.max_pages,
            min_product_quality=args.min_product_quality,
            delay=args.delay,
            output_dir=args.output_dir
        )

        sys.exit(0 if result.get('success') else 1)

    except KeyboardInterrupt:
        print("\n\n✗ Pipeline cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
