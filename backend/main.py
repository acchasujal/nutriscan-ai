import os
import logging
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from google.genai.errors import ClientError

load_dotenv()

from .gemini_client import GeminiClient
from .schema import AnalysisResponse, UserProfile, DailyIntakeSummary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="NutriScan AI API")

# =====================================================================
# MIDDLEWARE & CONFIGURATION
# =====================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini = GeminiClient()
ENABLE_GEMINI_PREFLIGHT_DEBUG = os.environ.get("ENABLE_GEMINI_PREFLIGHT_DEBUG", "false").lower() == "true"

# =====================================================================
# PATH RESOLUTION: Determine frontend distribution directory
# =====================================================================
# Resolve paths dynamically relative to this file's location
# __file__ = /app/backend/main.py (in Docker)
# Frontend dist = /app/frontend/dist (in Docker, per Dockerfile)
# Path from backend to frontend: ../frontend/dist

BACKEND_DIR = Path(__file__).resolve().parent  # /app/backend
PROJECT_ROOT = BACKEND_DIR.parent  # /app
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"
FRONTEND_INDEX_PATH = FRONTEND_DIST_DIR / "index.html"

logger.info(f"Backend directory: {BACKEND_DIR}")
logger.info(f"Project root: {PROJECT_ROOT}")
logger.info(f"Frontend dist: {FRONTEND_DIST_DIR}")
logger.info(f"Frontend assets: {FRONTEND_ASSETS_DIR}")
logger.info(f"Frontend index: {FRONTEND_INDEX_PATH}")

# =====================================================================
# STARTUP EVENTS
# =====================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup configuration for Cloud Run diagnostics."""
    port = os.environ.get("PORT", "8080")
    host = "0.0.0.0"
    api_key_status = "configured" if os.environ.get("GEMINI_API_KEY") else "missing"
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    logger.info("="*60)
    logger.info("NutriScan AI API Starting")
    logger.info("="*60)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Gemini Model: {gemini_model}")
    logger.info(f"Gemini API Key: {api_key_status}")
    logger.info(f"Preflight Debug: {ENABLE_GEMINI_PREFLIGHT_DEBUG}")
    logger.info(f"Frontend served from: {FRONTEND_DIST_DIR}")
    logger.info(f"Frontend index available: {FRONTEND_INDEX_PATH.exists()}")
    logger.info(f"Frontend assets available: {FRONTEND_ASSETS_DIR.exists()}")
    logger.info("="*60)


# =====================================================================
# API ENDPOINTS (defined before static file mounts for priority)
# =====================================================================

@app.get("/")
async def liveness():
    """Liveness probe for Cloud Run health checks.
    
    Cloud Run immediately pings this endpoint after container startup.
    Returns quickly to pass health checks and prevent timeout failures.
    """
    return {"status": "alive"}


