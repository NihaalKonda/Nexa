"""
Robots.txt module for checking crawling permissions and respecting site policies.
"""

import time
from typing import Optional, Dict, Tuple
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import requests


class RobotsChecker:
    """
    A robots.txt checker that caches robots.txt files and provides crawling permission checks.
    """
    
    def __init__(self, user_agent: str = "*"):
        """
        Initialize the robots checker.
        
        Args:
            user_agent: User agent string to use for robots.txt checks
        """
        self.user_agent = user_agent
        self.robots_cache: Dict[str, Tuple[RobotFileParser, float]] = {}
        self.cache_timeout = 3600  # Cache for 1 hour
        
    def _get_robots_url(self, domain: str) -> str:
        """
        Construct robots.txt URL from domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Full robots.txt URL
        """
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        return urljoin(domain, '/robots.txt')
    
    def _fetch_robots(self, domain: str) -> Optional[RobotFileParser]:
        """
        Fetch and parse robots.txt for a domain.
        
        Args:
            domain: Domain to fetch robots.txt for
            
        Returns:
            RobotFileParser instance or None if not available
        """
        robots_url = self._get_robots_url(domain)
        
        try:
            # Create robot parser
            rp = RobotFileParser()
            rp.set_url(robots_url)
            
            # Fetch with timeout and proper headers
            response = requests.get(
                robots_url,
                timeout=10,
                headers={
                    'User-Agent': 'contexgt-crawler/1.0 (compliance check)',
                    'Accept': 'text/plain'
                }
            )
            
            # Check if robots.txt exists and is accessible
            if response.status_code == 200:
                rp.set_url(robots_url)
                rp.read()
                return rp
            elif response.status_code == 404:
                # No robots.txt means everything is allowed
                return self._create_empty_robots(robots_url)
            else:
                # Other errors - be conservative and disallow
                print(f"Warning: Could not fetch robots.txt for {domain} (status: {response.status_code})")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Warning: Error fetching robots.txt for {domain}: {e}")
            return None
        except Exception as e:
            print(f"Warning: Error parsing robots.txt for {domain}: {e}")
            return None
    
    def _create_empty_robots(self, robots_url: str) -> RobotFileParser:
        """
        Create an empty robots.txt parser (allows everything).
        
        Args:
            robots_url: Robots.txt URL
            
        Returns:
            RobotFileParser that allows all access
        """
        rp = RobotFileParser()
        rp.set_url(robots_url)
        # Empty robots.txt allows everything
        return rp
    
    def _get_cached_robots(self, domain: str) -> Optional[RobotFileParser]:
        """
        Get robots.txt from cache if still valid.
        
        Args:
            domain: Domain name
            
        Returns:
            Cached RobotFileParser or None if not cached or expired
        """
        if domain in self.robots_cache:
            rp, timestamp = self.robots_cache[domain]
            if time.time() - timestamp < self.cache_timeout:
                return rp
            else:
                # Remove expired entry
                del self.robots_cache[domain]
        return None
    
    def can_crawl(self, domain: str, path: str) -> bool:
        """
        Check if a path can be crawled based on robots.txt.
        
        Args:
            domain: Domain name (e.g., 'example.com')
            path: URL path to check (e.g., '/products/item123')
            
        Returns:
            True if crawling is allowed, False otherwise
        """
        # First check cache
        rp = self._get_cached_robots(domain)
        
        # If not in cache, fetch and cache
        if rp is None:
            rp = self._fetch_robots(domain)
            if rp is not None:
                self.robots_cache[domain] = (rp, time.time())
            else:
                # If we can't get robots.txt, be conservative and disallow
                return False
        
        # Construct full URL for checking
        if not path.startswith('/'):
            path = '/' + path
        full_url = f"https://{domain}{path}"
        
        # Check if allowed for our user agent
        return rp.can_fetch(self.user_agent, full_url)
    
    def get_crawl_delay(self, domain: str) -> Optional[float]:
        """
        Get the crawl delay specified in robots.txt.
        
        Args:
            domain: Domain name
            
        Returns:
            Crawl delay in seconds or None if not specified
        """
        rp = self._get_cached_robots(domain)
        if rp is None:
            rp = self._fetch_robots(domain)
            if rp is not None:
                self.robots_cache[domain] = (rp, time.time())
        
        if rp is not None:
            delay = rp.crawl_delay(self.user_agent)
            return float(delay) if delay is not None else None
        return None
    
    def get_request_rate(self, domain: str) -> Optional[Tuple[int, int]]:
        """
        Get the request rate specified in robots.txt.
        
        Args:
            domain: Domain name
            
        Returns:
            Tuple of (requests, seconds) or None if not specified
        """
        rp = self._get_cached_robots(domain)
        if rp is None:
            rp = self._fetch_robots(domain)
            if rp is not None:
                self.robots_cache[domain] = (rp, time.time())
        
        if rp is not None:
            rate = rp.request_rate(self.user_agent)
            return rate if rate is not None else None
        return None


