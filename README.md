# NutriScan AI

NutriScan AI is a meal-photo nutrition assistant built with React, FastAPI, and Google Gemini. It analyzes food images, estimates nutrition, scores meal health, and gives personalized guidance based on the user's goals and daily intake.

## Features

- Image-based meal analysis with Gemini vision
- Personalized advice using profile and daily intake context
- Backend health panel with live Gemini status reporting
- Staged analysis progress UI so scans do not feel stuck
- Local meal history stored in `localStorage`
- Debug-friendly API diagnostics for upload and Gemini troubleshooting

## Product notes

- Nutrition values are AI estimates based on the visible meal, not laboratory measurements.
- Confidence and visual confirmation are included to help users judge how trustworthy a scan is.
- Pre-flight Gemini visual debugging is available, but disabled by default to reduce quota usage.

## Tech stack

- Frontend: React + Vite
- Backend: FastAPI + Pydantic
- AI: Google Gemini `gemini-2.5-flash`
- Deployment: Docker + Google Cloud Run

## Local setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- A Gemini API key

### Backend

```bash
python -m venv venv
# activate the virtual environment
pip install -r backend/requirements.txt
```

Create `backend/.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-2.5-flash
ENABLE_GEMINI_PREFLIGHT_DEBUG=false
```

### Frontend

```bash
cd frontend
npm install
cd ..
```

### Run locally

Backend:

```bash
uvicorn backend.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

Local URLs:

- Frontend: `http://127.0.0.1:5173/`
- Backend health: `http://127.0.0.1:8000/health`
- Backend test connection: `http://127.0.0.1:8000/test-connection`

## Google Cloud Run deployment

The repository includes a multi-stage `Dockerfile` that builds the frontend and serves the bundled app from FastAPI.

Build locally:

```bash
npm --prefix frontend run build
```

Deploy to Cloud Run:

```bash
gcloud run deploy nutriscan-ai \
  --source . \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=YOUR_KEY,GEMINI_MODEL=gemini-2.5-flash,ENABLE_GEMINI_PREFLIGHT_DEBUG=false
```

For production, prefer Secret Manager instead of committing or scripting plaintext API keys.

## Testing

Backend tests:

```bash
pytest tests/test_main.py
```

Frontend tests:

```bash
cd frontend
npm test
```
