# google_search_sourcing_with_cost_cap.py
"""
Google Search → Candidate URLs → Rank by locality → Extract products
with HARD COST LIMITS per run + lightweight caching.

Env vars required:
  - GOOGLE_API_KEY
  - GOOGLE_CSE_ID

Dependencies:
  - requests
  - (optional) phonenumbers

Integration:
  from google_search_sourcing_with_cost_cap import search_and_extract_products

  products = search_and_extract_products(
      keyword_terms=["PETG", "clear plastic sheet", "2mm"],
      city="College Park",
      region="MD",
      country="US",
      max_products=8,
      # Cost guardrails (any one may be used; both can coexist):
      max_requests_per_run=10,         # hard cap on API requests
      max_dollars_per_run=0.05,        # ~10 queries at $5/1000
      # Search shaping:
      pages_per_query=1,
      per_page=10,
      pause=0.7,
      deny_domains=["amazon.com","walmart.com","ebay.com","pinterest.com"],
      extractor_kwargs={"delay": 0.8, "min_quality": 3}
  )
"""

import os
import re
import time
import html
import math
import json
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse

import requests

try:
    import phonenumbers  # optional; used for tiny area-code signal
except Exception:
    phonenumbers = None

# ---- import your existing extractor exactly as-is ----
try:
    # Your wrapper file from the prompt (it exposes extract_products_batch)
    from product_validation_wrapper import extract_products_batch
except ImportError:
    # Fallback to sibling import if packaged differently
    from .product_validation_wrapper import extract_products_batch  # type: ignore


# =========================
# ---- Cost management ----
# =========================

COST_PER_1000_QUERIES_USD = 5.00

class CostLimiter:
    """
    Track and enforce per-run API spend/requests.
    """
    def __init__(
        self,
        max_requests_per_run: Optional[int] = None,
        max_dollars_per_run: Optional[float] = None,
        cost_per_1000: float = COST_PER_1000_QUERIES_USD,
    ):
        self.max_requests = max_requests_per_run
        self.max_dollars = max_dollars_per_run
        self.cost_per_1000 = cost_per_1000
        self.request_count = 0

        # Precompute request cap from dollar budget, if supplied
        self._budget_req_cap = None
        if self.max_dollars is not None:
            # requests_allowed = floor( max_dollars / (cost_per_1000/1000) )
            self._budget_req_cap = int(math.floor(self.max_dollars / (self.cost_per_1000 / 1000.0)))

    def _active_cap(self) -> Optional[int]:
        caps = [c for c in [self.max_requests, self._budget_req_cap] if c is not None]
        return min(caps) if caps else None

    def allow_another(self) -> bool:
        cap = self._active_cap()
        if cap is None:
            return True
        return self.request_count < cap

    def record(self) -> None:
        self.request_count += 1

    def estimated_cost(self) -> float:
        return (self.request_count * self.cost_per_1000) / 1000.0

    def remaining_requests(self) -> Optional[int]:
        cap = self._active_cap()
        if cap is None:
            return None
        return max(0, cap - self.request_count)

    def summary_str(self) -> str:
        cap = self._active_cap()
        s = f"[COST] Requests used: {self.request_count}"
        if cap is not None:
            s += f" / cap {cap}"
        s += f" | Est. cost this run: ${self.estimated_cost():.4f}"
        if self._budget_req_cap is not None:
            s += f" | Budget: ${self.max_dollars:.2f}"
        return s


# ============================
# ---- Search & Scoring ------
# ============================

def _get_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

def _norm(s: str) -> str:
    return (s or "").strip()

