# Nexa - Location-Based Supplier Discovery & Product Intelligence

A comprehensive pipeline for discovering suppliers in specific locations and extracting product insights from their websites.

## 🚀 Quick Start

```bash
# 1. Activate environment
source /Users/ankitnakhawa/miniconda3/bin/activate osh-testing-env

# 2. Run the pipeline
python pipeline.py \
  --keywords "industrial plastic supplier" \
  --location "37.7749,-122.4194" \
  --max-suppliers 10 \
  --max-pages 5

# 3. View results
cat data/results/summary.json
```

## 📋 What It Does

1. **Location-Based Discovery**: Finds suppliers near any location using Google Places API with intelligent keyword optimization
2. **Smart Crawling**: Respects robots.txt, discovers products via sitemaps
3. **Product Extraction**: Pulls product names, specs, prices, descriptions
4. **Relevance Scoring**: Ranks products by keyword relevance
5. **Structured Output**: Generates JSON, CSV, and summary reports

## 🎯 Features

### Intelligent Keyword Mapping
The pipeline automatically maps your keywords to relevant business types:
- `"industrial"` → hardware stores, industrial suppliers
- `"electronics"` → electronics stores, component distributors
- `"plastic"` → material suppliers, hardware stores
- And 30+ more keyword mappings...

### Complete Integration
- Seamless integration with existing procurement workflows
- Respects website robots.txt and rate limits
- Configurable delays and politeness controls
- Comprehensive error handling and logging

## 📦 Installation

### Using Conda (Recommended)
```bash
conda env create -f environment.yml
conda activate osh-testing-env
```

### Using pip
```bash
pip install requests beautifulsoup4 tldextract python-dateutil pint nltk
```

## 🔧 Usage

### Basic Usage
```bash
python pipeline.py \
  --keywords "your search keywords" \
  --location "LAT,LNG"
```

### All Options
```bash
python pipeline.py \
  --keywords "industrial components"  # What to search for (required)
  --location "37.7749,-122.4194"     # Where to search (required)
  --radius 50000                      # Search radius in meters (default: 50000)
  --max-suppliers 10                  # Max suppliers to process (default: 10)
  --max-pages 5                       # Max pages per supplier (default: 5)
  --delay 1.0                         # Politeness delay in seconds (default: 1.0)
  --output-dir data/results           # Output directory (default: data/results)
```

### Finding Locations

