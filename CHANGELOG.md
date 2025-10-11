# Changelog

## [2.0.0] - 2025-10-11

### Added
- **Location-Based Supplier Discovery**: New `fetch_suppliers_smart.py` module that uses Google Places API with intelligent keyword-to-place-type mapping
- **Consolidated Pipeline**: New `pipeline.py` that combines location discovery with existing product extraction pipeline
- **Comprehensive Documentation**:
  - `README.md` - Main project documentation
  - `QUICKSTART.md` - Quick reference guide
  - `README_PIPELINE.md` - Detailed pipeline documentation
- **Smart Keyword Optimization**: Automatic mapping of search keywords to relevant Google Place types (30+ mappings)

### Changed
- Updated `.gitignore` to exclude test files and results directories
- Archived original README as `ARCHIVE_original_readme.md`
- Improved environment setup with complete `environment.yml`

### Removed
- **Cleaned up redundant files**:
  - `combine_suppliers.py` (legacy utility)
  - `fetch_suppliers.py` (superseded by `fetch_suppliers_smart.py`)
  - `osh-sourcing.py` (empty legacy file)
  - `test_discovery_seed.py` (test file)
  - `test_keywords.py` (test file)
  - `app.py` (empty file)
- **Removed test data**:
  - `data/test_pipeline/`
  - `data/test_*.json`
  - `data/suppliers_places*.json`
  - All other temporary test outputs
- **Removed cache files**:
  - `__pycache__/`
  - `.DS_Store`
  - `test/` directory

### Technical Details

#### New Architecture
```
Pipeline Flow:
1. Fetch suppliers from location (Google Places API)
2. Expand search keywords
3. Discover product URLs (sitemaps)
4. Extract product data
5. Normalize specifications
6. Score by relevance
7. Generate reports
```

#### API Integration
- Google Places API with optimized search strategy
- Text Search API for location-based queries
- Place Details API for company information
- Intelligent place type filtering based on keywords

#### File Structure (Clean)
```
Nexa/
├── pipeline.py                    # Main pipeline (NEW)
├── fetch_suppliers_smart.py       # Smart discovery (NEW)
├── environment.yml
├── requirements.txt
├── README.md                      # New main README
├── QUICKSTART.md                  # Quick reference (NEW)
├── README_PIPELINE.md             # Detailed docs (NEW)
├── ARCHIVE_original_readme.md     # Original design doc
├── src/                          # Core modules (existing)
│   ├── main.py
│   ├── keywords.py
│   ├── discovery_seed.py
│   ├── sitemap.py
│   ├── product_extract.py
│   ├── specs_normalize.py
│   ├── scorer.py
│   └── store.py
└── data/                         # Data directory (cleaned)
    ├── suppliers.json            # Production suppliers
    ├── products.json             # Production products
    └── products_summary.json     # Production summary
```

## [1.0.0] - 2025-09-30

### Initial Release
- Basic keyword-based supplier discovery
- Product extraction from supplier websites
- Specification normalization
- Product scoring and ranking
- JSON/CSV export capabilities
- Modular architecture with separate concerns

---

## Migration Guide (1.0 → 2.0)

### Old Way (1.0)
```bash
# Had to manually provide suppliers
python -m src.main crawl \
  --suppliers data/suppliers.json \
  --keyword "product name"
```

### New Way (2.0)
```bash
# Automatically discover suppliers by location
python pipeline.py \
  --keywords "product name" \
  --location "LAT,LNG"
```

### Benefits of 2.0
- ✅ Automatic supplier discovery
- ✅ Location-based targeting
- ✅ Intelligent keyword optimization
- ✅ Consolidated single-command workflow
- ✅ Better documentation
- ✅ Cleaner codebase

### Backward Compatibility
The original pipeline (`src/main.py`) is still available:
```bash
python -m src.main run \
  --keyword "your search" \
  --max-domains 10
```
