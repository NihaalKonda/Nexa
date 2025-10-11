#!/usr/bin/env python3
"""
Validate supplier websites to check if they have scrapable product data.
Use this to filter out suppliers without e-commerce before attempting extraction.
"""

import requests
import time
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def check_sitemap_exists(domain: str) -> bool:
    """Check if domain has an accessible sitemap."""
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'

    sitemap_urls = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/product-sitemap.xml',
        '/products-sitemap.xml'
    ]

    for sitemap_path in sitemap_urls:
        try:
            url = urljoin(domain, sitemap_path)
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return True
        except:
            pass

    return False


def check_robots_txt(domain: str) -> Dict:
    """
    Check robots.txt for sitemap references and crawl permissions.

    Returns:
        Dict with sitemap URLs and whether /sitemap.xml is allowed
    """
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'

    try:
        url = urljoin(domain, '/robots.txt')
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            content = response.text

            # Find sitemap references
            sitemaps = []
            for line in content.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemaps.append(sitemap_url)

            # Check if sitemaps are disallowed
            sitemap_allowed = 'disallow: /sitemap' not in content.lower()

            return {
                'exists': True,
                'sitemaps': sitemaps,
                'sitemap_allowed': sitemap_allowed
            }
    except:
        pass

    return {
        'exists': False,
        'sitemaps': [],
        'sitemap_allowed': True  # Assume allowed if no robots.txt
    }


def check_for_ecommerce_signals(domain: str) -> Dict:
    """
    Check homepage for e-commerce signals.

    Returns:
        Dict with various e-commerce indicators
    """
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'

    signals = {
        'has_cart': False,
        'has_checkout': False,
        'has_product_links': False,
        'has_search': False,
        'has_catalog': False,
        'accessible': False
    }

    try:
        response = requests.get(domain, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; SupplierValidator/1.0)'
        })

        if response.status_code == 200:
            signals['accessible'] = True
            soup = BeautifulSoup(response.content, 'html.parser')
            html_text = soup.get_text().lower()
            html_lower = response.text.lower()

            # Check for cart/checkout
            signals['has_cart'] = any(term in html_lower for term in [
                'add to cart', 'shopping cart', 'cart-', 'cart_', '/cart',
                'basket', 'add-to-bag'
            ])

            signals['has_checkout'] = any(term in html_lower for term in [
                'checkout', 'check-out', 'check out', 'proceed to checkout'
            ])

            # Check for product-related links
            product_patterns = [
                '/product', '/item', '/catalog', '/shop', '/store',
                '/parts', '/products'
            ]

            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href'].lower()
                if any(pattern in href for pattern in product_patterns):
                    signals['has_product_links'] = True
                    break

            # Check for search functionality
            signals['has_search'] = bool(soup.find(['input', 'form'], {'type': 'search'})) or \
                                   'search' in html_lower and ('input' in html_lower or 'form' in html_lower)

            # Check for catalog/browse functionality
            signals['has_catalog'] = any(term in html_lower for term in [
                'browse catalog', 'product catalog', 'view products',
                'shop now', 'browse products', 'our products'
            ])

    except Exception as e:
        print(f"Error checking {domain}: {e}")

    return signals


