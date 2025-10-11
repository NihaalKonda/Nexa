# contexgt — Code‑First MVP Pipeline

A modular, compliant pipeline that turns a **keyword** → **suppliers** → **products** (with specs) using open/low‑cost discovery and by crawling **suppliers’ own sites** only when permitted.

> Goal: Ship a working procurement discovery MVP with structured **product** results (name, SKU, specs, datasheet, certs), not just supplier lists—without scraping prohibited directories.

---

## Design Goals
- **Compliant**: Respect robots.txt and site Terms; avoid marketplace/directory scraping.
- **Product‑centric**: Extract SKUs/specs/certifications/datasheets from supplier product pages.
- **Modular**: Swap seed sources, add normalizers, change stores easily.
- **Cheap**: Small daily crawl caps, caching, and free‑tier friendly.

---

## End‑to‑End Flow
```
[Keyword] → [Synonym expansion + HS/NAICS hints]
        → [Supplier seeds (Open Supply Hub / SAM.gov / your CSV)]
        → [Domains] → [robots.txt OK?]
        → [Sitemap discovery] → [Product‑ish URLs]
        → [Extract name/SKU/specs/certs/datasheets]
        → [Normalize specs → canonical keys/units]
        → [Score (relevance + freshness)]
        → [Store (JSON/CSV, optional DB)]
```

---

## Repository Layout
```
contexgt/
  src/
    main.py              # CLI / orchestrator
    keywords.py          # keyword expansion (synonyms)
    discovery_seed.py    # seed suppliers from CSV or stubs
    robots.py            # robots.txt checks
    sitemap.py           # sitemap discovery for product URLs
    product_extract.py   # parse product pages (name/SKU/specs/certs/pdf)
    specs_normalize.py   # unit normalization → canonical keys
    scorer.py            # relevance + freshness scoring
    store.py             # save/load JSON/CSV
  data/
    suppliers.json       # output of seeding
    products.json        # extracted products
    products.csv         # flattened for spreadsheets/BI
```

---

## Web Data Acquisition Tools

The pipeline uses several Python libraries for compliant web data extraction:

### **HTTP Requests & HTML Parsing**
- **`requests`** - HTTP client with timeout, headers, and error handling
- **`BeautifulSoup4`** - HTML/XML parsing for product page extraction
- **`urllib.robotparser`** - Built-in robots.txt compliance checking
- **`tldextract`** - Domain normalization and extraction

### **Data Processing & Normalization**  
- **`pint`** - Unit conversion library for specifications (mm, °C, PSI, etc.)
- **`python-dateutil`** - Date/time parsing for freshness scoring
- **`re`** (regex) - Pattern matching for SKUs, certifications, specifications

### **Compliance & Politeness**
- **Robots.txt checking** - Every URL checked before crawling
- **Request delays** - Configurable delays between requests (default: 1.0s)
- **Sitemap discovery** - Uses XML sitemaps for efficient URL discovery
- **User-Agent headers** - Identifies as "contexgt-crawler/1.0"
- **Timeout handling** - 10-15s timeouts prevent hanging requests

### **Data Extraction Approach**
- **Sitemap-first discovery** - Reads `/sitemap.xml` to find product pages
- **Heuristic parsing** - Multiple fallback selectors for robust extraction
- **Structured data support** - Microdata, JSON-LD, and schema.org
- **PDF datasheet detection** - Finds technical specification documents
- **Keyword relevance filtering** - Only processes relevant product pages

---

## Components

### `keywords.py`
- Splits the user query and adds **lightweight synonyms** (e.g., “petg” → glycol‑modified, polyester, thermoformable) to improve product‑page recall.

### `discovery_seed.py`
- **`load_suppliers_from_csv()`**: Parses a CSV you control (e.g., OSH/SAM exports) and normalizes to `{name, domain, country, state}` with dedupe.
- **`stub_suppliers()`**: Minimal seed list for wiring the pipeline before real data.

### `robots.py`
- **`can_crawl(domain, path)`**: Robots‑aware gate to prevent fetching disallowed paths.

### `sitemap.py`
- **`discover_product_urls(domain, cap)`**: Reads `/sitemap.xml` (and nested indexes). Returns up to `cap` URLs that look like `/product|/products|/catalog|/item|/datasheet`.

### `product_extract.py`
- **`extract_product(url, keyword_terms)`**: Heuristics to build a **product object**:
  - `name` via `h1` / `itemprop=name` / `og:title`
  - `sku`/`mpn` via regex near `SKU|MPN|Part #|Item #`
  - `price_text` via currency regex (store exact text only)
  - `specs_raw` via first reasonable **label/value** table or definition list
  - `datasheet_url` from first `.pdf` link
  - `certifications` via regex (`ISO 9001|RoHS|REACH|CE|FDA|ITAR`)
  - `source_url`, `last_seen_at`
  - Simple **keyword gating** so only relevant product pages pass

### `specs_normalize.py`
- Converts messy page labels → **canonical keys** and normalizes units using a tiny map:
  - `thickness|gauge` → `thickness_mm`
  - `width|length` → `*_mm`
  - `temperature|max temp` → `max_temp_c`
- Stores both **raw** and **canonical** specs.

### `scorer.py`
- **Relevance**: matches of terms in `name` (3×) and in `specs_raw` text (1×)
- **Freshness**: optional bonuses if `Last‑Modified`/sitemap `<lastmod>` is recent; +2 if a datasheet link exists.

### `store.py`
- Save/load **JSON**; export **CSV** with flattened fields (`name`, `sku`, `datasheet_url`, canonical spec columns, etc.).

### `main.py` (CLI)
- Subcommands:
  - **`seed`**: load suppliers from CSV (or use stub) → `data/suppliers.json`
  - **`crawl`**: for each supplier (capped), check robots → discover sitemaps → extract up to N products → `data/products.{json,csv}`
  - **`run`**: seed + crawl in one go
