"""
Improved product extraction with better validation.
Wraps the original product_extract.py with additional quality checks.
"""

import re
from typing import Optional, Dict, List
from urllib.parse import urlparse

try:
    from .product_extract import extract_product as extract_product_original
except ImportError:
    from product_extract import extract_product as extract_product_original


def is_valid_product(product: Dict, min_quality_score: int = 3) -> bool:
    """
    Validate if extracted data represents a real product.

    Quality scoring:
    - Has real product name (not generic): +2
    - Has price: +2
    - Has SKU/MPN: +1
    - Has specifications: +2
    - Has datasheet URL: +1
    - Has certifications: +1

    Args:
        product: Product dictionary
        min_quality_score: Minimum score to be considered valid (default: 3)

    Returns:
        True if product passes validation
    """
    if not product:
        return False

    quality_score = 0
    name = product.get('name', '').strip()

    # Check 1: Name quality
    generic_names = [
        'automotive', 'industrial', 'category', 'department',
        'products', 'catalog', 'shop', 'store', 'featured',
        'new products', 'brands', 'quick order', 'returns',
        'help', 'support', 'contact', 'about'
    ]

    if name:
        name_lower = name.lower()
        is_generic = any(generic in name_lower for generic in generic_names)

        if not is_generic and len(name) > 3:
            # Good product name
            quality_score += 2
        elif not is_generic:
            # Short but not generic
            quality_score += 1

    # Check 2: Has price
    price_text = product.get('price_text', '')
    if price_text and price_text.strip():
        # Check if it looks like a real price (has numbers/currency)
        if re.search(r'[\$\€\£\¥]?\d+', price_text):
            quality_score += 2

    # Check 3: Has SKU or MPN
    sku = product.get('sku', '')
    mpn = product.get('mpn', '')

    if sku and sku.strip() and sku.strip().upper() != 'S':
        # Has real SKU (not just "S" placeholder)
        quality_score += 1

    if mpn and mpn.strip():
        quality_score += 1

    # Check 4: Has specifications
    specs_raw = product.get('specs_raw', {})
    specs_canonical = product.get('specs_canonical', {})

    if specs_raw and len(specs_raw) > 2:
        # Has meaningful specs (more than 2 fields)
        quality_score += 2
    elif specs_raw and len(specs_raw) > 0:
        quality_score += 1

    if specs_canonical and len(specs_canonical) > 0:
        quality_score += 1

    # Check 5: Has datasheet URL
    datasheet_url = product.get('datasheet_url', '')
    if datasheet_url and datasheet_url.strip():
        quality_score += 1

    # Check 6: Has certifications
    certifications = product.get('certifications', [])
    if certifications and len(certifications) > 0:
        quality_score += 1

    # Final validation
    passed = quality_score >= min_quality_score

    if not passed:
        print(f"    ⚠ Low quality product (score: {quality_score}/{min_quality_score}): {name}")

    return passed


def extract_product_improved(url: str, keyword_terms: List[str], min_quality: int = 3) -> Optional[Dict]:
    """
    Extract product with improved validation.

    Args:
        url: Product page URL
        keyword_terms: List of keyword terms for matching
        min_quality: Minimum quality score (0-10, default: 3)

    Returns:
        Product dictionary if valid, None otherwise
    """
    print(f"Extracting product from: {url}")

    # Use original extraction logic
    product = extract_product_original(url, keyword_terms)

    if not product:
        print(f"  ✗ No product data extracted")
        return None

    # Validate product quality
    if not is_valid_product(product, min_quality_score=min_quality):
        print(f"  ✗ Product failed quality check: {product.get('name', 'Unknown')}")
        return None

    print(f"Successfully extracted product: {product.get('name', 'Unknown')}")
    return product


def extract_products_batch(
    urls: List[Dict],
    keyword_terms: List[str],
    max_products: int = 10,
    min_quality: int = 3,
    delay: float = 1.0
) -> List[Dict]:
    """
    Extract products from multiple URLs with quality filtering.

    Args:
        urls: List of URL dictionaries
        keyword_terms: Keyword terms for matching
        max_products: Maximum products to extract
        min_quality: Minimum quality score
        delay: Delay between requests

    Returns:
        List of validated products
    """
    import time

    products = []

    for idx, url_data in enumerate(urls[:max_products * 3], 1):  # Try 3x to account for failures
        if len(products) >= max_products:
            break

        url = url_data.get('url', url_data) if isinstance(url_data, dict) else url_data

        print(f"  [{idx}] Extracting: {url}")

        product = extract_product_improved(url, keyword_terms, min_quality=min_quality)

        if product:
            products.append(product)
            print(f"    ✓ Product {len(products)}/{max_products}: {product.get('name', 'Unknown')}")

        # Politeness delay
        if delay > 0:
            time.sleep(delay)

    return products


if __name__ == "__main__":
    # Test validation
    print("Testing product validation:")
    print("=" * 70)

    # Test case 1: Generic category page (should fail)
    test_product_1 = {
        'name': 'Automotive',
        'sku': 'S',
        'price_text': None,
        'specs_raw': {'itemlistelement': 'Hose Repair Parts'},
        'specs_canonical': {},
        'certifications': [],
        'datasheet_url': None
    }

    result_1 = is_valid_product(test_product_1)
    print(f"\nTest 1 - Generic category page:")
    print(f"  Name: {test_product_1['name']}")
    print(f"  Valid: {result_1} (expected: False)")

    # Test case 2: Real product (should pass)
    test_product_2 = {
        'name': '2mm PETG Clear Plastic Sheet 12x24 inch',
        'sku': 'PETG-2MM-1224',
        'mpn': 'PS-PETG-2-1224',
        'price_text': '$45.99',
        'specs_raw': {
            'thickness': '2mm',
            'material': 'PETG',
            'dimensions': '12 x 24 inches',
            'color': 'Clear',
            'finish': 'Glossy'
        },
        'specs_canonical': {
            'thickness_mm': 2.0,
            'width_mm': 304.8,
            'length_mm': 609.6
        },
        'certifications': ['FDA', 'NSF'],
        'datasheet_url': 'https://example.com/datasheets/petg-2mm.pdf'
    }

    result_2 = is_valid_product(test_product_2)
    print(f"\nTest 2 - Real product:")
    print(f"  Name: {test_product_2['name']}")
    print(f"  Valid: {result_2} (expected: True)")

    # Test case 3: Marginal product (should depend on threshold)
    test_product_3 = {
        'name': 'Quick Order',
        'sku': 'S',
        'price_text': None,
        'specs_raw': {},
        'specs_canonical': {},
        'certifications': [],
        'datasheet_url': None
    }

    result_3 = is_valid_product(test_product_3)
    print(f"\nTest 3 - Utility page:")
    print(f"  Name: {test_product_3['name']}")
    print(f"  Valid: {result_3} (expected: False)")
