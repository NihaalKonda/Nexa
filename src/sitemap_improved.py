"""
Improved sitemap module with better product URL detection.
This is separate from the original sitemap.py to preserve working logic.
"""

import re
import time
import xml.etree.ElementTree as ET
from typing import List, Optional, Set, Dict
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import requests
from bs4 import BeautifulSoup

try:
    from .robots import can_crawl
except ImportError:
    from robots import can_crawl


def fetch_sitemap_content(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch sitemap content from URL."""
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ProductCrawler/2.0)',
                'Accept': 'application/xml, text/xml, text/plain'
            }
        )

        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch sitemap {url}: HTTP {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap {url}: {e}")
        return None


def parse_sitemap_index(content: str, base_url: str) -> List[str]:
    """Parse a sitemap index file to get individual sitemap URLs."""
    sitemap_urls = []

    try:
        root = ET.fromstring(content)
        namespace = ''
        if root.tag.startswith('{'):
            namespace = root.tag.split('}')[0] + '}'

        for sitemap in root.findall(f'{namespace}sitemap'):
            loc_elem = sitemap.find(f'{namespace}loc')
            if loc_elem is not None and loc_elem.text:
                sitemap_url = urljoin(base_url, loc_elem.text.strip())
                sitemap_urls.append(sitemap_url)

    except ET.ParseError:
        loc_pattern = r'<loc>([^<]+)</loc>'
        matches = re.findall(loc_pattern, content, re.IGNORECASE)
        for match in matches:
            sitemap_url = urljoin(base_url, match.strip())
            sitemap_urls.append(sitemap_url)

    return sitemap_urls


def parse_sitemap_urls(content: str, base_url: str) -> List[dict]:
    """Parse a sitemap to extract URLs with metadata."""
    urls = []

    try:
        root = ET.fromstring(content)
        namespace = ''
        if root.tag.startswith('{'):
            namespace = root.tag.split('}')[0] + '}'

        for url_elem in root.findall(f'{namespace}url'):
            loc_elem = url_elem.find(f'{namespace}loc')
            if loc_elem is not None and loc_elem.text:
                url_data = {
                    'url': urljoin(base_url, loc_elem.text.strip()),
                    'lastmod': None,
                    'priority': None,
                    'changefreq': None
                }

                lastmod_elem = url_elem.find(f'{namespace}lastmod')
                if lastmod_elem is not None and lastmod_elem.text:
                    url_data['lastmod'] = lastmod_elem.text.strip()

                priority_elem = url_elem.find(f'{namespace}priority')
                if priority_elem is not None and priority_elem.text:
                    try:
                        url_data['priority'] = float(priority_elem.text.strip())
                    except ValueError:
                        pass

                changefreq_elem = url_elem.find(f'{namespace}changefreq')
                if changefreq_elem is not None and changefreq_elem.text:
                    url_data['changefreq'] = changefreq_elem.text.strip()

                urls.append(url_data)

    except ET.ParseError:
        loc_pattern = r'<loc>([^<]+)</loc>'
        matches = re.findall(loc_pattern, content, re.IGNORECASE)
        for match in matches:
            urls.append({
                'url': urljoin(base_url, match.strip()),
                'lastmod': None,
                'priority': None,
                'changefreq': None
            })

    return urls


def is_product_url_improved(url: str) -> bool:
    """
    Improved product URL detection with stricter filtering.

    Key improvements:
    1. Requires specific product indicators (IDs, SKUs, parameters)
    2. Excludes utility pages (brands, quickorder, returns, etc.)
    3. Better handling of query parameters
    4. More aggressive category/listing page exclusion

    Args:
        url: URL to check

    Returns:
        True if URL likely points to an actual product detail page
    """
    url_lower = url.lower()
    parsed = urlparse(url)
    path = parsed.path.lower()
    query_params = parse_qs(parsed.query)

    # FIRST: Aggressively exclude utility/navigation pages
    exclude_patterns = [
        # Utility pages
        r'/brands?\.aspx',
        r'/brands?\.html',
        r'/brands?/',
        r'/newitems',
        r'/new[-_]products',
        r'/quickorder',
        r'/quick[-_]order',
        r'/returns?/',
        r'/help/',
        r'/content/',
        r'/info/',

        # Category/listing pages
        r'/category/',
        r'/categories/',
        r'/catalog/$',  # Catalog homepage
        r'/catalog\.aspx$',
        r'/products/$',  # Product listing
        r'/shop/$',
        r'/store/$',

        # Department/section pages
        r'/department',
        r'/section',
        r'/automotive/$',
        r'/industrial/$',
        r'/repair[-_]',
        r'/hose[-_]repair[-_]parts/$',

        # Definitely not products
        r'/blog/',
        r'/news/',
        r'/about/',
        r'/contact/',
        r'/careers/',
        r'/support/',
        r'/privacy/',
        r'/terms/',
        r'/login/',
        r'/register/',
        r'/account/',
        r'/cart/',
        r'/checkout/',
        r'/search/',
        r'/tag[s]?/',
        r'/author[s]?/',
        r'/admin/',
        r'/wp-',
        r'/assets/',
        r'/static/',
        r'/images/',
        r'/css/',
        r'/js/',
        r'/media/',
        r'/pdf/',
        r'\.pdf$',
    ]

    for pattern in exclude_patterns:
        if re.search(pattern, path):
            return False

    # SECOND: Require strong product indicators

    # 1. Check for product ID in query parameters
    product_params = ['itemid', 'productid', 'id', 'sku', 'pid', 'partno', 'part', 'mpn']
    has_product_param = any(
        param in [p.lower() for p in query_params.keys()]
        for param in product_params
    )

    if has_product_param:
        # Make sure the ID looks real (not empty, has numbers)
        for param_key in query_params.keys():
            if param_key.lower() in product_params:
                param_value = query_params[param_key][0] if query_params[param_key] else ''
                # Require actual value with numbers
                if param_value and re.search(r'\d', param_value) and len(param_value) >= 3:
                    return True

    # 2. Check for product-like path patterns with IDs
    # These patterns should have numbers/IDs in them
    product_path_patterns = [
        r'/product[s]?/[^/]+/\d+',  # /products/name/123
        r'/product[s]?/[a-z0-9\-]{8,}',  # /product/sku-abc123xyz
        r'/item[s]?/[a-z0-9\-]{6,}',  # /item/abc123
        r'/part[s]?/[a-z0-9\-]{6,}',  # /parts/xyz789
        r'/p/[a-z0-9\-]{6,}',  # /p/product-id
        r'/dp/[A-Z0-9]{6,}',  # /dp/B08XYZ (Amazon-style)
        r'/sku-\d+',  # /sku-12345
        r'/model-[a-z0-9\-]+',  # /model-xyz
    ]

    for pattern in product_path_patterns:
        if re.search(pattern, path):
            return True

    # 3. Check for .aspx/.html pages with item/product in name AND parameters
    if re.search(r'/(item|product|catalog)\.aspx', path) and has_product_param:
        return True

    # 4. Path ends with a product-looking identifier (numbers, SKU-style)
    path_parts = path.rstrip('/').split('/')
    if len(path_parts) > 0:
        last_part = path_parts[-1]
        # Check if last part looks like a product identifier
        # Must have numbers and be reasonably long
        if re.match(r'^[a-z0-9\-_]{8,}$', last_part) and re.search(r'\d', last_part):
            # Additional check: not a generic word
            generic_words = ['index', 'default', 'home', 'main', 'page']
            if last_part not in generic_words:
                return True

    # Default: NOT a product page
    return False


def discover_product_urls_improved(domain: str, cap: int = 100) -> List[dict]:
    """
    Improved product URL discovery with better filtering.

    Args:
        domain: Domain to search
        cap: Maximum number of URLs to return

    Returns:
        List of product URL dictionaries
    """
    if not domain.startswith(('http://', 'https://')):
        domain = f'https://{domain}'

    base_url = domain

    # Check robots.txt
    sitemap_url = urljoin(base_url, '/sitemap.xml')
    if not can_crawl(domain, '/sitemap.xml'):
        print(f"Robots.txt disallows access to /sitemap.xml for {domain}")
        return []

    print(f"Checking sitemap: {sitemap_url}")

    all_urls = []
    seen_urls = set()

    # Try to fetch main sitemap
    content = fetch_sitemap_content(sitemap_url)

    if content:
        # Check if it's a sitemap index
        if '<sitemapindex' in content or '<sitemap>' in content:
            print(f"Found sitemap index at {sitemap_url}")
            sitemap_urls = parse_sitemap_index(content, base_url)

            # Prioritize product-specific sitemaps
            product_sitemaps = [
                url for url in sitemap_urls
                if any(keyword in url.lower() for keyword in [
                    'product', 'item', 'catalog', 'part', 'sku'
                ])
            ]

            # Try product-specific sitemaps first
            for sm_url in product_sitemaps[:5]:  # Limit to 5 sitemaps
                print(f"Checking product sitemap: {sm_url}")
                sm_content = fetch_sitemap_content(sm_url)
                if sm_content:
                    urls = parse_sitemap_urls(sm_content, base_url)
                    print(f"Found {len(urls)} URLs in {sm_url}")

                    for url_data in urls:
                        url = url_data['url']
                        if url not in seen_urls and is_product_url_improved(url):
                            seen_urls.add(url)
                            all_urls.append(url_data)
                            print(f"  ✓ Product URL: {url}")

                            if len(all_urls) >= cap:
                                break

                if len(all_urls) >= cap:
                    break

                time.sleep(0.1)  # Politeness delay
        else:
            # Regular sitemap
            print(f"Parsing regular sitemap: {sitemap_url}")
            urls = parse_sitemap_urls(content, base_url)

            for url_data in urls:
                url = url_data['url']
                if url not in seen_urls and is_product_url_improved(url):
                    seen_urls.add(url)
                    all_urls.append(url_data)
                    print(f"  ✓ Product URL: {url}")

                    if len(all_urls) >= cap:
                        break

    # Try robots.txt for sitemap references
    if len(all_urls) == 0:
        print(f"Checking sitemap: {urljoin(base_url, '/robots.txt')}")
        try:
            robots_response = requests.get(
                urljoin(base_url, '/robots.txt'),
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ProductCrawler/2.0)'}
            )

            if robots_response.status_code == 200:
                sitemap_refs = re.findall(
                    r'Sitemap:\s*(.+)',
                    robots_response.text,
                    re.IGNORECASE
                )

                for sitemap_ref in sitemap_refs[:3]:  # Limit to 3 sitemaps
                    sitemap_ref = sitemap_ref.strip()
                    print(f"Checking sitemap: {sitemap_ref}")

                    sm_content = fetch_sitemap_content(sitemap_ref)
                    if sm_content:
                        # Check if index or regular
                        if '<sitemapindex' in sm_content:
                            sub_sitemaps = parse_sitemap_index(sm_content, base_url)
                            product_sitemaps = [
                                url for url in sub_sitemaps
                                if any(kw in url.lower() for kw in ['product', 'item'])
                            ]

                            for sub_sm_url in product_sitemaps[:3]:
                                sub_content = fetch_sitemap_content(sub_sm_url)
                                if sub_content:
                                    urls = parse_sitemap_urls(sub_content, base_url)

                                    for url_data in urls:
                                        url = url_data['url']
                                        if url not in seen_urls and is_product_url_improved(url):
                                            seen_urls.add(url)
                                            all_urls.append(url_data)
                                            print(f"  ✓ Product URL: {url}")

                                            if len(all_urls) >= cap:
                                                break
                        else:
                            urls = parse_sitemap_urls(sm_content, base_url)

                            for url_data in urls:
                                url = url_data['url']
                                if url not in seen_urls and is_product_url_improved(url):
                                    seen_urls.add(url)
                                    all_urls.append(url_data)
                                    print(f"  ✓ Product URL: {url}")

                                    if len(all_urls) >= cap:
                                        break

                    if len(all_urls) >= cap:
                        break

                    time.sleep(0.1)
        except Exception as e:
            print(f"Error checking robots.txt: {e}")

    print(f"Discovered {len(all_urls)} product URLs for {domain}")
    return all_urls


if __name__ == "__main__":
    # Test with some URLs
    test_urls = [
        "https://www.usplastic.com/catalog/brands.aspx",  # Should be False
        "https://www.usplastic.com/catalog/newitems.aspx",  # Should be False
        "https://www.usplastic.com/catalog/item.aspx?itemid=25358",  # Should be True
        "https://www.usplastic.com/catalog/item.aspx?itemid=25359",  # Should be True
        "https://www.doitbest.com/category/automotive/",  # Should be False
        "https://www.mcmaster.com/products/plastic-sheets/",  # Should be False
        "https://www.mcmaster.com/1234/plastic-sheet-petg/",  # Should be True
    ]

    print("Testing improved product URL detection:")
    print("=" * 70)

    for url in test_urls:
        result = is_product_url_improved(url)
        status = "✓ PRODUCT" if result else "✗ NOT PRODUCT"
        print(f"{status}: {url}")
