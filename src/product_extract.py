"""
Product extraction module for parsing product pages and extracting structured data.
"""

import re
import hashlib
import requests
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Comment
import time


def generate_product_id(domain: str, name: str, source_url: str) -> str:
    """
    Generate a unique product ID based on domain, name, and source URL.
    
    Args:
        domain: Domain name
        name: Product name
        source_url: Source URL
        
    Returns:
        Hashed product ID
    """
    combined = f"{domain}|{name}|{source_url}".lower().strip()
    return hashlib.md5(combined.encode()).hexdigest()


def fetch_page_content(url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
    """
    Fetch and parse HTML content from URL.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        BeautifulSoup object or None if failed
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                'User-Agent': 'contexgt-crawler/1.0 (product extraction)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove comments and script tags for cleaner parsing
            for element in soup(["script", "style", "noscript"]):
                element.decompose()
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            return soup
        else:
            print(f"Failed to fetch {url}: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_product_name(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract product name using various heuristics.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Product name or None if not found
    """
    # Try different selectors in order of preference
    selectors = [
        'h1[itemprop="name"]',
        '[itemprop="name"]',
        'h1.product-title',
        'h1.product-name', 
        '.product-title h1',
        '.product-name h1',
        'h1',
        '[data-testid="product-title"]',
        '.pdp-product-name',
        '#product-name',
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(strip=True)
            if text and len(text) > 5 and len(text) < 200:  # Reasonable length
                return text
    
    # Try meta tags
    meta_selectors = [
        'meta[property="og:title"]',
        'meta[name="title"]',
        'meta[property="twitter:title"]',
    ]
    
    for selector in meta_selectors:
        element = soup.select_one(selector)
        if element and element.get('content'):
            content = element.get('content').strip()
            if content and len(content) > 5 and len(content) < 200:
                return content
    
    # Last resort - title tag
    title = soup.find('title')
    if title:
        title_text = title.get_text(strip=True)
        # Clean up common title patterns
        title_text = re.sub(r'\s*\|\s*.*$', '', title_text)  # Remove "| Company Name"
        title_text = re.sub(r'\s*-\s*.*$', '', title_text)   # Remove "- Company Name"
        if title_text and len(title_text) > 5:
            return title_text
    
    return None


def extract_sku_mpn(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract SKU and MPN (Manufacturer Part Number).
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Tuple of (sku, mpn) or (None, None) if not found
    """
    sku = None
    mpn = None
    
    # Common patterns to look for
    sku_patterns = [
        r'(?:sku|item\s*#?|part\s*#?|model\s*#?|product\s*#?)[\s:]*([a-z0-9\-_]+)',
        r'(?:item|part|model|product)\s*(?:number|code|id)[\s:]*([a-z0-9\-_]+)',
    ]
    
    mpn_patterns = [
        r'(?:mpn|manufacturer\s*part\s*#?|mfg\s*part\s*#?)[\s:]*([a-z0-9\-_]+)',
        r'manufacturer\s*(?:number|code|id)[\s:]*([a-z0-9\-_]+)',
    ]
    
    # Search in text content
    text_content = soup.get_text().lower()
    
    for pattern in sku_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match and not sku:
            sku = match.group(1).upper()
    
    for pattern in mpn_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match and not mpn:
            mpn = match.group(1).upper()
    
    # Also check structured data
    structured_selectors = [
        '[itemprop="sku"]',
        '[itemprop="mpn"]',
        '[itemprop="productID"]',
        '.sku',
        '.mpn',
        '.part-number',
        '.product-id',
        '#sku',
        '#mpn',
        '#part-number',
    ]
    
    for selector in structured_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(strip=True)
            if text and re.match(r'^[a-z0-9\-_]+$', text, re.IGNORECASE):
                if 'sku' in selector.lower() or 'part' in selector.lower():
                    if not sku:
                        sku = text.upper()
                elif 'mpn' in selector.lower():
                    if not mpn:
                        mpn = text.upper()
    
    return sku, mpn


def extract_price(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract price information as text (no parsing, just capture).
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Price text or None if not found
    """
    # Price patterns
    price_selectors = [
        '[itemprop="price"]',
        '.price',
        '.product-price',
        '#price',
        '.cost',
        '[data-testid*="price"]',
        '.price-current',
        '.sale-price',
        '.pricing',
        '.unit-price',
        '.list-price',
        '.bulk-price',
        '[class*="price"]',
        '[id*="price"]',
        '.amount',
        '.currency',
    ]
    
    for selector in price_selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(strip=True)
            # Look for currency symbols and numbers
            if re.search(r'[\$£€¥₹]\s*\d+|\d+\.\d{2}', text):
                return text
    
    # Search in text for currency patterns
    text_content = soup.get_text()
    
    # Try various price patterns
    price_patterns = [
        # Standard price labels
        r'(?:price|cost)[\s:]*[\$£€¥₹]\s*\d+(?:\.\d{2})?',
        # Bulk pricing (e.g., "124.982/Each", "27.50 each")
        r'\d+\.\d+\s*/\s*each',
        r'\d+\.\d+\s*each',
        # Price ranges
        r'[\$£€¥₹]\s*\d+(?:\.\d{2})?\s*-\s*[\$£€¥₹]\s*\d+(?:\.\d{2})?',
        # Just currency and number
        r'[\$£€¥₹]\s*\d+(?:\.\d{2})?',
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None


def extract_specifications(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extract specifications from tables and definition lists.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        Dictionary of specifications
    """
    specs = {}
    
    # Look for specification tables
    spec_tables = soup.find_all('table')
    for table in spec_tables:
        # Skip if table looks decorative (too few cells)
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue
            
        spec_count = 0
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                
                if label and value and len(label) < 100 and len(value) < 500:
                    # Clean up the label
                    label = re.sub(r'[^\w\s]', '', label).strip()
                    if label:
                        specs[label] = value
                        spec_count += 1
        
        # If we got good specs from this table, we can stop
        if spec_count >= 3:
            break
    
    # Look for definition lists if tables didn't work well
    if len(specs) < 3:
        dl_elements = soup.find_all('dl')
        for dl in dl_elements:
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')
            
            if len(dt_elements) == len(dd_elements):
                for dt, dd in zip(dt_elements, dd_elements):
                    label = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    
                    if label and value and len(label) < 100 and len(value) < 500:
                        label = re.sub(r'[^\w\s]', '', label).strip()
                        if label:
                            specs[label] = value
    
    # Look for structured data
    structured_specs = soup.find_all(attrs={'itemprop': True})
    for element in structured_specs:
        prop = element.get('itemprop')
        if prop and prop not in ['name', 'price', 'url', 'image']:
            value = element.get_text(strip=True)
            if value and len(value) < 500:
                specs[prop.lower()] = value
    
    return specs


def extract_certifications(soup: BeautifulSoup) -> List[str]:
    """
    Extract certifications and standards.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        List of certifications found
    """
    certifications = []
    text_content = soup.get_text()
    
    # Common certification patterns
    cert_patterns = [
        r'\bISO\s*\d+(?:-\d+)*\b',
        r'\bASTM\s*[A-Z]?\d+(?:-\d+)*\b',
        r'\bDIN\s*\d+(?:-\d+)*\b',
        r'\bMIL-\w+-\d+\b',
        r'\bUSP\s*Class\s*\w+\b',
        r'\bFDA\s*(?:approved|compliant)\b',
        r'\bRoHS\s*(?:compliant|certified)\b',
        r'\bREACH\s*(?:compliant|certified)\b',
        r'\bCE\s*(?:mark|marked|certified)\b',
        r'\bUL\s*(?:listed|certified|\d+)\b',
        r'\bNSF\s*\d*\b',
        r'\b3-A\s*Sanitary\b',
        r'\bITAR\s*(?:compliant|exempt)\b',
    ]
    
    for pattern in cert_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        for match in matches:
            cert = match.strip()
            if cert and cert not in certifications:
                certifications.append(cert)
    
    return certifications


def extract_datasheet_url(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """
    Find PDF datasheet links.
    
    Args:
        soup: BeautifulSoup object
        base_url: Base URL for resolving relative links
        
    Returns:
        Datasheet URL or None if not found
    """
    # Look for PDF links
    pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
    
    for link in pdf_links:
        href = link.get('href')
        link_text = link.get_text(strip=True).lower()
        
        # Prioritize links that mention datasheet, spec, technical data
        priority_terms = ['datasheet', 'data sheet', 'spec', 'specification', 'technical', 'tech data']
        
        if any(term in link_text for term in priority_terms):
            return urljoin(base_url, href)
    
    # If no priority PDF found, return first PDF
    if pdf_links:
        return urljoin(base_url, pdf_links[0].get('href'))
    
    return None


def check_keyword_relevance(soup: BeautifulSoup, keyword_terms: List[str]) -> bool:
    """
    Check if the page is relevant to the search keywords.
    
    Args:
        soup: BeautifulSoup object
        keyword_terms: List of keyword terms to match
        
    Returns:
        True if page appears relevant
    """
    if not keyword_terms:
        return True
    
    text_content = soup.get_text().lower()
    
    # Count matches
    matches = 0
    for term in keyword_terms:
        if term.lower() in text_content:
            matches += 1
    
    # Consider relevant if at least 15% of terms match or at least 2 terms match
    # This balances better matching with avoiding false positives
    relevance_threshold = max(2, len(keyword_terms) * 0.15)
    return matches >= relevance_threshold


def extract_product(url: str, keyword_terms: List[str] = None) -> Optional[Dict]:
    """
    Extract product information from a URL.
    
    Args:
        url: URL to extract from
        keyword_terms: List of keyword terms to check relevance
        
    Returns:
        Product dictionary or None if extraction failed
    """
    if keyword_terms is None:
        keyword_terms = []
    
    print(f"Extracting product from: {url}")
    
    # Fetch page content
    soup = fetch_page_content(url)
    if not soup:
        return None
    
    # Check keyword relevance first
    if not check_keyword_relevance(soup, keyword_terms):
        print(f"Page not relevant to keywords: {url}")
        return None
    
    # Extract components
    name = extract_product_name(soup)
    if not name:
        print(f"Could not extract product name from: {url}")
        return None
    
    sku, mpn = extract_sku_mpn(soup)
    price_text = extract_price(soup)
    specs_raw = extract_specifications(soup)
    certifications = extract_certifications(soup)
    datasheet_url = extract_datasheet_url(soup, url)
    
    # Get domain for product ID
    domain = urlparse(url).netloc
    
    # Create product dictionary
    product = {
        'product_id': generate_product_id(domain, name, url),
        'supplier_id': None,  # Will be set by caller
        'name': name,
        'sku': sku,
        'mpn': mpn,
        'price_text': price_text,
        'specs_raw': specs_raw,
        'specs_canonical': {},  # Will be filled by normalization
        'certifications': certifications,
        'datasheet_url': datasheet_url,
        'source_url': url,
        'last_seen_at': datetime.utcnow().isoformat() + 'Z',
        'score': 0  # Will be calculated by scorer
    }
    
    print(f"Successfully extracted product: {name}")
    return product


if __name__ == "__main__":
    # Test the product extraction functions
    print("=" * 60)
    print("TESTING PRODUCT EXTRACTION MODULE")
    print("=" * 60)
    
    # Create test HTML for demonstration
    test_html = """
    <html>
    <head>
        <title>PETG Sheet 2mm Clear - Industrial Plastics</title>
        <meta property="og:title" content="PETG Sheet 2mm Clear"/>
    </head>
    <body>
        <h1>PETG Sheet 2mm Clear</h1>
        <div class="product-info">
            <p>SKU: PET-SH-2MM-CLR</p>
            <p>MPN: PETG2000C</p>
            <p>Price: $45.99</p>
        </div>
        <table class="specifications">
            <tr><td>Material</td><td>PETG</td></tr>
            <tr><td>Thickness</td><td>2.0mm</td></tr>
            <tr><td>Width</td><td>1000mm</td></tr>
            <tr><td>Length</td><td>2000mm</td></tr>
            <tr><td>Color</td><td>Clear</td></tr>
            <tr><td>Temperature Rating</td><td>80°C max</td></tr>
        </table>
        <div class="certifications">
            <p>Certifications: FDA approved, RoHS compliant, ISO 9001</p>
        </div>
        <a href="/datasheets/petg-sheet-datasheet.pdf">Technical Datasheet PDF</a>
    </body>
    </html>
    """
    
    print("\n1. Testing HTML parsing components:")
    soup = BeautifulSoup(test_html, 'html.parser')
    
    # Test name extraction
    name = extract_product_name(soup)
    print(f"  Product name: {name}")
    
    # Test SKU/MPN extraction
    sku, mpn = extract_sku_mpn(soup)
    print(f"  SKU: {sku}, MPN: {mpn}")
    
    # Test price extraction
    price = extract_price(soup)
    print(f"  Price: {price}")
    
    # Test specifications
    specs = extract_specifications(soup)
    print(f"  Specifications: {len(specs)} found")
    for key, value in list(specs.items())[:3]:  # Show first 3
        print(f"    {key}: {value}")
    
    # Test certifications
    certs = extract_certifications(soup)
    print(f"  Certifications: {certs}")
    
    # Test datasheet URL
    datasheet = extract_datasheet_url(soup, "https://example.com")
    print(f"  Datasheet URL: {datasheet}")
    
    # Test keyword relevance
    keywords = ["petg", "sheet", "2mm", "clear"]
    relevant = check_keyword_relevance(soup, keywords)
    print(f"  Keyword relevance: {relevant}")
    
    print("\n2. Product extraction structure verified")
    print("  (Use extract_product(url, keywords) for real extraction)")
    
    print("\n3. Testing ID generation:")
    test_id = generate_product_id("example.com", "PETG Sheet 2mm", "https://example.com/product/123")
    print(f"  Sample product ID: {test_id}")