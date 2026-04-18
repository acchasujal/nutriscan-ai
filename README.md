# NutriScan AI

NutriScan AI is a full-stack meal-photo nutrition assistant built with React, FastAPI, and Google Gemini. It analyzes food images, estimates nutrition, scores meal health, and provides personalized guidance based on user goals and daily intake tracking.

## Features

- **Image-based meal analysis** with Google Gemini 2.5 Flash vision AI
- **Personalized advice** using user profile and daily intake context
- **Health scoring** with visual confirmation of detected foods
- **Staged progress UI** for smooth user experience during image analysis
- **Local meal history** stored in browser `localStorage`
- **Comprehensive diagnostics** with backend health panel and Gemini API status reporting
- **Responsive React UI** with full single-page app (SPA) routing support
- **Production-ready Docker** multi-stage build for Cloud Run deployment

## Tech Stack

- **Frontend:** React 18+ + Vite (modern ES modules, HMR)
- **Backend:** FastAPI + Pydantic v2 (async/await support)
- **AI Model:** Google Gemini `gemini-2.5-flash` (via `google-genai>=1.2.0`)
- **Deployment:** Docker (multi-stage) + Google Cloud Run
- **Static Files:** Mounted at `/assets` with React Router SPA catch-all routing

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key (free tier available at [Google AI Studio](https://aistudio.google.com/app/apikey))

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r backend/requirements.txt
```

Create `backend/.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_key_here
GEMINI_MODEL=gemini-2.5-flash
ENABLE_GEMINI_PREFLIGHT_DEBUG=false
PORT=8000
```

**Key Dependencies:**
- `fastapi==0.109.0` - Modern async web framework
- `google-genai>=1.2.0` - Latest Google Gemini SDK
- `pydantic==2.6.1` - Data validation
- `python-multipart==0.0.6` - Image upload support
- `aiofiles==23.2.1` - Async file serving for static assets

### Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### Run Locally

**Terminal 1 - Backend:**

```bash
uvicorn backend.main:app --reload --port 8000
```

Backend will be available at `http://127.0.0.1:8000`

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

Frontend dev server will be available at `http://127.0.0.1:5173`

### Useful Endpoints for Development

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Liveness probe (Cloud Run health check) |
| `/health` | GET | Full system status (API key, Gemini model, status) |
| `/test-connection` | GET | Gemini API connectivity test |
| `/analyze` | POST | Main food analysis endpoint (multipart/form-data) |
| `/{path}` | GET | Catch-all SPA route (serves `index.html`) |

**Example: Test food analysis**

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F "file=@meal.jpg" \
  -F "profile={\"goal\":\"weight_loss\",\"diet\":\"balanced\",\"conditions\":[],\"daily_calorie_target\":2000}" \
  -F "daily_intake={\"total_calories\":1200,\"total_protein_g\":60,\"total_sodium_mg\":2000}"
```

## Docker & Cloud Run Deployment

### Multi-Stage Build

The `Dockerfile` uses a two-stage build:

1. **Stage 1 (frontend-builder):** Node.js Alpine - builds React production bundle
2. **Stage 2 (backend + serving):** Python 3.11 Slim - runs FastAPI + serves built frontend

```dockerfile
# Stage 1: Builds frontend
FROM node:18-alpine AS frontend-builder
# ... npm install, npm run build → creates /app/frontend/dist

# Stage 2: FastAPI + serving
FROM python:3.11-slim
# ... pip install, copies backend + built frontend/dist
# Exposes port 8080 (Cloud Run default)
# CMD runs: uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

### Build & Test Locally

```bash
# Build the Docker image
docker build -t nutriscan-ai:latest .

# Run locally
docker run \
  -e GEMINI_API_KEY=your_key \
  -e GEMINI_MODEL=gemini-2.5-flash \
  -p 8080:8080 \
  nutriscan-ai:latest
```

### Deploy to Google Cloud Run

```bash
# Using gcloud CLI
gcloud run deploy nutriscan-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars \
    GEMINI_API_KEY=your_key,\
    GEMINI_MODEL=gemini-2.5-flash,\
    ENABLE_GEMINI_PREFLIGHT_DEBUG=false
```

**Security Best Practice:** Use Google Secret Manager for sensitive credentials:

```bash
gcloud secrets create gemini-api-key --data-file=-
gcloud run deploy nutriscan-ai \
  --source . \
  --secret GEMINI_API_KEY=gemini-api-key:latest \
  # ... other flags
```

## Frontend Architecture

The React UI includes:

- **Image Upload:** Drag-and-drop or click-to-upload image selection
- **Analysis Progress:** Visual feedback during Gemini processing
- **Health Score Display:** Nutrition breakdown, macro ratios, health metrics
- **Daily Tracker:** Running totals of calories, protein, sodium
- **Meal History:** Browse previous analyses from `localStorage`
- **Backend Health Panel:** Real-time Gemini API status and diagnostics

**React Router:** The catch-all route `/{rest_of_path:path}` in FastAPI serves `index.html`, enabling full SPA routing without page reloads.

## Backend Architecture

**Gemini Client Wrapper** (`backend/gemini_client.py`):
- Uses modern `google-genai>=1.2.0` SDK pattern
- Async request handling with `client.aio.models.generate_content()`
- Structured JSON responses with Pydantic validation
- System prompt for deterministic nutrition analysis
- Error handling with detailed logging

**FastAPI App** (`backend/main.py`):
- Static file mounting: `/assets` → `frontend/dist/assets`
- React Router SPA support: catch-all route serves `index.html`
- CORS enabled for frontend requests
- Comprehensive logging for diagnostics
- Environment validation on startup

## Testing

### Backend Tests

```bash
pytest tests/test_main.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=backend --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Manual E2E Testing

1. Start backend: `uvicorn backend.main:app --reload`
2. Start frontend: `npm run dev`
3. Upload a food image
4. Verify analysis appears with nutrition breakdown
5. Check browser console for errors
6. Check backend logs for Gemini API calls

## Important Notes

- **Nutrition Estimates:** Values are AI-powered estimates based on visible food, not laboratory measurements. Confidence scores indicate reliability.
- **API Key Security:** Never commit `.env` or API keys to git. Use `.gitignore` and Secret Manager in production.
- **Quota Management:** Pre-flight debug mode uses extra Gemini API calls. Disabled by default. Enable only for troubleshooting.
- **Multi-Stage Build:** Frontend must be built before Docker build. The Dockerfile automates this in Stage 1.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY not set` | Add to `backend/.env` and restart backend |
| Frontend not loading | Build frontend: `npm --prefix frontend run build` |
| Gemini API errors | Check quota at [Google AI Studio](https://aistudio.google.com/app/apikey) |
| Assets not loading | Verify `/assets` mount: check backend logs for `✓ Mounted /assets` |
| React Router 404s | Verify catch-all route: backend logs should show `Serving SPA index.html` |

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit with clear messages
4. Push and open a pull request

## License

MIT
