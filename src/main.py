#!/usr/bin/env python3
"""
Main CLI orchestrator for the contexgt procurement discovery pipeline.
"""

import argparse
import sys
import time
from typing import List, Optional

try:
    from .discovery_seed import stub_suppliers, load_suppliers_from_csv, save_suppliers, load_suppliers
    from .keywords import expand_keywords
    from .sitemap import discover_product_urls
    from .product_extract import extract_product
    from .specs_normalize import normalize_specifications
    from .scorer import score_products
    from .store import save_products, create_summary_report
except ImportError:
    # Handle running as script
    from discovery_seed import stub_suppliers, load_suppliers_from_csv, save_suppliers, load_suppliers
    from keywords import expand_keywords
    from sitemap import discover_product_urls
    from product_extract import extract_product
    from specs_normalize import normalize_specifications
    from scorer import score_products
    from store import save_products, create_summary_report


def cmd_seed(args) -> None:
    """
    Seed command: Load suppliers from CSV or create stubs.
    """
    print("=" * 60)
    print("SEEDING SUPPLIERS")
    print("=" * 60)

    if args.csv:
        print(f"Loading suppliers from CSV: {args.csv}")
        suppliers = load_suppliers_from_csv(
            args.csv,
            name_col=args.name_col,
            website_col=args.website_col,
            country_col=args.country_col,
            state_col=args.state_col
        )
    else:
        print("Creating stub suppliers")
        suppliers = stub_suppliers()

    # Save suppliers
    save_suppliers(suppliers, args.out)

    print(f"\nSeed complete! Generated {len(suppliers)} suppliers.")
    print(f"Saved to: {args.out}")


def cmd_crawl(args) -> None:
    """
    Crawl command: Discover and extract products from suppliers.
    """
    print("=" * 60)
    print("CRAWLING FOR PRODUCTS")
    print("=" * 60)

    if not args.keyword:
        print("Error: --keyword is required for crawling")
        sys.exit(1)

    print(f"Keyword: {args.keyword}")
    print(f"Max domains: {args.max_domains}")
    print(f"Max pages per domain: {args.max_pages}")
    print(f"Delay between requests: {args.delay}s")

    # Load suppliers
    print(f"\nLoading suppliers from: {args.suppliers}")
    suppliers = load_suppliers(args.suppliers)
    print(f"Loaded {len(suppliers)} suppliers")

    # Expand keywords
    print(f"\nExpanding keywords...")
    keyword_terms = expand_keywords(args.keyword)
    print(f"Expanded to {len(keyword_terms)} terms: {keyword_terms[:10]}...")

    # Process suppliers (limit to max_domains)
    products = []
    processed_domains = 0

    print(f"\nStarting crawl...")

    for supplier in suppliers:
        if processed_domains >= args.max_domains:
            print(f"Reached maximum domains limit ({args.max_domains})")
            break

        domain = supplier['domain']
        print(f"\n--- Processing {supplier['name']} ({domain}) ---")

        try:
            # Discover product URLs from sitemap
            product_urls = discover_product_urls(domain, cap=args.max_pages)

            if not product_urls:
                print(f"No product URLs found for {domain}")
                continue

            print(f"Found {len(product_urls)} potential product URLs")

            # Extract products from URLs
            domain_products = []

            for url_data in product_urls[:args.max_pages]:  # Respect page limit
                url = url_data['url']

                try:
                    product = extract_product(url, keyword_terms)

                    if product:
                        # Set supplier ID
                        product['supplier_id'] = supplier['supplier_id']

                        # Normalize specifications
                        specs_canonical = normalize_specifications(product.get('specs_raw', {}))
                        product['specs_canonical'] = specs_canonical

                        domain_products.append(product)

                        print(f"  ✓ Extracted: {product['name']}")
                    else:
                        print(f"  ✗ No product extracted from: {url}")

                except Exception as e:
                    print(f"  ✗ Error extracting from {url}: {e}")

                # Politeness delay
                if args.delay > 0:
                    time.sleep(args.delay)

            products.extend(domain_products)
            print(f"Extracted {len(domain_products)} products from {domain}")

        except Exception as e:
            print(f"Error processing {domain}: {e}")

        processed_domains += 1

        # Brief delay between domains
        if args.delay > 0:
            time.sleep(args.delay * 2)

    print(f"\n--- CRAWL COMPLETE ---")
    print(f"Total products extracted: {len(products)}")

    if products:
        # Score products
        print(f"\nScoring products...")
        scored_products = score_products(products, keyword_terms)

        print(f"Top 5 products by score:")
        for i, product in enumerate(scored_products[:5]):
            print(f"  {i+1}. {product['name']} (Score: {product['score']})")

        # Save results
        print(f"\nSaving results...")
        save_products(
            scored_products,
            json_path=args.out_json,
            csv_path=args.out_csv
        )

        # Create summary report
        if args.out_json:
            summary_path = args.out_json.replace('.json', '_summary.json')
            create_summary_report(scored_products, summary_path)

        print(f"\nResults saved!")
        if args.out_json:
            print(f"  JSON: {args.out_json}")
        if args.out_csv:
            print(f"  CSV: {args.out_csv}")

    else:
        print("\nNo products were extracted.")


