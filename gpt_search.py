#!/usr/bin/env python3
"""
Product price finder using an **open‑source LLM via Ollama**.

• Input: one string of keywords (e.g., "aluminum sheet 6061 0.125 24x36")
• The script will: build site‑specific search URLs → collect likely product links →
  fetch those pages → ask an OSS model to extract price & details → print a table
  and save JSON.

Quick start
-----------
1) Conda env (optional but recommended):
    conda create -n alu-oss python=3.11 -y && conda activate alu-oss

2) Install deps:
    pip install requests beautifulsoup4 python-dateutil
    # If you need JS rendering for some sites:
    pip install playwright && playwright install chromium

3) Run an OSS LLM locally with Ollama (separate terminal):
    # mac: brew install ollama; then
    ollama serve
    ollama pull qwen2.5:7b   # or llama3.1 / mistral:7b / any GGUF via hf.co/...

4) Execute:
    export OLLAMA_MODEL=qwen2.5:7b    # or your model name/ref
    # export OLLAMA_URL=http://localhost:11434/api/chat   # default is fine

    python product_price_finder_oss.py "aluminum sheet 6061 0.125 24x36"

Notes
-----
• The script prefers static HTML via requests; enable Playwright with --playwright
  if search pages or product pages are JS‑rendered.
• It currently targets several vendors with simple search URL patterns; extend SITE_CONFIG
  to add more sources easily.
• Results saved to prices_search.json
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

# Optional Playwright support is loaded lazily
HAVE_PLAYWRIGHT = False
try:
    import importlib.util as _ilus
    HAVE_PLAYWRIGHT = _ilus.find_spec("playwright") is not None
except Exception:
    HAVE_PLAYWRIGHT = False

DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", os.environ.get("MODEL", "qwen2.5:7b"))
TIMEOUT = int(os.environ.get("SCRAPER_TIMEOUT", 30))
USER_AGENT = os.environ.get("SCRAPER_UA", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

HEADERS = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}

@dataclass
class Site:
    name: str
    base: str
    search_path: str                 # format string or lambda; will insert query
    result_link_selector: str        # CSS selector for result anchors
    allow_domains: Tuple[str, ...]   # domains to keep when collecting links


def _sp(q: str) -> str:
    # simple encoder for spaces to '+' (works for many sites)
    return "+".join(q.split())

# --- Configure sites here ---
SITE_CONFIG: List[Site] = [
    Site(
        name="OnlineMetals",
        base="https://www.onlinemetals.com",
        search_path="/en/search?q={q}",
        result_link_selector="a.om-product-card__link, a[href*='/en/buy/']",
        allow_domains=("www.onlinemetals.com", "onlinemetals.com"),
    ),
    Site(
        name="BuyMetal",
        base="https://buymetal.com",
        search_path="/search?q={q}",
        result_link_selector="a.product-item-link, a[href*='/aluminum/']",
        allow_domains=("buymetal.com",),
    ),
    Site(
        name="McMaster",
        base="https://www.mcmaster.com",
        search_path="/search/Results.aspx?FT={q}",
        result_link_selector="a#FirstResultLink, a.SearchResultsLink",
        allow_domains=("www.mcmaster.com", "mcmaster.com"),
    ),
    Site(
        name="MetalSupermarkets",
        base="https://www.metalsupermarkets.com",
        search_path="/search/?q={q}",
        result_link_selector="a.card-title, a[href*='/product/']",
        allow_domains=("www.metalsupermarkets.com", "metalsupermarkets.com"),
    ),
    Site(
        name="HomeDepot",
        base="https://www.homedepot.com",
        search_path="/s/{q}",
        result_link_selector="a[href*='/p/'], a[href*='/p/'] .product-header__title",
        allow_domains=("www.homedepot.com", "homedepot.com"),
    ),
]


# ---------------- HTTP helpers ----------------

def get(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def get_dynamic(url: str) -> str:
    if not HAVE_PLAYWRIGHT:
        raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install chromium")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(TIMEOUT * 1000)
        page.goto(url)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
        return html


def html_to_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


# ---------------- Search & collect product links ----------------

def build_search_url(site: Site, query: str) -> str:
    return site.base + site.search_path.format(q=_sp(query))


def same_domain(url: str, allow_domains: Tuple[str, ...]) -> bool:
    from urllib.parse import urlparse
    host = urlparse(url).netloc.lower()
    return any(host.endswith(d) for d in allow_domains)


def absolutize(base: str, href: str) -> str:
    from urllib.parse import urljoin
    return urljoin(base, href)


def collect_product_links(site: Site, query: str, use_playwright: bool, max_links: int) -> List[str]:
    url = build_search_url(site, query)
    try:
        html = get(url) if not use_playwright else get_dynamic(url)
    except Exception:
        return []
    soup = html_to_soup(html)

    links: List[str] = []
    for a in soup.select(site.result_link_selector):
        href = a.get("href")
        if not href:
            continue
        abs_url = absolutize(site.base, href)
        if not same_domain(abs_url, site.allow_domains):
            continue
        # heuristic filter to prefer aluminum sheet pages
        txt = (a.get_text(strip=True) or "").lower()
        if "aluminum" in txt and ("sheet" in txt or "plate" in txt) or \
           ("aluminum" in abs_url and ("sheet" in abs_url or "plate" in abs_url)):
            links.append(abs_url)
        if len(links) >= max_links:
            break
    return list(dict.fromkeys(links))  # dedupe while preserving order


# ---------------- LLM extraction via Ollama ----------------
SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": {"type": "string"},
        "product": {"type": "string"},
        "alloy": {"type": "string"},
        "temper": {"type": "string"},
        "thickness_in": {"type": "number"},
        "size": {"type": "string"},
        "price_usd": {"type": "number"},
        "unit": {"type": "string"},
        "min_qty": {"type": "number"},
        "currency": {"type": "string"},
        "url": {"type": "string"},
        "timestamp_iso": {"type": "string"},
        "raw_price_text": {"type": "string"}
    },
    "required": ["vendor", "product", "price_usd", "url", "timestamp_iso"],
}

SYSTEM = (
    "You extract aluminum product pricing from provided page text. "
    "Return STRICT JSON ONLY (no prose). Follow this JSON schema. "
    "If multiple variants exist, pick a common single‑unit price. Normalize thickness to inches."
)


PRICE_RE = re.compile(r"\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]+(?:\.[0-9]{2}))")


def call_ollama_extract(page_text: str, url: str, model: str, ollama_url: str) -> Dict:
    now = datetime.now(timezone.utc).isoformat()
    chunk = page_text[:14000]
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": (
                    "Extract one aluminum sheet/plate price from this page into the JSON schema.\n"
                    f"SCHEMA: {json.dumps(SCHEMA)}\n"
                    f"PAGE_URL: {url}\nCRAWLED_AT: {now}\n"
                    f"TEXT BEGIN\n{chunk}\nTEXT END\n"
                    "Return ONLY JSON."
                ),
            },
        ],
        "stream": False,
        "options": {"temperature": 0}
    }
    r = requests.post(ollama_url, json=payload, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    content = (data.get("message", {}) or {}).get("content", "{}").strip()

    # Extract JSON object from response
    m = re.search(r"\{[\s\S]*\}\s*$", content)
    s = m.group(0) if m else content
    try:
        out = json.loads(s)
    except json.JSONDecodeError:
        # try first {...}
        cand = re.findall(r"\{[\s\S]*?\}", content)
        out = json.loads(cand[0]) if cand else {}

    out.setdefault("url", url)
    out.setdefault("timestamp_iso", now)
    out.setdefault("currency", "USD")

    # price fallback via regex
    if not isinstance(out.get("price_usd"), (int, float)):
        m = PRICE_RE.search(content)
        if m:
            try:
                out["price_usd"] = float(m.group(1).replace(",", ""))
            except Exception:
                pass

    # thickness normalization: strings like '1/8 in'
    if isinstance(out.get("thickness_in"), str):
        out["thickness_in"] = frac_in_to_float(out["thickness_in"]) or None

    return out


def frac_in_to_float(s: str) -> Optional[float]:
    s = s.lower().replace('inch', '').replace('inches', '').replace('in.', '').replace('in', '').replace('"', '').strip()
    try:
        if "/" in s:
            n, d = s.split("/", 1)
            return float(n) / float(d)
        return float(s)
    except Exception:
        return None


# ---------------- Main flow ----------------

def fetch_text(url: str, use_playwright: bool) -> str:
    try:
        html = get(url)
    except Exception as e:
        return f"FETCH_ERROR: {e}"
    # try simple text; if too small and playwright requested, re-render
    txt = simplify_html_to_text(html)
    if use_playwright and len(txt) < 400 and HAVE_PLAYWRIGHT:
        try:
            html = get_dynamic(url)
            txt = simplify_html_to_text(html)
        except Exception as e:
            return f"FETCH_ERROR_DYNAMIC: {e}"
    return txt


def simplify_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    return " ".join(soup.get_text(" ", strip=True).split())


def run(query: str, sites: List[str], max_links: int, use_playwright: bool, model: str, ollama_url: str) -> List[Dict]:
    site_objs = [s for s in SITE_CONFIG if s.name.lower() in {x.lower() for x in sites}] if sites else SITE_CONFIG

    results: List[Dict] = []
    for site in site_objs:
        print(f"\n=== {site.name} search ===")
        links = collect_product_links(site, query, use_playwright, max_links)
        if not links:
            print("(no candidate links found)")
            continue
        for link in links:
            print(f"→ {link}")
            txt = fetch_text(link, use_playwright)
            if txt.startswith("FETCH_ERROR"):
                results.append({"vendor": site.name, "product": "", "price_usd": None, "url": link, "timestamp_iso": datetime.now(timezone.utc).isoformat(), "error": txt})
                continue
            try:
                data = call_ollama_extract(txt, link, model=model, ollama_url=ollama_url)
                # if vendor empty, default to site name
                if not data.get("vendor"):
                    data["vendor"] = site.name
                results.append(data)
                print(f"✓ {data.get('vendor','')} — {data.get('product','')[:70]} — ${data.get('price_usd')}")
            except Exception as e:
                results.append({"vendor": site.name, "product": "", "price_usd": None, "url": link, "timestamp_iso": datetime.now(timezone.utc).isoformat(), "error": f"EXTRACT_ERROR: {e}"})
            time.sleep(0.7)
    return results


def print_table(rows: List[Dict]):
    if not rows:
        print("No results.")
        return
    cols = ["vendor", "product", "alloy", "thickness_in", "size", "price_usd", "unit", "url"]
    widths = {c: max(len(c), *(len(str(r.get(c, ''))) for r in rows)) for c in cols}
    line = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print("\n" + line)
    print(sep)
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def main():
    ap = argparse.ArgumentParser(description="Find aluminum product prices using an OSS LLM via Ollama.")
    ap.add_argument("query", type=str, help="Keyword string, e.g. 'aluminum sheet 6061 0.125 24x36'")
    ap.add_argument("--sites", nargs="*", default=[], help="Subset of sites to search (names: OnlineMetals BuyMetal McMaster MetalSupermarkets HomeDepot)")
    ap.add_argument("--max-links", type=int, default=4, help="Max product links per site to visit")
    ap.add_argument("--playwright", action="store_true", help="Use Playwright for JS-heavy pages")
    ap.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Ollama model name/ref (env OLLAMA_MODEL)")
    ap.add_argument("--ollama-url", type=str, default=DEFAULT_OLLAMA_URL, help="Ollama chat endpoint URL")
    args = ap.parse_args()

    if args.playwright and not HAVE_PLAYWRIGHT:
        print("[warn] --playwright requested but Playwright not installed. Install it first.")

    results = run(
        query=args.query,
        sites=args.sites,
        max_links=args.max_links,
        use_playwright=args.playwright,
        model=args.model,
        ollama_url=args.ollama_url,
    )
    with open("prices_search.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nSaved -> prices_search.json")
    print_table(results)


if __name__ == "__main__":
    main()
