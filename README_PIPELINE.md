# Consolidated Supplier Discovery & Product Extraction Pipeline

## Overview

This pipeline provides an end-to-end solution for:
1. **Location-based supplier discovery** using Google Places API with intelligent keyword optimization
2. **Website scraping** to extract product information
3. **Product scoring** and insights generation

## Features

### 1. Smart Supplier Discovery (`fetch_suppliers_smart.py`)
- Uses Google Places API with **keyword-based place type optimization**
- Automatically maps keywords to relevant place types:
  - `"industrial"` → `store`, `hardware_store`, `home_goods_store`
  - `"electronics"` → `electronics_store`, `store`
  - `"plastic"` → `hardware_store`, `store`
  - And many more...
- Searches by location coordinates + radius
- Deduplicates results by domain
- Extracts company info: name, domain, state, country

### 2. Consolidated Pipeline (`pipeline.py`)
Complete end-to-end automation:
- Fetches suppliers from location
- Expands search keywords
- Crawls supplier websites (respects robots.txt)
- Extracts product data
- Normalizes specifications
- Scores products by relevance
- Generates comprehensive reports

## Installation

### Using Conda (Recommended)
```bash
# Create environment from the provided environment.yml
conda env create -f environment.yml

# Activate environment
conda activate osh-testing-env
```

### Using pip
```bash
pip install requests beautifulsoup4 tldextract python-dateutil pint nltk
```

## Usage

### Quick Start - Full Pipeline

```bash
# Activate conda environment
source /Users/ankitnakhawa/miniconda3/bin/activate osh-testing-env

# Run the full pipeline
python pipeline.py \
  --keywords "industrial plastic supplier" \
  --location "37.7749,-122.4194" \
  --radius 50000 \
  --max-suppliers 10 \
  --max-pages 5 \
  --output-dir data/results
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--keywords` | Search keywords (required) | - |
| `--location` | Lat,lng coordinates (required) | - |
| `--radius` | Search radius in meters | 50000 (50km) |
| `--max-suppliers` | Max suppliers to fetch/process | 10 |
| `--max-pages` | Max pages per supplier | 5 |
| `--delay` | Delay between requests (seconds) | 1.0 |
| `--output-dir` | Output directory | data/results |

### Example Use Cases

#### 1. Find electronics distributors near New York
```bash
python pipeline.py \
  --keywords "electronics distributor" \
  --location "40.7128,-74.0060" \
  --radius 30000 \
  --max-suppliers 5 \
  --max-pages 3 \
  --output-dir data/nyc_electronics
```

#### 2. Find hardware suppliers near Chicago
```bash
python pipeline.py \
  --keywords "hardware supplier industrial" \
  --location "41.8781,-87.6298" \
  --radius 40000 \
  --max-suppliers 8 \
  --max-pages 4 \
  --delay 2.0 \
  --output-dir data/chicago_hardware
```

#### 3. Find manufacturing suppliers near Los Angeles
```bash
python pipeline.py \
  --keywords "manufacturing supplier metal parts" \
  --location "34.0522,-118.2437" \
  --radius 60000 \
  --max-suppliers 15 \
  --max-pages 10 \
  --output-dir data/la_manufacturing
```

### Standalone Supplier Fetching

If you only want to fetch suppliers without scraping:

```bash
python fetch_suppliers_smart.py \
  --keywords "industrial plastic supplier" \
  --location "37.7749,-122.4194" \
  --radius 50000 \
  --max-results 20 \
  --output data/my_suppliers.json
```

## Output Files

The pipeline generates the following files in the output directory:

```
data/results/
├── suppliers.json         # List of discovered suppliers
├── products.json          # Extracted products with full details
├── products.csv           # Products in CSV format
├── summary.json           # Aggregated statistics
└── pipeline_stats.json    # Pipeline execution metrics
```

### suppliers.json
```json
[
  {
    "supplier_id": "7842a96c73a9baad",
    "name": "Industrial USA",
    "domain": "industrialusainc.com",
    "country": "US",
    "state": "NY",
    "sources": ["GOOGLE_PLACES_API"],
    "last_seen_at": "2025-10-11T16:46:19.458794Z"
  }
]
```

### products.json
Contains detailed product information including:
- Product name, description, price
- Specifications (raw and normalized)
- Relevance score
- Supplier information
- Source URL

