# Migration Notes: From src/ Pipeline to app.py Backend

**Date**: October 13, 2025

## What Changed

### ✅ Removed

**Code:**
- **`src/` folder**: Old web scraping pipeline (13 Python modules)
- **`pipeline.py`**: Old Google Places + scraping pipeline
- **`pipeline_hybrid.py`**: Hybrid pipeline variants
- **`pipeline_hybrid_improved.py`**: Improved hybrid pipeline
- **`pipeline_validated.py`**: Validated pipeline
- **`fetch_suppliers_smart.py`**: Google Places supplier fetcher
- **`gpt_search.py`**: Old GPT search implementation
- **`validate_supplier_website.py`**: Website validator

**Documentation:**
- **`ARCHIVE_original_readme.md`**: Old system design docs
- **`CHANGELOG.md`**: Old changelog
- **`QUICKSTART.md`**: Old quickstart guide
- **`README_PIPELINE.md`**: Old pipeline documentation
- **`environment.yml`**: Old Conda environment file
- **`nexa_mvp_frontend_platform_blueprint.md`**: Old frontend blueprint
- **`prices_search.json`**: Old test data file

**Data:**
- **`data/`**: Old pipeline output files (suppliers.json, products.json, products.csv)

### ✅ Added
- **`app.py`**: New Flask REST API backend with GPT-4 web search
- **`frontend/src/lib/api.ts`**: API client for frontend
- **`frontend/src/app/search-gpt/page.tsx`**: New GPT-powered search UI
- **`.env`**: Environment configuration
- **`BACKEND_README.md`**: Complete backend documentation

## Why the Change?

### Old Approach (src/ folder)
- **Manual web scraping** from supplier websites
- **Sitemap parsing** for product discovery
- **robots.txt compliance** checking
- **Local keyword matching**
- **Slow and brittle** - depends on website structure

### New Approach (app.py)
- **GPT-4 powered web search** - AI understands context
- **Government contract integration** - USASpending.gov API
- **Online review aggregation** - Reputation analysis
- **REST API** - Clean frontend integration
- **Fast and reliable** - AI handles complexity

## Benefits

1. **Faster Development**: No need to write scrapers for each site
2. **Better Results**: AI understands natural language queries
3. **More Data**: Contracts + reviews + supplier info in one place
4. **Easier Maintenance**: No scraper updates needed
5. **Modern Stack**: Flask + Next.js with TypeScript

## Cost Trade-off

- **Old**: Free (just bandwidth + Google Places API)
- **New**: OpenAI API costs (~$0.01-0.30 per search)
- **Worth it?**: Yes - much better UX and faster development

## Data Storage

The new backend (`app.py`) generates CSV files in the root directory when using the detailed search endpoint. These files are automatically ignored by git (.gitignore includes `*.csv`).

## Next Steps

1. Start backend: `python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Visit: `http://localhost:3000/search-gpt`
4. Try a search!

## Rollback (if needed)

The old system is completely removed. If you need it back:
1. Check git history: `git log --all -- src/`
2. Restore files: `git checkout <commit-hash> -- src/ pipeline.py`

## Questions?

See [BACKEND_README.md](BACKEND_README.md) for complete API documentation.
