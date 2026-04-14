# NutriScan AI

**NutriScan AI** has been upgraded into a production-quality Food & Health assistant. With a robust React and FastAPI architecture, it provides strong personalization, contextual AI analysis using Gemini 1.5 Flash, and a professional, SaaS-inspired UI/UX.

## 🌟 Features

- **Personalized Context-Aware AI**: The AI considers your goal (weight loss/muscle gain), diet type, health conditions (like low sodium), and your cumulative daily intake when generating advice.
- **Daily Tracker & Smart Alerts**: Real-time progress bars against your personalized goals with dynamic warnings (e.g., high sodium or low protein).
- **User Profile System**: Stores your dietary preferences locally without requiring an account.
- **Clean SaaS UI/UX**: A minimal, structured two-column layout focusing on clarity, typography, and accessibility.
- **Enhanced Meal History**: Persistent `localStorage` history featuring average health scores and insight tracking over time.

## 🛠️ Tech Stack

- **Frontend**: React (Vite), Lucide Icons, Pure CSS (SaaS UI logic).
- **Backend**: FastAPI (Python 3.9), Async Endpoints, Pydantic Schema.
- **AI Engine**: Google Gemini 1.5 Flash Vision.
- **Deployment**: Multi-stage Dockerfile (Google Cloud Run compatible).

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Gemini API Key

### 1. Backend Setup
```bash
python -m venv venv
# Activate your venv
pip install -r backend/requirements.txt

# Create a .env file and add:
# GEMINI_API_KEY=your_google_ai_studio_key
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Run the Application
```bash
uvicorn backend.main:app --reload
```
Access the application at `http://localhost:8000`.

## ☁️ Deployment (Google Cloud Run)

Deploy using the provided multi-stage `Dockerfile`:
```bash
gcloud run deploy nutriscan-ai --source . --env-vars-file env.yaml
```

## 🔒 Security

- **Environment Secrets**: API keys are isolated via python-dotenv and environment configurations.
- **Client-Side Safety**: No API keys are exposed to the browser.
- **File Validation**: Enforced image/mime type validation.

## ♿ Accessibility

- Uses rigorous semantic HTML elements and grid layouts.
- Dynamic ARIA labels are added to interactive buttons and forms.
- The neutral palette (emerald, slate, clean white) ensures WCAG high-contrast standards.

## 🧪 Testing

A complete `pytest` suite is included to ensure the `/analyze` endpoint validates both async files and profile form payloads correctly.
```bash
pytest
```