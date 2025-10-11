#!/usr/bin/env python3
"""
Fully validated pipeline with supplier website checking.

This pipeline:
1. Discovers suppliers (existing + location-based)
2. VALIDATES each supplier's website for scrapability
3. Only attempts extraction on validated suppliers
4. Uses improved extraction logic

This reduces wasted time on suppliers without product data.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from fetch_suppliers_smart import fetch_suppliers_from_location
from validate_supplier_website import validate_suppliers_batch
from sitemap_improved import discover_product_urls_improved
from product_extract_improved import extract_product_improved
from keywords import expand_keywords
from specs_normalize import normalize_specifications
from scorer import score_products
from store import save_products, create_summary_report


def load_existing_suppliers(suppliers_file: str) -> List[Dict]:
    """Load existing suppliers from JSON file."""
    try:
        with open(suppliers_file, 'r') as f:
            suppliers = json.load(f)
        print(f"✓ Loaded {len(suppliers)} existing suppliers")
        return suppliers
    except FileNotFoundError:
        print(f"⚠ No existing suppliers file found")
        return []


def score_supplier_quality(supplier: Dict) -> int:
    """Score supplier quality (0-100)."""
    score = 50
    domain = supplier.get('domain', '').lower()

    known_quality = [
        'mcmaster.com', 'grainger.com', 'usplastic.com',
        'professionalplastics.com', 'fastenal.com', 'mscdirect.com'
    ]

    if any(kq in domain for kq in known_quality):
        score += 30

    # Add validation score bonus
    validation_score = supplier.get('validation_score', 0)
    score += min(validation_score, 20)  # Up to +20 for validation

    sources = supplier.get('sources', [])
    if 'PUBLIC' in sources:
        score += 10
    if 'MANUAL_ADDITION' in sources:
        score += 15
    if 'GOOGLE_PLACES_API' in sources:
        score += 5

    return min(score, 100)


def merge_suppliers(existing: List[Dict], new: List[Dict], max_total: int = 20) -> List[Dict]:
    """Merge suppliers (local first if available)."""
    seen_domains = set()
    merged = []

    # Add new local suppliers first
    for supplier in new:
        domain = supplier.get('domain', '').lower()
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            merged.append(supplier)

    # Add existing suppliers
    for supplier in existing:
        domain = supplier.get('domain', '').lower()
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            merged.append(supplier)

    return merged[:max_total]


def run_validated_pipeline(
    keywords: str,
    location: str = None,
    radius: int = 50000,
    existing_suppliers_file: str = "data/suppliers.json",
    max_local_suppliers: int = 10,
    max_total_suppliers: int = 20,
    min_validation_score: int = 4,
    max_pages: int = 10,
    min_product_quality: int = 3,
    delay: float = 1.0,
    output_dir: str = "data/results_validated"
) -> Dict:
    """Run fully validated pipeline."""

    print("\n" + "=" * 80)
    print("VALIDATED PIPELINE - WITH SUPPLIER WEBSITE VERIFICATION")
    print("=" * 80)

    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()

    stats = {
        'start_time': datetime.utcnow().isoformat() + 'Z',
        'keywords': keywords,
        'location': location
    }

    # Step 1: Load & Discover
    print("\n" + "=" * 80)
    print("STEP 1: LOADING & DISCOVERING SUPPLIERS")
    print("=" * 80)

    existing_suppliers = load_existing_suppliers(existing_suppliers_file)
    stats['existing_suppliers'] = len(existing_suppliers)

    new_suppliers = []
    if location:
        print(f"\nDiscovering local suppliers near {location}...")
        new_suppliers = fetch_suppliers_from_location(
            keywords=keywords,
            location=location,
            radius=radius,
            max_results=max_local_suppliers
        )
        stats['new_suppliers'] = len(new_suppliers)
    else:
        print("⚠ No location provided")
        stats['new_suppliers'] = 0

    # Merge
    all_suppliers = merge_suppliers(existing_suppliers, new_suppliers, max_total=max_total_suppliers)
    print(f"\nMerged: {len(all_suppliers)} total suppliers (local prioritized)")
    stats['total_suppliers'] = len(all_suppliers)

    # Step 2: VALIDATE websites
    print("\n" + "=" * 80)
    print("STEP 2: VALIDATING SUPPLIER WEBSITES")
    print("=" * 80)
    print(f"Checking which suppliers have scrapable product data...")
    print(f"Minimum validation score: {min_validation_score}/13")

    validated_suppliers = validate_suppliers_batch(all_suppliers, min_score=min_validation_score)

    stats['suppliers_validated'] = len(all_suppliers)
    stats['suppliers_passed'] = len(validated_suppliers)
    stats['validation_pass_rate'] = f"{len(validated_suppliers)/len(all_suppliers)*100:.1f}%" if all_suppliers else "0%"

    if not validated_suppliers:
        print("\n✗ No suppliers passed validation")
        return {'success': False, 'stats': stats}

    # Sort by quality score
    for supplier in validated_suppliers:
        supplier['quality_score'] = score_supplier_quality(supplier)

    validated_suppliers.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    # Save validated suppliers
    suppliers_file = os.path.join(output_dir, 'suppliers_validated.json')
    with open(suppliers_file, 'w') as f:
        json.dump(validated_suppliers, f, indent=2)
    print(f"\n✓ Saved validated suppliers to: {suppliers_file}")

    # Step 3: Expand keywords
    print("\n" + "=" * 80)
    print("STEP 3: EXPANDING KEYWORDS")
    print("=" * 80)

    keyword_terms = expand_keywords(keywords)
    print(f"Expanded '{keywords}' to {len(keyword_terms)} terms")
    stats['keyword_terms'] = len(keyword_terms)

    # Step 4: Crawl ONLY validated suppliers
    print("\n" + "=" * 80)
    print("STEP 4: CRAWLING VALIDATED SUPPLIERS")
    print("=" * 80)
    print(f"Crawling {len(validated_suppliers)} validated suppliers")

    products = []
    urls_attempted = 0
    urls_extracted = 0

    for idx, supplier in enumerate(validated_suppliers, 1):
        domain = supplier['domain']
        quality = supplier.get('quality_score', 0)
        validation = supplier.get('validation_score', 0)

        print(f"\n[{idx}/{len(validated_suppliers)}] {supplier['name']} ({domain})")
        print(f"Quality: {quality}/100 | Validation: {validation}/13")
        print("-" * 80)

        try:
            product_urls = discover_product_urls_improved(domain, cap=max_pages * 2)

            if not product_urls:
                print(f"  ✗ No product URLs found")
                continue

            print(f"  ✓ Found {len(product_urls)} product URLs")

            for url_idx, url_data in enumerate(product_urls[:max_pages], 1):
                url = url_data['url']
                urls_attempted += 1

                print(f"  [{url_idx}/{min(max_pages, len(product_urls))}] {url}")

                try:
                    product = extract_product_improved(url, keyword_terms, min_quality=min_product_quality)

                    if product:
                        product['supplier_id'] = supplier['supplier_id']
                        product['supplier_quality'] = quality
                        product['specs_canonical'] = normalize_specifications(product.get('specs_raw', {}))
                        products.append(product)
                        urls_extracted += 1
                        print(f"    ✓ {product['name'][:60]}")

                except Exception as e:
                    print(f"    ✗ Error: {e}")

                if delay > 0:
                    time.sleep(delay)

            print(f"  Extracted: {len([p for p in products if p['supplier_id'] == supplier['supplier_id']])} products")

        except Exception as e:
            print(f"  ✗ Error: {e}")

        if delay > 0:
            time.sleep(delay * 2)

    stats['urls_attempted'] = urls_attempted
    stats['urls_extracted'] = urls_extracted
    stats['extraction_rate'] = f"{(urls_extracted/urls_attempted*100):.1f}%" if urls_attempted > 0 else "0%"
    stats['products_extracted'] = len(products)

    # Step 5: Score & Save
    print("\n" + "=" * 80)
    print("STEP 5: SCORING & SAVING")
    print("=" * 80)

    if products:
        scored_products = score_products(products, keyword_terms)

        for product in scored_products:
            quality_boost = (product.get('supplier_quality', 50) - 50) * 0.1
            product['score'] = product.get('score', 0) + quality_boost

        scored_products.sort(key=lambda x: x.get('score', 0), reverse=True)

        print(f"\nTop 10 products:")
        for i, product in enumerate(scored_products[:10], 1):
            print(f"  {i}. {product['name'][:65]}")
            print(f"     Score: {product.get('score', 0):.1f} | Price: {product.get('price_text', 'N/A')}")

        json_path = os.path.join(output_dir, 'products.json')
        csv_path = os.path.join(output_dir, 'products.csv')
        save_products(scored_products, json_path=json_path, csv_path=csv_path)

        summary_path = os.path.join(output_dir, 'summary.json')
        create_summary_report(scored_products, summary_path)

        stats['products_saved'] = len(scored_products)

        print(f"\n✓ Saved to:")
        print(f"  • {json_path}")
        print(f"  • {csv_path}")
        print(f"  • {summary_path}")
    else:
        print("\n✗ No products extracted")
        stats['products_saved'] = 0

    # Final stats
    duration = time.time() - start_time
    stats['duration_seconds'] = round(duration, 2)
    stats['end_time'] = datetime.utcnow().isoformat() + 'Z'

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f}s")
    print(f"Suppliers discovered: {stats['total_suppliers']}")
    print(f"Suppliers validated: {stats['suppliers_passed']}/{stats['suppliers_validated']} ({stats['validation_pass_rate']})")
    print(f"URLs attempted: {stats['urls_attempted']}")
    print(f"URLs extracted: {stats['urls_extracted']} ({stats['extraction_rate']})")
    print(f"Products saved: {stats['products_saved']}")

    stats_path = os.path.join(output_dir, 'pipeline_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    return {'success': True, 'stats': stats}


def main():
    parser = argparse.ArgumentParser(description="Validated pipeline with website checking")
    parser.add_argument('--keywords', type=str, required=True)
    parser.add_argument('--location', type=str, help='Lat,lng coordinates')
    parser.add_argument('--radius', type=int, default=50000)
    parser.add_argument('--existing-suppliers', type=str, default='data/suppliers.json')
    parser.add_argument('--max-local-suppliers', type=int, default=10)
    parser.add_argument('--max-total-suppliers', type=int, default=20)
    parser.add_argument('--min-validation-score', type=int, default=4, help='Min website validation score (0-13)')
    parser.add_argument('--max-pages', type=int, default=10)
    parser.add_argument('--min-product-quality', type=int, default=3)
    parser.add_argument('--delay', type=float, default=1.0)
    parser.add_argument('--output-dir', type=str, default='data/results_validated')

    args = parser.parse_args()

    try:
        result = run_validated_pipeline(
            keywords=args.keywords,
            location=args.location,
            radius=args.radius,
            existing_suppliers_file=args.existing_suppliers,
            max_local_suppliers=args.max_local_suppliers,
            max_total_suppliers=args.max_total_suppliers,
            min_validation_score=args.min_validation_score,
            max_pages=args.max_pages,
            min_product_quality=args.min_product_quality,
            delay=args.delay,
            output_dir=args.output_dir
        )

        sys.exit(0 if result.get('success') else 1)

    except KeyboardInterrupt:
        print("\n\n✗ Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