- Flags:
  - `--keyword` (required for crawl/run)
  - `--max-domains`, `--max-pages`, `--delay` (crawl politeness)
  - CSV column remaps: `--name-col`, `--website-col`, `--country-col`, `--state-col`

---

## Data Model

### `suppliers`
- `supplier_id` (hash of name|domain)
- `name`, `domain`, `country`, `state`
- `sources` (e.g., ["SEED_CSV", "STUB"])
- `last_seen_at`

### `products`
- `product_id` (hash of domain|name|source_url)
- `supplier_id`
- `name`, `sku`, `price_text`
- `specs_raw` (JSON)
- `specs_canonical` (JSON; e.g., `thickness_mm`, `width_mm`, `length_mm`, `max_temp_c`)
- `certifications` (string[])
- `datasheet_url`, `source_url`
- `last_seen_at`, `score` (int)

---

## CSV Seed (expected columns)
- **Required**: `name`, `website`
- **Optional**: `country`, `state`
- Column names can be remapped via CLI flags.

Example rows:
```
name,website,country,state
Acme Plastics,https://www.acmeplastics.com,US,NJ
Precision Gaskets,https://precisiongaskets.example,US,OH
```

---

## Product Extraction Heuristics (MVP)
- Prefer **tables with label/value rows**; ignore decorative tables.
- Stop after the first table yielding ≥3 pairs (good signal of real specs).
- Regex for common certs and identifiers; keep **string matches exact** (no hallucinated data).
- Keep **`source_url`** and **`datasheet_url`** for evidence.

---

## Ranking & Freshness
- Name hits (3×), specs hits (1×) → base relevance.
- **Bonuses**: recent HTTP `Last‑Modified` / sitemap `<lastmod>`; datasheet present (+2).
- This is intentionally simple; extend with recency windows or shipment signals later.

---

## Politeness & Cost Controls
- Per run, cap to **N domains × M pages** (e.g., `50 × 10`).
- Delay between requests (e.g., `1.0s`); single session per origin.
- Cache ETag/Last‑Modified (extend later) to skip unchanged pages.
- Back off on 403/429 and log domain‑level outcomes.

---

## Compliance Notes
- Crawl **only suppliers’ own sites** and **only if robots.txt allows** the target paths.
- Do **not** automate marketplaces/directories unless you have written permission.
- Avoid login‑gated/paywalled content and PII harvesting.

---

## Quick Start

> **Prerequisites:** Activate your conda environment: `conda activate osh-testing-env`

### 🚀 **Simplest Usage** (Recommended)

The system comes pre-loaded with **59 suppliers** and automatically saves to `data/products.json` and `data/products.csv`:

```bash
python -m src.main run --keyword "plastic sheet"
```

That's it! This will:
- Use existing 59 suppliers (no setup needed)
- Crawl for products matching "plastic sheet"
- Save results to `data/products.json` and `data/products.csv`

### 🎯 **Common Search Examples**

```bash
# Plastic materials
python -m src.main run --keyword "plastic sheet"
python -m src.main run --keyword "polymer plate"

# Industrial components
python -m src.main run --keyword "gasket material"
python -m src.main run --keyword "industrial tubing"

# Broader searches (more results)
python -m src.main run --keyword "material"
python -m src.main run --keyword "product"
```

### ⚙️ **Advanced Options**

**Scale up the search:**
```bash
python -m src.main run --keyword "plastic sheet" --max-domains 25 --max-pages 10
```

**Faster crawling:**
```bash
python -m src.main run --keyword "plastic sheet" --delay 0.5
```

**Custom output files:**
```bash
python -m src.main run --keyword "plastic sheet" --products-json my_results.json
```

### 📋 **Key Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--keyword` | *required* | Search term (e.g., "plastic sheet", "gasket") |
| `--max-domains` | 10 | How many supplier websites to crawl |
| `--max-pages` | 5 | How many pages per website |
| `--delay` | 1.0 | Seconds between requests (be polite!) |

### 📊 **Current System Status**

- **59 suppliers** pre-loaded and ready
- **16+ crawlable suppliers** (others blocked by robots.txt)
- **NLTK-powered** keyword expansion (automatically finds synonyms)
- **Smart filtering** (15% relevance threshold, 2+ term minimum)
- **Auto-saves** to `data/products.json` and `data/products.csv`

### 🔧 **Troubleshooting**

**Getting few results?**
- Use broader keywords: `"material"` instead of `"PETG sheet 2mm ISO 9001"`
- Increase domains: `--max-domains 25`
- Many suppliers block crawlers (this is normal)

**Want more suppliers?**
- Add them manually to `data/suppliers.json`
- Use format: `{"name": "...", "domain": "...", "country": "US", "state": "..."}`

### 💡 **Advanced Usage**

```bash
# Full command structure
python -m src.main run \
  --keyword "search term" \
  --max-domains 25 \
  --max-pages 10 \
  --delay 0.5 \
  --products-json custom_output.json
```

---

## Extending the MVP
- **Spec parsing**: add per‑vertical mappers; improve table detection and `dl` parsing.
- **PDFs**: add a pdf extraction stage for datasheets (e.g., `pdfplumber`).
- **Search**: move from JSON to SQLite/Postgres; index `name/sku/specs` and numeric spec ranges.
- **Freshness**: read HTTP headers and sitemaps to compute a normalized 0–100 freshness score.
- **ETL**: add a lightweight scheduler (GitHub Actions or your preferred cron) and write metrics summaries.

---

## Disclaimer
This pipeline is for demonstration. You are responsible for ensuring your use complies with applicable Terms, robots.txt directives, and data‑privacy laws in your jurisdiction.