def build_queries(
    keyword_terms: List[str],
    city: str,
    region: Optional[str] = None,
    country: Optional[str] = None,
) -> List[str]:
    """
    Build multiple intent- and location-aware queries to improve recall while keeping them compact.
    """
    kw = " ".join(keyword_terms)
    loc_full = " ".join([p for p in [city, region, country] if p])

    intents = [
        "buy", "price", "catalog", "datasheet", "SKU", "MPN", "specifications",
        "inurl:product", "inurl:catalog", "site:*/product", "site:*/shop"
    ]
    queries = [f'{kw} "{loc_full}" {intent}' for intent in intents]
    queries += [
        f'{kw} "{city}" {region or ""} price',
        f'{kw} "{city}" {region or ""} supplier',
        f'{kw} near "{city} {region or ""}"',
        f'{kw} distributor "{loc_full}"',
    ]
    seen = set()
    out = []
    for q in queries:
        q = " ".join(q.split())
        if q not in seen:
            out.append(q)
            seen.add(q)
    return out

# Lightweight in-process cache to avoid duplicate billable calls in the same run
# Key: (q, start, num, gl, cr)
_SEARCH_CACHE: Dict[Tuple[str, int, int, Optional[str], Optional[str]], Dict] = {}

def google_search_raw(
    q: str,
    api_key: str,
    cse_id: str,
    *,
    gl: Optional[str] = None,
    cr: Optional[str] = None,
    num: int = 10,
    start: int = 1,
    timeout: float = 20.0,
) -> Dict:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": q,
        "num": max(1, min(num, 10)),
        "start": max(1, start),
        "safe": "off",
    }
    if gl:
        params["gl"] = gl.lower()
    if cr:
        params["cr"] = cr

    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def google_search_capped(
    q: str,
    api_key: str,
    cse_id: str,
    *,
    cost: CostLimiter,
    gl: Optional[str] = None,
    cr: Optional[str] = None,
    num: int = 10,
    start: int = 1,
    timeout: float = 20.0,
    use_cache: bool = True,
) -> Dict:
    """
    Wrapper that enforces per-run limits and caches identical calls.
    """
    cache_key = (q, start, max(1, min(num, 10)), gl, cr)
    if use_cache and cache_key in _SEARCH_CACHE:
        return _SEARCH_CACHE[cache_key]

    if not cost.allow_another():
        logging.warning("[COST] Query skipped due to cap: %s (start=%d)", q, start)
        return {"items": []}

    data = google_search_raw(q, api_key, cse_id, gl=gl, cr=cr, num=num, start=start, timeout=timeout)
    cost.record()
    if use_cache:
        _SEARCH_CACHE[cache_key] = data
    return data

def _contains_city_or_region(text: str, city: str, region: Optional[str]) -> int:
    score = 0
    t = text.lower()
    if city and city.lower() in t:
        score += 3
    if region and region.lower() in t:
        score += 2
    return score

def _area_code_score(text: str) -> int:
    if not phonenumbers:
        return 0
    score = 0
    for m in re.finditer(r"(\+?1[\s\-\.]?)?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}", text):
        try:
            num = phonenumbers.parse(m.group(), "US")
            if phonenumbers.is_possible_number(num) and phonenumbers.region_code_for_number(num) == "US":
                score += 1
        except Exception:
            pass
    return min(score, 2)

def _domain_is_local(url: str, city: str, region: Optional[str]) -> int:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return 0
    score = 0
    tokens = re.split(r"[.\-]", host)
    if city and city.lower() in tokens:
        score += 2
    if region and region.lower() in tokens:
        score += 1
    return score

def location_score(title: str, snippet: str, url: str, city: str, region: Optional[str]) -> Tuple[int, List[str]]:
    reasons = []
    score = 0

    s1 = _contains_city_or_region(title, city, region)
    if s1:
        score += s1
        reasons.append(f"title_city_region+{s1}")

    s2 = _contains_city_or_region(snippet, city, region)
    if s2:
        score += s2
        reasons.append(f"snippet_city_region+{s2}")

    s3 = _domain_is_local(url, city, region)
    if s3:
        score += s3
        reasons.append(f"domain_local+{s3}")

    s4 = _area_code_score(" ".join([title, snippet]))
    if s4:
        score += s4
        reasons.append(f"area_code+{s4}")

    return score, reasons