## How the Keyword Optimization Works

The pipeline uses an intelligent keyword-to-place-type mapping system:

1. **Analyzes your keywords**: `"industrial plastic supplier"`
2. **Extracts relevant terms**: `industrial`, `plastic`, `supplier`
3. **Maps to place types**:
   - `industrial` → `store`, `hardware_store`, `home_goods_store`
   - `plastic` → `hardware_store`, `store`
   - `supplier` → `store`, `hardware_store`, `home_goods_store`
4. **Searches each place type** and deduplicates results
5. **Returns unique suppliers** with valid websites

This approach is **much more effective** than generic searches because it targets the right business categories.

## API Usage & Costs

### Google Places API
- **Text Search**: ~$0.032 per request
- **Place Details**: ~$0.017 per request

**Estimated cost for typical run** (10 suppliers):
- Text Search: 3 requests × $0.032 = $0.10
- Place Details: 10 requests × $0.017 = $0.17
- **Total: ~$0.27 USD**

**Free tier**: Google provides $200/month free credit for Maps Platform.

### Checking Your Usage
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "Billing" → "Reports"
3. Filter by "Maps Platform"

## Location Coordinates Reference

Common US cities:

| City | Coordinates |
|------|-------------|
| San Francisco | 37.7749,-122.4194 |
| New York | 40.7128,-74.0060 |
| Los Angeles | 34.0522,-118.2437 |
| Chicago | 41.8781,-87.6298 |
| Houston | 29.7604,-95.3698 |
| Phoenix | 33.4484,-112.0740 |
| Philadelphia | 39.9526,-75.1652 |
| San Antonio | 29.4241,-98.4936 |
| San Diego | 32.7157,-117.1611 |
| Dallas | 32.7767,-96.7970 |

**Find coordinates**: Use [Google Maps](https://maps.google.com) → Right-click location → Click coordinates to copy

## Integration with Existing Code

The pipeline integrates seamlessly with your existing modules:

- `src/keywords.py` - Keyword expansion
- `src/sitemap.py` - URL discovery
- `src/product_extract.py` - Product extraction
- `src/specs_normalize.py` - Specification normalization
- `src/scorer.py` - Product scoring
- `src/store.py` - Data storage and reporting

## Troubleshooting

### SSL Errors
Some websites may have SSL issues. The pipeline will skip these and continue with other suppliers.

### No Products Found
Common reasons:
- Supplier websites block crawlers (robots.txt)
- No sitemaps available
- Keywords don't match website content

**Solution**: Increase `--max-suppliers` to get more options.

### Rate Limiting
If you hit rate limits:
- Increase `--delay` parameter (e.g., `--delay 2.0`)
- Reduce `--max-suppliers` and `--max-pages`

## Advanced Usage

### Using Existing Suppliers
If you want to use the existing pipeline with your own supplier list:

```bash
python -m src.main crawl \
  --suppliers data/suppliers.json \
  --keyword "your search term" \
  --max-domains 10 \
  --max-pages 5 \
  --out-json data/products.json \
  --out-csv data/products.csv
```

### Combining Location Discovery with Manual Suppliers
1. First, fetch suppliers from location:
   ```bash
   python fetch_suppliers_smart.py --keywords "..." --location "..." --output data/location_suppliers.json
   ```

2. Merge with your existing suppliers list

3. Run the scraping pipeline:
   ```bash
   python -m src.main crawl --suppliers data/merged_suppliers.json --keyword "..."
   ```

## Files Created

### Core Pipeline Files
- `pipeline.py` - Main consolidated pipeline
- `fetch_suppliers_smart.py` - Smart location-based supplier fetcher
- `fetch_suppliers.py` - Basic supplier fetcher (legacy)
- `combine_suppliers.py` - Utility to merge supplier files

### Test Files
- `data/test_smart_suppliers.json` - Test output from smart fetcher
- `data/test_pipeline/` - Test pipeline results

## Next Steps

1. **Run a small test** to verify everything works
2. **Scale up** by increasing `--max-suppliers` and `--max-pages`
3. **Analyze results** in the generated CSV and JSON files
4. **Iterate** with different keywords and locations

## Support

For issues or questions:
- Check the [main README](README.md)
- Review the code comments in `pipeline.py`
- Test with small parameters first before scaling up