def _mask_api_key(api_key: str | None) -> str:
    if not api_key:
        return "missing"
    if len(api_key) <= 8:
        return f"{api_key[:4]}..."
    return f"{api_key[:4]}...{api_key[-4:]}"


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_food(
    file: UploadFile = File(...),
    profile: str = Form(None),
    daily_intake: str = Form(None),
):
    logger.info("Received /analyze request: filename=%s content_type=%s", file.filename, file.content_type)

    if not file.content_type or not file.content_type.startswith("image/"):
        logger.error("Invalid file type uploaded: %s", file.content_type)
        raise HTTPException(status_code=400, detail="File must be an image")

    # Parse context models if provided
    user_prof = None
    if profile:
        try:
            user_prof = UserProfile.validate_json(profile)
        except Exception as e:
            logger.warning("Failed to parse user profile: %s", e)
            pass # ignore parse errors for graceful degradation

    intake_sum = None
    if daily_intake:
        try:
            intake_sum = DailyIntakeSummary.validate_json(daily_intake)
        except Exception as e:
            logger.warning("Failed to parse daily intake: %s", e)
            pass

    try:
        await file.seek(0)
        img_bytes = await file.read()
        logger.info("Uploaded image byte size after read: %s", len(img_bytes))

        if not img_bytes:
            logger.error("Uploaded image buffer is empty after read for filename=%s", file.filename)
            raise HTTPException(status_code=400, detail="Uploaded image is empty")

        if ENABLE_GEMINI_PREFLIGHT_DEBUG:
            visual_description = await gemini.describe_image(
                image_bytes=img_bytes,
                mime_type=file.content_type,
            )
            logger.info("DEBUG_VISUAL_DESCRIPTION: %s", visual_description)
        else:
            logger.info("Gemini pre-flight debug is disabled for this request.")

        analysis_nonce = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')}-{uuid4().hex[:8]}"
        result = await gemini.analyze_food(
            image_bytes=img_bytes,
            mime_type=file.content_type,
            profile=user_prof,
            daily_intake=intake_sum,
            analysis_nonce=analysis_nonce,
        )
        logger.info("Successfully received analysis result from Gemini client.")
        return result
    except HTTPException:
        raise
    except ClientError as e:
        logger.error("Gemini client error in endpoint: %s", e, exc_info=True)
        status_code = getattr(e, "code", None) or getattr(e, "status_code", None) or 502
        raise HTTPException(status_code=int(status_code), detail=str(e))
    except Exception as e:
        logger.error("Error processing image in endpoint: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    api_key_loaded = bool(os.environ.get("GEMINI_API_KEY"))
    gemini_connection = await gemini.get_connection_status()

    return {
        "status": "ok" if gemini_connection["ok"] else "error",
        "api_key_loaded": api_key_loaded,
        "gemini_model": gemini_connection["state"],
        "gemini_message": gemini_connection["message"],
        "gemini_model_name": gemini_connection["model"],
        "preflight_debug_enabled": ENABLE_GEMINI_PREFLIGHT_DEBUG,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/test-connection")
async def test_connection():
    server_time = datetime.now(timezone.utc).isoformat()
    api_key = os.environ.get("GEMINI_API_KEY")

    return {
        "status": "ok",
        "server_time": server_time,
        "gemini_api_key_status": {
            "present": bool(api_key),
            "masked": _mask_api_key(api_key),
        },
        "preflight_debug_enabled": ENABLE_GEMINI_PREFLIGHT_DEBUG,
        "gemini_model_name": gemini.model_name,
        "cloud_run_compatible": True,
    }


# =====================================================================
# STATIC FILE SERVING & REACT ROUTER SUPPORT
# =====================================================================

# Mount assets directory if it exists (for CSS, JS, images)
if FRONTEND_ASSETS_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_ASSETS_DIR)),
        name="assets"
    )
    logger.info("✓ Mounted /assets from frontend/dist/assets")
else:
    logger.warning("⚠ Frontend assets directory not found: %s", FRONTEND_ASSETS_DIR)

# Mount other static files from frontend/dist root (favicon, manifest, etc.)
if FRONTEND_DIST_DIR.exists():
    app.mount(
        "/.well-known",
        StaticFiles(directory=str(FRONTEND_DIST_DIR)),
        name="well-known"
    )
    logger.info("✓ Mounted /.well-known from frontend/dist")
else:
    logger.warning("⚠ Frontend dist directory not found: %s", FRONTEND_DIST_DIR)


# =====================================================================
# CATCH-ALL ROUTE FOR REACT ROUTER (SPA SUPPORT)
# =====================================================================

@app.get("/{rest_of_path:path}")
async def serve_spa(rest_of_path: str):
    """
    Catch-all route that serves index.html for React Router.
    
    This allows React Router to handle client-side routing for all paths
    that don't match API endpoints or static files.
    
    Examples:
    - GET /dashboard → serves index.html
    - GET /profile/settings → serves index.html
    - GET /assets/style.css → handled by StaticFiles mount
    - GET /analyze → handled by API endpoint
    """
    if FRONTEND_INDEX_PATH.exists():
        logger.debug(f"Serving SPA index.html for path: /{rest_of_path}")
        return FileResponse(
            path=str(FRONTEND_INDEX_PATH),
            media_type="text/html"
        )
    else:
        logger.warning("Frontend index.html not found: %s", FRONTEND_INDEX_PATH)
        return {
            "error": "Frontend not found",
            "message": "The frontend build (frontend/dist/index.html) is not available. Build the frontend with 'npm run build' in the frontend directory.",
            "path": str(FRONTEND_INDEX_PATH),
            "dev_mode": True,
        }