SCRAPABLE_HINT_RE = re.compile(
    r"\b(product|catalog|shop|sku|mpn|price|add to cart|add-to-cart|datasheet|specifications|part number)\b",
    re.IGNORECASE
)

PATH_HINT_RE = re.compile(r"/(product|products|item|sku|part|shop|store)/", re.IGNORECASE)

def looks_scrapable(url: str, title: str, snippet: str) -> bool:
    # Avoid typical non-scrapable or non-product content
    if url.lower().endswith((".pdf", ".doc", ".ppt", ".zip")):
        return False
    text = f"{title} {snippet}"
    if SCRAPABLE_HINT_RE.search(text):
        return True
    if PATH_HINT_RE.search(url):
        return True
    # modest fallback: shorter URLs that aren't homepages
    try:
        path = urlparse(url).path or ""
    except Exception:
        path = ""
    return path not in ("", "/")

DEFAULT_DENY = {
    "amazon.com", "www.amazon.com", "smile.amazon.com",
    "walmart.com", "www.walmart.com",
    "ebay.com", "www.ebay.com",
    "pinterest.com", "www.pinterest.com",
    "facebook.com", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "youtube.com", "www.youtube.com",
    "linkedin.com", "www.linkedin.com"
}

def search_candidates(
    keyword_terms: List[str],
    city: str,
    region: Optional[str] = None,
    country: Optional[str] = None,
    *,
    pages_per_query: int = 1,
    per_page: int = 10,
    pause: float = 0.6,
    allow_domains: Optional[List[str]] = None,
    deny_domains: Optional[List[str]] = None,
    max_requests_per_run: Optional[int] = None,
    max_dollars_per_run: Optional[float] = None,
) -> Tuple[List[Dict], CostLimiter]:
    """
    Run multiple query variants, gather result items, attach location/scrapability scores, and rank.
    Enforces per-run request/cost caps.
    """
    api_key = _get_env("GOOGLE_API_KEY")
    cse_id  = _get_env("GOOGLE_CSE_ID")

    cost = CostLimiter(
        max_requests_per_run=max_requests_per_run,
        max_dollars_per_run=max_dollars_per_run,
        cost_per_1000=COST_PER_1000_QUERIES_USD,
    )

    gl = (country or "US").lower()
    cr = f"country{country.upper()}" if country else None

    allow_set = set([d.lower() for d in (allow_domains or [])])
    deny_set  = DEFAULT_DENY.union(set([d.lower() for d in (deny_domains or [])]))

    queries = build_queries(keyword_terms, city, region, country)
    seen_urls = set()
    items: List[Dict] = []

    for q in queries:
        for page in range(pages_per_query):
            start = 1 + page * per_page
            if not cost.allow_another():
                logging.warning("[COST] Cap reached before calling query: %s (start=%d)", q, start)
                break

            try:
                data = google_search_capped(
                    q, api_key, cse_id, cost=cost, gl=gl, cr=cr,
                    num=per_page, start=start, timeout=20.0, use_cache=True
                )
            except requests.HTTPError as e:
                logging.warning(f"[HTTP] Search error: {e}")
                break
            except Exception as e:
                logging.warning(f"[ERR] Search error: {e}")
                break

            for it in data.get("items", []):
                url = it.get("link") or it.get("formattedUrl")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                host = urlparse(url).netloc.lower()
                if allow_set and host not in allow_set:
                    continue
                if host in deny_set:
                    continue

                title = html.unescape(_norm(it.get("title", "")))
                snippet = html.unescape(_norm(it.get("snippet", "")))

                # Scrapability & commerce hints
                scrapable = looks_scrapable(url, title, snippet)
                commerce_hit = bool(SCRAPABLE_HINT_RE.search(f"{title} {snippet}"))

                # Locality
                loc_score, reasons = location_score(title, snippet, url, city, region)

                # Base scoring
                base = 5 if commerce_hit else 0
                scrap_bonus = 3 if scrapable else 0
                total_score = base + loc_score + scrap_bonus

                items.append({
                    "url": url,
                    "title": title,
                    "snippet": snippet,
                    "score": total_score,
                    "reasons": reasons + (["scrapable+3"] if scrapable else []),
                    "commerce": commerce_hit,
                    "query": q,
                })

            # polite pacing (also helps avoid quota spikes)
            time.sleep(pause)

    # Rank by score desc, then commerce, then shorter URL
    items.sort(key=lambda d: (-d["score"], -(1 if d["commerce"] else 0), len(d["url"])))

    print(cost.summary_str())
    return items, cost


