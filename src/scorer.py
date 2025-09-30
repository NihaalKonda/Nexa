"""
Scoring module for calculating product relevance and freshness scores.
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dateutil.parser import parse as parse_date


def calculate_relevance_score(product: Dict, keyword_terms: List[str]) -> int:
    """
    Calculate relevance score based on keyword matches in name and specifications.
    
    Args:
        product: Product dictionary
        keyword_terms: List of search terms
        
    Returns:
        Relevance score (integer)
    """
    if not keyword_terms:
        return 0
    
    score = 0
    
    # Name matches (weighted 3x)
    name = product.get('name', '').lower()
    name_matches = 0
    for term in keyword_terms:
        if term.lower() in name:
            name_matches += 1
    score += name_matches * 3
    
    # SKU/MPN matches (weighted 2x)
    sku = product.get('sku', '') or ''
    mpn = product.get('mpn', '') or ''
    sku_mpn_text = f"{sku} {mpn}".lower()
    
    sku_mpn_matches = 0
    for term in keyword_terms:
        if term.lower() in sku_mpn_text:
            sku_mpn_matches += 1
    score += sku_mpn_matches * 2
    
    # Specifications matches (weighted 1x)
    specs_raw = product.get('specs_raw', {}) or {}
    specs_text = ' '.join(f"{k} {v}" for k, v in specs_raw.items()).lower()
    
    specs_matches = 0
    for term in keyword_terms:
        if term.lower() in specs_text:
            specs_matches += 1
    score += specs_matches
    
    # Certifications matches (weighted 1x)
    certifications = product.get('certifications', []) or []
    cert_text = ' '.join(certifications).lower()
    
    cert_matches = 0
    for term in keyword_terms:
        if term.lower() in cert_text:
            cert_matches += 1
    score += cert_matches
    
    return score


def calculate_freshness_score(product: Dict) -> int:
    """
    Calculate freshness score based on last modification dates.
    
    Args:
        product: Product dictionary
        
    Returns:
        Freshness score (0-10)
    """
    score = 0
    now = datetime.now(timezone.utc)
    
    # Check last_seen_at
    last_seen_str = product.get('last_seen_at')
    if last_seen_str:
        try:
            last_seen = parse_date(last_seen_str)
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            
            days_old = (now - last_seen).days
            
            if days_old <= 7:       # Within a week
                score += 5
            elif days_old <= 30:    # Within a month
                score += 3
            elif days_old <= 90:    # Within 3 months
                score += 1
                
        except Exception:
            pass
    
    # TODO: Could add HTTP Last-Modified header parsing here
    # TODO: Could add sitemap lastmod date parsing here
    
    return min(score, 10)  # Cap at 10


def calculate_datasheet_bonus(product: Dict) -> int:
    """
    Calculate bonus score for having a datasheet.
    
    Args:
        product: Product dictionary
        
    Returns:
        Datasheet bonus score
    """
    datasheet_url = product.get('datasheet_url')
    if datasheet_url and datasheet_url.strip():
        return 2
    return 0


def calculate_completeness_score(product: Dict) -> int:
    """
    Calculate score based on completeness of product information.
    
    Args:
        product: Product dictionary
        
    Returns:
        Completeness score (0-10)
    """
    score = 0
    
    # Required fields
    if product.get('name'):
        score += 2
    
    # Valuable fields
    if product.get('sku') or product.get('mpn'):
        score += 2
    
    if product.get('specs_raw') and len(product['specs_raw']) >= 3:
        score += 2
    
    if product.get('certifications') and len(product['certifications']) > 0:
        score += 1
    
    if product.get('price_text'):
        score += 1
    
    if product.get('datasheet_url'):
        score += 2
    
    return min(score, 10)  # Cap at 10


def calculate_canonical_specs_bonus(product: Dict) -> int:
    """
    Calculate bonus for having normalized/canonical specifications.
    
    Args:
        product: Product dictionary
        
    Returns:
        Canonical specs bonus score
    """
    specs_canonical = product.get('specs_canonical', {})
    if not specs_canonical:
        return 0
    
    # Bonus points for key normalized dimensions
    important_specs = [
        'thickness_mm', 'width_mm', 'length_mm', 'diameter_mm',
        'max_temp_c', 'max_pressure_psi', 'hardness_shore_a'
    ]
    
    bonus = 0
    for spec in important_specs:
        if spec in specs_canonical:
            bonus += 1
    
    return min(bonus, 5)  # Cap bonus


def calculate_total_score(product: Dict, keyword_terms: List[str]) -> int:
    """
    Calculate total score for a product.
    
    Args:
        product: Product dictionary
        keyword_terms: List of search terms
        
    Returns:
        Total score
    """
    relevance = calculate_relevance_score(product, keyword_terms)
    freshness = calculate_freshness_score(product)
    datasheet_bonus = calculate_datasheet_bonus(product)
    completeness = calculate_completeness_score(product)
    canonical_bonus = calculate_canonical_specs_bonus(product)
    
    total = relevance + freshness + datasheet_bonus + completeness + canonical_bonus
    
    return total


def score_product(product: Dict, keyword_terms: List[str]) -> Dict:
    """
    Score a product and return detailed scoring breakdown.
    
    Args:
        product: Product dictionary
        keyword_terms: List of search terms
        
    Returns:
        Dictionary with updated product and scoring details
    """
    # Calculate individual scores
    relevance = calculate_relevance_score(product, keyword_terms)
    freshness = calculate_freshness_score(product)
    datasheet_bonus = calculate_datasheet_bonus(product)
    completeness = calculate_completeness_score(product)
    canonical_bonus = calculate_canonical_specs_bonus(product)
    total = relevance + freshness + datasheet_bonus + completeness + canonical_bonus
    
    # Update product with total score
    scored_product = product.copy()
    scored_product['score'] = total
    
    # Create scoring breakdown
    scoring_breakdown = {
        'relevance_score': relevance,
        'freshness_score': freshness,
        'datasheet_bonus': datasheet_bonus,
        'completeness_score': completeness,
        'canonical_specs_bonus': canonical_bonus,
        'total_score': total
    }
    
    return {
        'product': scored_product,
        'scoring_breakdown': scoring_breakdown
    }


def score_products(products: List[Dict], keyword_terms: List[str]) -> List[Dict]:
    """
    Score a list of products and sort by score.
    
    Args:
        products: List of product dictionaries
        keyword_terms: List of search terms
        
    Returns:
        List of products sorted by score (highest first)
    """
    scored_products = []
    
    for product in products:
        result = score_product(product, keyword_terms)
        scored_products.append(result['product'])
    
    # Sort by score (highest first)
    scored_products.sort(key=lambda p: p.get('score', 0), reverse=True)
    
    return scored_products


def get_top_products(products: List[Dict], keyword_terms: List[str], limit: int = 10) -> List[Dict]:
    """
    Get top N products by score.
    
    Args:
        products: List of product dictionaries  
        keyword_terms: List of search terms
        limit: Maximum number of products to return
        
    Returns:
        List of top products
    """
    scored_products = score_products(products, keyword_terms)
    return scored_products[:limit]


def filter_products_by_min_score(products: List[Dict], keyword_terms: List[str], min_score: int = 5) -> List[Dict]:
    """
    Filter products by minimum score threshold.
    
    Args:
        products: List of product dictionaries
        keyword_terms: List of search terms
        min_score: Minimum score threshold
        
    Returns:
        List of products meeting minimum score
    """
    scored_products = score_products(products, keyword_terms)
    return [p for p in scored_products if p.get('score', 0) >= min_score]


def analyze_scoring_distribution(products: List[Dict], keyword_terms: List[str]) -> Dict:
    """
    Analyze the distribution of scores across products.
    
    Args:
        products: List of product dictionaries
        keyword_terms: List of search terms
        
    Returns:
        Dictionary with scoring statistics
    """
    if not products:
        return {}
    
    scored_products = score_products(products, keyword_terms)
    scores = [p.get('score', 0) for p in scored_products]
    
    analysis = {
        'total_products': len(products),
        'min_score': min(scores) if scores else 0,
        'max_score': max(scores) if scores else 0,
        'avg_score': sum(scores) / len(scores) if scores else 0,
        'score_ranges': {
            'excellent (20+)': len([s for s in scores if s >= 20]),
            'good (10-19)': len([s for s in scores if 10 <= s < 20]),
            'fair (5-9)': len([s for s in scores if 5 <= s < 10]),
            'poor (0-4)': len([s for s in scores if s < 5])
        }
    }
    
    return analysis


if __name__ == "__main__":
    # Test the scoring functions
    print("=" * 60)
    print("TESTING SCORING MODULE")
    print("=" * 60)
    
    # Create test products
    test_products = [
        {
            'product_id': 'test1',
            'name': 'PETG Sheet 2mm Clear',
            'sku': 'PET-SH-2MM-CLR',
            'mpn': 'PETG2000C',
            'specs_raw': {
                'material': 'PETG',
                'thickness': '2.0mm',
                'color': 'clear',
                'temperature rating': '80°C max'
            },
            'specs_canonical': {
                'thickness_mm': 2.0,
                'max_temp_c': 80.0
            },
            'certifications': ['FDA approved', 'RoHS compliant'],
            'datasheet_url': 'https://example.com/datasheet.pdf',
            'last_seen_at': '2024-01-15T10:00:00Z',
            'price_text': '$45.99'
        },
        {
            'product_id': 'test2', 
            'name': 'PVC Gasket Round',
            'sku': 'PVC-GSK-RND',
            'specs_raw': {
                'material': 'PVC',
                'shape': 'round'
            },
            'certifications': [],
            'datasheet_url': None,
            'last_seen_at': '2023-06-01T10:00:00Z',
        },
        {
            'product_id': 'test3',
            'name': 'PETG Film Clear 0.5mm',
            'sku': 'PET-FILM-05',
            'specs_raw': {
                'material': 'PETG',
                'thickness': '0.5mm',
                'color': 'clear',
                'width': '1000mm'
            },
            'specs_canonical': {
                'thickness_mm': 0.5,
                'width_mm': 1000.0
            },
            'certifications': ['ISO 9001'],
            'datasheet_url': 'https://example.com/film-datasheet.pdf',
            'last_seen_at': '2024-01-20T10:00:00Z',
            'price_text': '$28.50'
        }
    ]
    
    test_keywords = ['petg', 'clear', '2mm', 'sheet']
    
    print("\n1. Testing individual scoring components:")
    for i, product in enumerate(test_products):
        print(f"\n  Product {i+1}: {product['name']}")
        
        result = score_product(product, test_keywords)
        breakdown = result['scoring_breakdown']
        
        print(f"    Relevance: {breakdown['relevance_score']}")
        print(f"    Freshness: {breakdown['freshness_score']}")
        print(f"    Datasheet: {breakdown['datasheet_bonus']}")
        print(f"    Completeness: {breakdown['completeness_score']}")
        print(f"    Canonical: {breakdown['canonical_specs_bonus']}")
        print(f"    TOTAL: {breakdown['total_score']}")
    
    print("\n2. Testing product ranking:")
    ranked_products = score_products(test_products, test_keywords)
    
    print("  Ranked products (by score):")
    for i, product in enumerate(ranked_products):
        print(f"    {i+1}. {product['name']} (Score: {product['score']})")
    
    print("\n3. Testing scoring analysis:")
    analysis = analyze_scoring_distribution(test_products, test_keywords)
    print(f"  Score analysis:")
    print(f"    Total products: {analysis['total_products']}")
    print(f"    Score range: {analysis['min_score']} - {analysis['max_score']}")
    print(f"    Average score: {analysis['avg_score']:.1f}")
    print(f"    Distribution:")
    for range_name, count in analysis['score_ranges'].items():
        print(f"      {range_name}: {count} products")
    
    print("\n4. Testing filtering:")
    top_3 = get_top_products(test_products, test_keywords, limit=3)
    print(f"  Top 3 products:")
    for i, product in enumerate(top_3):
        print(f"    {i+1}. {product['name']} (Score: {product['score']})")
    
    min_score_filter = filter_products_by_min_score(test_products, test_keywords, min_score=10)
    print(f"  Products with score >= 10: {len(min_score_filter)}")
    for product in min_score_filter:
        print(f"    {product['name']} (Score: {product['score']})")