def cmd_run(args) -> None:
    """
    Run command: Seed + Crawl in one go.
    """
    print("=" * 60)
    print("RUNNING FULL PIPELINE")
    print("=" * 60)

    # Create suppliers file path
    suppliers_file = "data/suppliers.json"

    # Check if suppliers file already exists
    try:
        suppliers = load_suppliers(suppliers_file)
        print(f"Step 1: Using existing suppliers from {suppliers_file}")
        print(f"Loaded {len(suppliers)} existing suppliers")
    except (FileNotFoundError, Exception):
        # Only seed suppliers if file doesn't exist or is invalid
        print("Step 1: Seeding suppliers...")
        if args.csv:
            suppliers = load_suppliers_from_csv(
                args.csv,
                name_col=args.name_col,
                website_col=args.website_col,
                country_col=args.country_col,
                state_col=args.state_col
            )
        else:
            suppliers = stub_suppliers()

        save_suppliers(suppliers, suppliers_file)
        print(f"Seeded {len(suppliers)} suppliers")

    # Then crawl
    print("\nStep 2: Crawling for products...")

    # Set suppliers file for crawl
    args.suppliers = suppliers_file

    # Run crawl
    cmd_crawl(args)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser.
    """
    parser = argparse.ArgumentParser(
        description="contexgt - Code-First MVP Pipeline for Procurement Discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seed with stub suppliers
  python -m src.main seed --out data/suppliers.json

  # Seed from CSV
  python -m src.main seed --csv suppliers.csv --out data/suppliers.json

  # Crawl for products
  python -m src.main crawl --suppliers data/suppliers.json \\
    --keyword "PETG sheet 2mm ISO 9001" \\
    --max-domains 10 --max-pages 5 \\
    --out-json data/products.json --out-csv data/products.csv

  # Run end-to-end
  python -m src.main run --keyword "die-cut gaskets ISO 9001" \\
    --max-domains 20 --max-pages 10 \\
    --products-json data/products.json --products-csv data/products.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Seed command
    seed_parser = subparsers.add_parser('seed', help='Load suppliers from CSV or create stubs')
    seed_parser.add_argument('--csv', help='Path to suppliers CSV file')
    seed_parser.add_argument('--out', default='data/suppliers.json',
                           help='Output JSON file for suppliers (default: data/suppliers.json)')
    seed_parser.add_argument('--name-col', default='name',
                           help='CSV column name for supplier name (default: name)')
    seed_parser.add_argument('--website-col', default='website',
                           help='CSV column name for website (default: website)')
    seed_parser.add_argument('--country-col', default='country',
                           help='CSV column name for country (default: country)')
    seed_parser.add_argument('--state-col', default='state',
                           help='CSV column name for state (default: state)')

    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Crawl suppliers for products')
    crawl_parser.add_argument('--suppliers', default='data/suppliers.json',
                            help='Path to suppliers JSON file (default: data/suppliers.json)')
    crawl_parser.add_argument('--keyword', required=True,
                            help='Search keyword (required)')
    crawl_parser.add_argument('--max-domains', type=int, default=10,
                            help='Maximum number of domains to process (default: 10)')
    crawl_parser.add_argument('--max-pages', type=int, default=5,
                            help='Maximum pages per domain (default: 5)')
    crawl_parser.add_argument('--delay', type=float, default=1.0,
                            help='Delay between requests in seconds (default: 1.0)')
    crawl_parser.add_argument('--out-json', default='data/products.json',
                            help='Output JSON file for products (default: data/products.json)')
    crawl_parser.add_argument('--out-csv', default='data/products.csv',
                            help='Output CSV file for products (default: data/products.csv)')

    # Run command (seed + crawl)
    run_parser = subparsers.add_parser('run', help='Run full pipeline (seed + crawl)')
    run_parser.add_argument('--csv', help='Path to suppliers CSV file (optional)')
    run_parser.add_argument('--keyword', required=True,
                          help='Search keyword (required)')
    run_parser.add_argument('--max-domains', type=int, default=10,
                          help='Maximum number of domains to process (default: 10)')
    run_parser.add_argument('--max-pages', type=int, default=5,
                          help='Maximum pages per domain (default: 5)')
    run_parser.add_argument('--delay', type=float, default=1.0,
                          help='Delay between requests in seconds (default: 1.0)')
    run_parser.add_argument('--products-json', default='data/products.json',
                          help='Output JSON file for products (default: data/products.json)')
    run_parser.add_argument('--products-csv', default='data/products.csv',
                          help='Output CSV file for products (default: data/products.csv)')

    # CSV column mapping for run command
    run_parser.add_argument('--name-col', default='name',
                          help='CSV column name for supplier name (default: name)')
    run_parser.add_argument('--website-col', default='website',
                          help='CSV column name for website (default: website)')
    run_parser.add_argument('--country-col', default='country',
                          help='CSV column name for country (default: country)')
    run_parser.add_argument('--state-col', default='state',
                          help='CSV column name for state (default: state)')

    return parser


def main() -> None:
    """
    Main entry point.
    """
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'seed':
            cmd_seed(args)
        elif args.command == 'crawl':
            # Set defaults for crawl outputs if not specified
            if not args.out_json and not args.out_csv:
                args.out_json = 'data/products.json'
                args.out_csv = 'data/products.csv'
            cmd_crawl(args)
        elif args.command == 'run':
            # Set crawl outputs for run command
            args.out_json = args.products_json
            args.out_csv = args.products_csv
            cmd_run(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()