# =========================================
# ---- High-level: search → extract --------
# =========================================

def search_and_extract_products(
    keyword_terms: List[str],
    city: str,
    region: Optional[str] = None,
    country: Optional[str] = None,
    *,
    max_products: int = 10,
    pages_per_query: int = 1,
    per_page: int = 10,
    pause: float = 0.6,
    allow_domains: Optional[List[str]] = None,
    deny_domains: Optional[List[str]] = None,
    extractor_kwargs: Optional[Dict] = None,
    # Cost guardrails (choose either or both):
    max_requests_per_run: Optional[int] = None,
    max_dollars_per_run: Optional[float] = None,
) -> List[Dict]:
    """
    Orchestrates search (with cost limits) and hands top candidates to your extractor.
    """
    extractor_kwargs = extractor_kwargs or {}

    candidates, cost = search_candidates(
        keyword_terms=keyword_terms,
        city=city,
        region=region,
        country=country,
        pages_per_query=pages_per_query,
        per_page=per_page,
        pause=pause,
        allow_domains=allow_domains,
        deny_domains=deny_domains,
        max_requests_per_run=max_requests_per_run,
        max_dollars_per_run=max_dollars_per_run,
    )

    # Oversample to offset extraction failures
    oversample = max_products * 3
    urls = [{"url": c["url"], "score": c["score"], "reasons": c["reasons"]} for c in candidates[:oversample]]

    print(f"[Search] Selected {len(urls)} candidate URLs (top {oversample})")
    for i, u in enumerate(urls[:20], 1):
        print(f"  {i:02d}. {u['url']}  [score={u['score']}, reasons={','.join(u['reasons'])}]")

    # Hand off to your improved batch extractor (unchanged)
    products = extract_products_batch(
        urls=urls,
        keyword_terms=extractor_kwargs.get("keyword_terms", keyword_terms),
        max_products=max_products,
        min_quality=extractor_kwargs.get("min_quality", 3),
        delay=extractor_kwargs.get("delay", 0.8),
    )

    # Final cost summary
    print("[RESULT] Products:", len(products))
    print("[RESULT] " + CostLimiter(max_requests_per_run, max_dollars_per_run).summary_str().split("|")[0] \
          + f" | Actual used: {len(_SEARCH_CACHE)} cached calls; billable: {cost.request_count}; Est. cost: ${cost.estimated_cost():.4f}")

    return products


# ======================
# ---- Quick test ------
# ======================

if __name__ == "__main__":
    # Minimal smoke test (won't actually run without API key + extractor)
    os.environ.setdefault("GOOGLE_API_KEY", "REPLACE_ME")
    os.environ.setdefault("GOOGLE_CSE_ID", "REPLACE_ME")

    try:
        res = search_and_extract_products(
            keyword_terms=["PETG", "clear plastic sheet", "2mm"],
            city="College Park",
            region="MD",
            country="US",
            max_products=3,
            pages_per_query=1,
            per_page=5,
            pause=0.8,
            # Cost guardrails: pick ONE or BOTH
            max_requests_per_run=10,
            max_dollars_per_run=0.05,  # ~10 requests
            deny_domains=["amazon.com","walmart.com","ebay.com","pinterest.com"],
            extractor_kwargs={"min_quality": 3, "delay": 0.5},
        )
        print(json.dumps(res, indent=2)[:2000] + " ...")
    except RuntimeError as e:
        print("Config error:", e)
