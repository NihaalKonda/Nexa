# Nexa - AI-Powered Supplier Discovery Platform

A modern platform for discovering suppliers using GPT-4 powered web search, with government contract integration and online reputation analysis.

## 🚀 Quick Start

### Backend Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start the backend
python app.py
```

Backend runs on: `http://localhost:5000`

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

Frontend runs on: `http://localhost:3000`

Visit: `http://localhost:3000/search-gpt` for the AI-powered search

## 📋 What It Does

1. **GPT-4 Web Search**: AI-powered supplier discovery using OpenAI's web search
2. **Government Contracts**: Fetches past contracts from USASpending.gov API
3. **Online Reviews**: Aggregates supplier reviews and reputation data
4. **REST API**: Clean API endpoints for frontend integration
5. **Modern UI**: Next.js frontend with beautiful search interface

## 🎯 Features

### AI-Powered Search
- Natural language product queries
- Location-based supplier discovery
- Price range filtering
- Real-time web search results

### Supplier Intelligence
- **Government Contract History**: View past government contracts for each supplier
- **Online Reputation**: Reviews from Google, Yelp, BBB, and industry sources
- **Contact Information**: Direct website and contact details
- **Product Specifications**: Detailed product info with pricing and units

### Modern Architecture
- **Backend**: Flask REST API with OpenAI integration
- **Frontend**: Next.js 15 with React 19 and TypeScript
- **Database**: Supabase with Prisma ORM
- **Authentication**: NextAuth.js

## 💡 Example Search

Search for:
- Product: "aluminum sheets"
- Location: "Buffalo, New York"
- Price Range: $50 - $300

Results include:
- 10-30 relevant suppliers
- Product specifications and pricing
- Government contract history
- Online reviews and reputation

## 🔧 API Endpoints

### Health Check
```bash
GET /api/health
```

### Search Suppliers (Fast)
```bash
POST /api/search
{
  "product": "aluminum sheets",
  "location": "Buffalo, New York",
  "price_min": 50,
  "price_max": 300
}
```

### Search with Details (Includes Contracts & Reviews)
```bash
POST /api/search/detailed
{
  "product": "aluminum sheets",
  "location": "Buffalo, New York",
  "price_min": 50,
  "price_max": 300
}
```

### Get Company Contracts
```bash
GET /api/contracts/{company_name}
```

### Get Company Reviews
```bash
POST /api/reviews
{
  "company_name": "Industrial Parts Co.",
  "location": "Buffalo, New York"
}
```

## 📁 Project Structure

```
Nexa/
├── app.py                         # Flask backend API
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (API keys)
├── BACKEND_README.md             # Backend documentation
├── MIGRATION_NOTES.md            # Migration documentation
└── frontend/                     # Next.js frontend
    ├── src/
    │   ├── app/
    │   │   ├── search-gpt/      # GPT-powered search page
    │   │   ├── search/          # Standard search page
    │   │   └── dashboard/       # Dashboard
    │   └── lib/
    │       └── api.ts           # Backend API client
    ├── package.json
    └── .env.local               # Frontend config
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│               Next.js Frontend (Port 3000)              │
│                    /search-gpt page                     │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/REST API
                          ▼
┌─────────────────────────────────────────────────────────┐
│               Flask Backend (Port 5000)                 │
│                      app.py                             │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   OpenAI     │  │ USASpending  │  │   Web        │
│   GPT-4      │  │   API        │  │   Reviews    │
│   Web Search │  │  (Gov Data)  │  │   Search     │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 💰 Cost Considerations

### OpenAI API
- **Basic search**: ~$0.01-0.05 per search
- **Detailed search** (with contracts & reviews): ~$0.10-0.30 per search

### USASpending API
- **Free** (U.S. Government API)

## 🔒 Security

- API keys stored in `.env` file (not committed to git)
- CORS enabled for frontend communication
- Environment-based configuration

## 📚 Documentation

- **[BACKEND_README.md](BACKEND_README.md)**: Complete backend API documentation
- **[frontend/README.md](frontend/README.md)**: Frontend development guide

## 🐛 Troubleshooting

### Backend won't start
- Check that port 5000 is available
- Verify `OPENAI_API_KEY` is set in `.env`
- Run: `pip install -r requirements.txt`

### Frontend can't connect to backend
- Ensure backend is running on port 5000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Verify CORS is enabled in backend

### Slow searches
- Use basic search (`/api/search`) instead of detailed
- Basic search is much faster (no contracts/reviews enrichment)

## 🚀 Production Deployment

### Backend
```bash
# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

## 📄 License

[Add your license here]

---

**Need help?** See [BACKEND_README.md](BACKEND_README.md) for detailed API documentation.