def validate_supplier(supplier: Dict, verbose: bool = True) -> Dict:
    """
    Validate a supplier's website for scrapability.

    Args:
        supplier: Supplier dict with 'domain' key
        verbose: Print validation details

    Returns:
        Dict with validation results and score
    """
    domain = supplier.get('domain', '')
    name = supplier.get('name', 'Unknown')

    if verbose:
        print(f"\nValidating: {name} ({domain})")
        print("-" * 60)

    results = {
        'supplier_id': supplier.get('supplier_id'),
        'name': name,
        'domain': domain,
        'validation_score': 0,
        'is_scrapable': False,
        'checks': {}
    }

    # Check 1: Sitemap exists
    has_sitemap = check_sitemap_exists(domain)
    results['checks']['sitemap_exists'] = has_sitemap
    if has_sitemap:
        results['validation_score'] += 3
        if verbose:
            print("  ✓ Sitemap found")
    else:
        if verbose:
            print("  ✗ No sitemap found")

    time.sleep(0.2)  # Politeness

    # Check 2: Robots.txt analysis
    robots_info = check_robots_txt(domain)
    results['checks']['robots_txt'] = robots_info

    if robots_info['exists']:
        if verbose:
            print(f"  ✓ robots.txt exists")
        if robots_info['sitemap_allowed']:
            results['validation_score'] += 2
            if verbose:
                print(f"  ✓ Sitemaps allowed")
        else:
            if verbose:
                print(f"  ✗ Sitemaps disallowed")

        if robots_info['sitemaps']:
            results['validation_score'] += 2
            if verbose:
                print(f"  ✓ {len(robots_info['sitemaps'])} sitemap(s) declared")
    else:
        if verbose:
            print("  ⚠ No robots.txt (assuming allowed)")
        results['validation_score'] += 1

    time.sleep(0.2)

    # Check 3: E-commerce signals
    ecommerce = check_for_ecommerce_signals(domain)
    results['checks']['ecommerce'] = ecommerce

    if ecommerce['accessible']:
        if verbose:
            print("  ✓ Website accessible")
        results['validation_score'] += 1

        if ecommerce['has_cart'] or ecommerce['has_checkout']:
            results['validation_score'] += 3
            if verbose:
                print("  ✓ Has shopping cart/checkout")

        if ecommerce['has_product_links']:
            results['validation_score'] += 2
            if verbose:
                print("  ✓ Has product links")
        else:
            if verbose:
                print("  ✗ No product links found")

        if ecommerce['has_catalog']:
            results['validation_score'] += 1
            if verbose:
                print("  ✓ Has catalog/browse functionality")
    else:
        if verbose:
            print("  ✗ Website not accessible")

    # Final assessment
    # Score breakdown:
    # 0-3: Not scrapable
    # 4-6: Marginal
    # 7+: Good to scrape

    results['is_scrapable'] = results['validation_score'] >= 4

    if verbose:
        print(f"\n  Score: {results['validation_score']}/13")
        print(f"  Scrapable: {'✓ YES' if results['is_scrapable'] else '✗ NO'}")

    return results


def validate_suppliers_batch(suppliers: list, min_score: int = 4) -> list:
    """
    Validate multiple suppliers and return only scrapable ones.

    Args:
        suppliers: List of supplier dicts
        min_score: Minimum validation score to keep supplier

    Returns:
        List of validated suppliers that passed
    """
    validated = []

    print(f"\n{'='*70}")
    print(f"VALIDATING {len(suppliers)} SUPPLIERS")
    print(f"{'='*70}")

    for idx, supplier in enumerate(suppliers, 1):
        print(f"\n[{idx}/{len(suppliers)}]", end=" ")

        result = validate_supplier(supplier, verbose=True)

        if result['validation_score'] >= min_score:
            validated.append({
                **supplier,
                'validation_score': result['validation_score'],
                'validation_checks': result['checks']
            })

        # Politeness delay
        time.sleep(0.5)

    print(f"\n{'='*70}")
    print(f"VALIDATION COMPLETE")
    print(f"{'='*70}")
    print(f"Passed: {len(validated)}/{len(suppliers)} suppliers")
    print(f"Success rate: {len(validated)/len(suppliers)*100:.1f}%")

    return validated


if __name__ == "__main__":
    # Test with some sample suppliers
    test_suppliers = [
        {
            'supplier_id': 'test1',
            'name': 'US Plastic Corp',
            'domain': 'usplastic.com'
        },
        {
            'supplier_id': 'test2',
            'name': 'McMaster-Carr',
            'domain': 'mcmaster.com'
        },
        {
            'supplier_id': 'test3',
            'name': 'Ace Hardware (franchise)',
            'domain': 'acehardware.com'
        }
    ]

    validated = validate_suppliers_batch(test_suppliers, min_score=4)

    print(f"\nScrapable suppliers:")
    for supplier in validated:
        print(f"  • {supplier['name']} (score: {supplier['validation_score']})")