Get coordinates from Google Maps:
1. Go to [maps.google.com](https://maps.google.com)
2. Right-click on your desired location
3. Click the coordinates to copy

Common US cities:
- San Francisco: `37.7749,-122.4194`
- New York: `40.7128,-74.0060`
- Los Angeles: `34.0522,-118.2437`
- Chicago: `41.8781,-87.6298`

## 📊 Output

The pipeline generates:

```
data/results/
├── suppliers.json         # All discovered suppliers
├── products.json          # Extracted products (full details)
├── products.csv           # Products in CSV format
├── summary.json           # Quick stats and top products
└── pipeline_stats.json    # Execution metrics
```

## 💡 Examples

### Find Electronics Distributors in NYC
```bash
python pipeline.py \
  --keywords "electronics distributor components" \
  --location "40.7128,-74.0060" \
  --radius 50000 \
  --max-suppliers 10 \
  --output-dir data/nyc_electronics
```

### Find Plastic Suppliers in Bay Area
```bash
python pipeline.py \
  --keywords "industrial plastic sheets PETG" \
  --location "37.7749,-122.4194" \
  --radius 80000 \
  --max-suppliers 15 \
  --max-pages 8 \
  --output-dir data/bayarea_plastics
```

### Find Hardware Suppliers in Chicago
```bash
python pipeline.py \
  --keywords "hardware supplier industrial tools" \
  --location "41.8781,-87.6298" \
  --radius 40000 \
  --max-suppliers 8 \
  --output-dir data/chicago_hardware
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    pipeline.py                          │
│              (Main Orchestrator)                        │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Google     │  │   Existing   │  │   Product    │
│   Places     │  │   Pipeline   │  │   Scoring    │
│   Discovery  │  │   Modules    │  │   & Export   │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
   Suppliers         Product URLs      Ranked Results
```

### Core Modules

- **`pipeline.py`**: Main orchestrator connecting all components
- **`fetch_suppliers_smart.py`**: Intelligent location-based supplier discovery
- **`src/keywords.py`**: Keyword expansion and synonym generation
- **`src/sitemap.py`**: Sitemap-based URL discovery
- **`src/product_extract.py`**: Product data extraction from pages
- **`src/specs_normalize.py`**: Specification normalization
- **`src/scorer.py`**: Product relevance scoring
- **`src/store.py`**: Data persistence and reporting

## 💰 Cost

### Google Places API
- Text Search: ~$0.032 per request
- Place Details: ~$0.017 per request

**Typical run (10 suppliers)**: ~$0.27 USD

**Free tier**: Google provides **$200/month free credit** = ~740 runs/month

### Monitoring Usage
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "Billing" → "Reports"
3. Filter by "Maps Platform"

## 🛠️ Advanced Usage

### Using Existing Suppliers
If you have your own supplier list:
```bash
python -m src.main crawl \
  --suppliers data/suppliers.json \
  --keyword "your search term" \
  --max-domains 10 \
  --max-pages 5 \
  --out-json data/products.json
```

### Standalone Supplier Discovery
Just fetch suppliers without crawling:
```bash
python fetch_suppliers_smart.py \
  --keywords "industrial supplier" \
  --location "37.7749,-122.4194" \
  --max-results 20 \
  --output data/my_suppliers.json
```

## 🐛 Troubleshooting

### No suppliers found
- Increase `--radius` (e.g., 100000 = 100km)
- Use more general keywords

### No products extracted
- Some suppliers block crawlers (robots.txt)
- Increase `--max-suppliers` to try more options
- Check `pipeline_stats.json` for details

### Slow performance
- Reduce `--max-pages` for faster runs
- Reduce `--max-suppliers`
- Increase `--delay` if hitting rate limits

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Quick reference guide
- **[README_PIPELINE.md](README_PIPELINE.md)**: Detailed pipeline documentation
- **[ARCHIVE_original_readme.md](ARCHIVE_original_readme.md)**: Original system design

## 📁 Project Structure

```
Nexa/
├── pipeline.py                    # Main consolidated pipeline
├── fetch_suppliers_smart.py       # Smart supplier discovery
├── environment.yml                # Conda environment
├── requirements.txt               # Pip requirements
├── src/                          # Core modules
│   ├── main.py                   # CLI orchestrator
│   ├── keywords.py               # Keyword expansion
│   ├── discovery_seed.py         # Supplier seeding
│   ├── sitemap.py                # URL discovery
│   ├── product_extract.py        # Product extraction
│   ├── specs_normalize.py        # Spec normalization
│   ├── scorer.py                 # Product scoring
│   └── store.py                  # Data storage
└── data/                         # Data directory
    ├── suppliers.json            # Current suppliers
    ├── products.json             # Extracted products
    └── results/                  # Pipeline outputs
```

## 🤝 Contributing

This is a production-ready pipeline. Key principles:
- Respect robots.txt and site terms
- Use appropriate delays between requests
- Handle errors gracefully
- Generate structured, queryable output

## 📄 License

[Add your license here]

## 🔗 Related Projects

- Original design: [ARCHIVE_original_readme.md](ARCHIVE_original_readme.md)
- Google Places API: [Documentation](https://developers.google.com/maps/documentation/places/web-service/overview)

---

**Need help?** See [QUICKSTART.md](QUICKSTART.md) for quick reference or [README_PIPELINE.md](README_PIPELINE.md) for detailed documentation.