# Module-level convenience functions
_default_checker = RobotsChecker()

def can_crawl(domain: str, path: str) -> bool:
    """
    Convenience function to check if a path can be crawled.
    
    Args:
        domain: Domain name
        path: URL path to check
        
    Returns:
        True if crawling is allowed, False otherwise
    """
    return _default_checker.can_crawl(domain, path)


def get_crawl_delay(domain: str) -> Optional[float]:
    """
    Convenience function to get crawl delay for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        Crawl delay in seconds or None if not specified
    """
    return _default_checker.get_crawl_delay(domain)


def check_domain_compliance(domain: str) -> Dict[str, any]:
    """
    Get comprehensive compliance information for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        Dictionary with compliance information
    """
    result = {
        'domain': domain,
        'robots_url': _default_checker._get_robots_url(domain),
        'sitemap_allowed': can_crawl(domain, '/sitemap.xml'),
        'product_paths_allowed': {},
        'crawl_delay': get_crawl_delay(domain),
        'request_rate': _default_checker.get_request_rate(domain)
    }
    
    # Check common product page paths
    test_paths = [
        '/products/',
        '/product/',
        '/catalog/',
        '/item/',
        '/shop/',
        '/store/',
        '/parts/',
        '/datasheet/'
    ]
    
    for path in test_paths:
        result['product_paths_allowed'][path] = can_crawl(domain, path)
    
    return result


if __name__ == "__main__":
    # Test the robots functionality
    print("=" * 60)
    print("TESTING ROBOTS MODULE")
    print("=" * 60)
    
    # Test domains with different robots.txt configurations
    test_domains = [
        'httpbin.org',  # Usually allows most things
        'github.com',   # Has robots.txt
        'nonexistentdomainfortesting123.com'  # Should fail gracefully
    ]
    
    print("\n1. Basic crawl permission tests:")
    for domain in test_domains[:2]:  # Skip the nonexistent one for basic test
        try:
            print(f"\nTesting {domain}:")
            
            # Test different paths
            test_paths = ['/robots.txt', '/', '/sitemap.xml', '/products/test']
            
            for path in test_paths:
                allowed = can_crawl(domain, path)
                print(f"  {path}: {'ALLOWED' if allowed else 'BLOCKED'}")
                
            # Test crawl delay
            delay = get_crawl_delay(domain)
            if delay:
                print(f"  Crawl delay: {delay}s")
            else:
                print(f"  Crawl delay: None specified")
                
        except Exception as e:
            print(f"  Error testing {domain}: {e}")
    
    print("\n2. Comprehensive compliance check:")
    if len(test_domains) >= 1:
        domain = test_domains[0]
        try:
            compliance = check_domain_compliance(domain)
            print(f"\nCompliance report for {domain}:")
            print(f"  Robots URL: {compliance['robots_url']}")
            print(f"  Sitemap allowed: {compliance['sitemap_allowed']}")
            print(f"  Crawl delay: {compliance['crawl_delay']}")
            print(f"  Product paths:")
            for path, allowed in compliance['product_paths_allowed'].items():
                print(f"    {path}: {'ALLOWED' if allowed else 'BLOCKED'}")
        except Exception as e:
            print(f"  Error in compliance check: {e}")
    
    print("\n3. Testing robots checker class:")
    try:
        checker = RobotsChecker(user_agent="test-bot/1.0")
        result = checker.can_crawl('httpbin.org', '/get')
        print(f"  Custom checker result: {'ALLOWED' if result else 'BLOCKED'}")
    except Exception as e:
        print(f"  Error with custom checker: {e}")