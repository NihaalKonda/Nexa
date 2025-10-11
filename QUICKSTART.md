# Quick Start Guide

## TL;DR - Run the Pipeline Now

```bash
# 1. Activate environment
source /Users/ankitnakhawa/miniconda3/bin/activate osh-testing-env

# 2. Run pipeline
python pipeline.py \
  --keywords "industrial plastic supplier" \
  --location "37.7749,-122.4194" \
  --max-suppliers 5 \
  --max-pages 3

# 3. Check results
ls -la data/results/
cat data/results/summary.json
```

## What It Does

1. **Finds suppliers** near your location using Google Places API
2. **Crawls their websites** to extract product information
3. **Scores products** by relevance to your keywords
4. **Generates reports** in JSON and CSV format

## Common Commands

### Basic run (default settings)
```bash
python pipeline.py \
  --keywords "your product keywords" \
  --location "LAT,LNG"
```

### Fast test run (1 supplier, 1 page)
```bash
python pipeline.py \
  --keywords "hardware tools" \
  --location "37.7749,-122.4194" \
  --max-suppliers 1 \
  --max-pages 1
```

### Production run (many suppliers, thorough)
```bash
python pipeline.py \
  --keywords "industrial components ISO 9001" \
  --location "40.7128,-74.0060" \
  --radius 100000 \
  --max-suppliers 20 \
  --max-pages 10 \
  --delay 2.0 \
  --output-dir data/production_run
```

## Key Parameters

| Parameter | What It Does | Recommendation |
|-----------|--------------|----------------|
| `--keywords` | What to search for | Be specific: "plastic sheets PETG" |
| `--location` | Where to search (lat,lng) | Get from Google Maps |
| `--max-suppliers` | How many suppliers to try | Start with 5-10 |
| `--max-pages` | Pages per supplier | 3-5 for testing, 10+ for production |
| `--delay` | Politeness delay (seconds) | 1.0 for testing, 2.0 for production |

## Finding Location Coordinates

**Method 1**: Google Maps
1. Go to [maps.google.com](https://maps.google.com)
2. Right-click on your location
3. Click the coordinates to copy them
4. Use format: `"37.7749,-122.4194"` (with quotes!)

**Method 2**: Common cities (copy-paste ready)
```bash
# San Francisco
--location "37.7749,-122.4194"

# New York
--location "40.7128,-74.0060"

# Los Angeles
--location "34.0522,-118.2437"

# Chicago
--location "41.8781,-87.6298"
```

## Output Files Explained

After running, check `data/results/`:

- `suppliers.json` - All suppliers found
- `products.json` - All products extracted (full details)
- `products.csv` - Products in spreadsheet format
- `summary.json` - Quick stats and top products
- `pipeline_stats.json` - Performance metrics

## Example Workflows

### Workflow 1: Electronics Distributors in NYC
```bash
python pipeline.py \
  --keywords "electronics components distributor" \
  --location "40.7128,-74.0060" \
  --radius 50000 \
  --max-suppliers 10 \
  --output-dir data/nyc_electronics
```

### Workflow 2: Industrial Plastics in Bay Area
```bash
python pipeline.py \
  --keywords "industrial plastic sheets PETG acrylic" \
  --location "37.7749,-122.4194" \
  --radius 80000 \
  --max-suppliers 15 \
  --max-pages 8 \
  --output-dir data/bayarea_plastics
```

### Workflow 3: Hardware Suppliers Nationally
```bash
# Run for multiple cities and combine results

# West Coast
python pipeline.py --keywords "hardware supplier" \
  --location "37.7749,-122.4194" --max-suppliers 5 \
  --output-dir data/west_coast

# East Coast
python pipeline.py --keywords "hardware supplier" \
  --location "40.7128,-74.0060" --max-suppliers 5 \
  --output-dir data/east_coast

# Midwest
python pipeline.py --keywords "hardware supplier" \
  --location "41.8781,-87.6298" --max-suppliers 5 \
  --output-dir data/midwest
```

## Troubleshooting

### "No suppliers found"
- Try a larger `--radius` (e.g., 100000 = 100km)
- Use more general keywords (e.g., "supplier" instead of "ISO 9001 certified PETG supplier")

### "No products extracted"
- Some suppliers block crawlers
- Increase `--max-suppliers` to try more options
- Check `pipeline_stats.json` for details

### Pipeline runs slow
- Reduce `--max-pages` (fewer pages = faster)
- Reduce `--max-suppliers` (fewer suppliers = faster)
- This is normal for production runs with many suppliers

### API errors
- Check your Google API key is valid
- Check you haven't exceeded API quotas
- Google provides $200/month free credit

## Cost Estimates

**Small test** (5 suppliers): ~$0.15
**Medium run** (10 suppliers): ~$0.30
**Large run** (20 suppliers): ~$0.60

Google provides **$200/month free**, so you can do ~650 small tests or ~330 medium runs per month.

## Best Practices

1. **Start small**: Test with `--max-suppliers 1` first
2. **Be specific**: Use detailed keywords for better results
3. **Be polite**: Use `--delay 1.0` or higher
4. **Check output**: Review `summary.json` after each run
5. **Iterate**: Adjust keywords based on results

## Need More Help?

See [README_PIPELINE.md](README_PIPELINE.md) for complete documentation.
