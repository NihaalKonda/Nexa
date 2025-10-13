# Nexa Backend API

Flask-based backend API for GPT-powered supplier search, integrating government contracts and online reviews.

## Features

- **GPT-4 Web Search**: Searches the web for suppliers using OpenAI's GPT-4 with web search
- **Government Contracts**: Fetches past government contracts from USASpending.gov
- **Online Reviews**: Searches for supplier reviews and mentions across the web
- **REST API**: Clean REST API endpoints for frontend integration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
FLASK_ENV=development
PORT=5000
```

### 3. Run the Backend

```bash
python app.py
```

The backend will start on `http://localhost:5000`

## API Endpoints

### Health Check

```bash
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "message": "Backend API is running"
}
```

### Search Suppliers (Basic)

```bash
POST /api/search
Content-Type: application/json

{
  "product": "aluminum sheets",
  "location": "Buffalo, New York",
  "price_min": 50,
  "price_max": 300
}
```

Response:
```json
{
  "success": true,
  "count": 10,
  "suppliers": [
    {
      "name": "Supplier Name",
      "location": "City, State",
      "product_title": "Specific product name",
      "units_sold": "Unit of sale",
      "price_range": "$X - $Y per unit",
      "website": "https://example.com",
      "contact": "email or phone",
      "description": "short summary"
    }
  ]
}
```

### Search Suppliers (Detailed with Contracts & Reviews)

```bash
POST /api/search/detailed
Content-Type: application/json

{
  "product": "aluminum sheets",
  "location": "Buffalo, New York",
  "price_min": 50,
  "price_max": 300
}
```

Response includes additional fields:
- `past_contracts`: Government contract information
- `reviews_mentions`: Online reviews and mentions

⚠️ **Note**: This endpoint takes longer (2+ seconds per supplier) as it enriches data with contracts and reviews.

### Get Company Contracts

```bash
GET /api/contracts/{company_name}
```

Example:
```bash
GET /api/contracts/Industrial%20Parts%20Co.
```

Response:
```json
{
  "success": true,
  "company": "Industrial Parts Co.",
  "contracts": "Department of Defense: $1,234,567; GSA: $567,890"
}
```

### Get Company Reviews

```bash
POST /api/reviews
Content-Type: application/json

{
  "company_name": "Industrial Parts Co.",
  "location": "Buffalo, New York"
}
```

Response:
```json
{
  "success": true,
  "company": "Industrial Parts Co.",
  "location": "Buffalo, New York",
  "reviews": "Highly rated supplier with 4.5 stars on Google. Known for quality products..."
}
```

## Frontend Integration

The frontend is configured to connect to the backend API at `http://localhost:5000/api`.

### Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit the new GPT Search page at: `http://localhost:3000/search-gpt`

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Flask Backend (app.py)               │
│                    Port: 5000                           │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   OpenAI     │  │ USASpending  │  │   Web        │
│   GPT-4      │  │   API        │  │   Reviews    │
│   Web Search │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Migration from `src/` Folder

This backend replaces the functionality in the `src/` folder with a more modern approach:

### Old Approach (`src/`)
- Manual web crawling and scraping
- Sitemap parsing
- robots.txt checking
- Local keyword matching

### New Approach (`app.py`)
- **GPT-4 powered web search** for more accurate results
- **Structured JSON output** from AI
- **Government contract integration**
- **Online review aggregation**
- **REST API** for frontend integration

The `src/` folder is kept for reference and compatibility, but the new backend provides a more powerful and flexible solution.

## Cost Considerations

### OpenAI API
- Basic search: ~$0.01-0.05 per search (depends on results)
- Detailed search with reviews: ~$0.10-0.30 per search (more API calls)

### USASpending API
- Free (government API)

## Development

### Enable Debug Mode

Set `FLASK_ENV=development` in `.env` to enable:
- Auto-reload on code changes
- Detailed error messages
- Debug logs

### CORS Configuration

CORS is enabled by default for all origins. To restrict:

```python
CORS(app, origins=["http://localhost:3000"])
```

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Set up reverse proxy (nginx/Apache)
4. Enable HTTPS
5. Secure your OpenAI API key

## Troubleshooting

### Backend won't start
- Check that port 5000 is not in use
- Verify OpenAI API key is set in `.env`
- Install all dependencies: `pip install -r requirements.txt`

### Frontend can't connect
- Ensure backend is running on port 5000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Verify CORS is enabled in `app.py`

### Slow searches
- Use basic search (`/api/search`) instead of detailed
- Reduce the number of suppliers returned
- Consider caching results

## API Key Security

⚠️ **Important**: Never commit your `.env` file to version control!

The `.env` file is already in `.gitignore`. If you accidentally committed it:

```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```
