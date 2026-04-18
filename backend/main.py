import os
import logging
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from google import genai  # Modern google-genai SDK pattern
from google.genai.errors import ClientError

load_dotenv()

from .gemini_client import GeminiClient
from .schema import AnalysisResponse, UserProfile, DailyIntakeSummary

# =====================================================================
# LOGGING CONFIGURATION
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================================================================
# ENVIRONMENT VALIDATION
# =====================================================================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.warning("⚠️  WARNING: GEMINI_API_KEY environment variable is not set. Gemini API calls will fail.")
else:
    logger.info("✓ GEMINI_API_KEY is configured")

# =====================================================================
# FASTAPI APP SETUP
# =====================================================================
app = FastAPI(title="NutriScan AI API")

# Add CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
gemini = GeminiClient()
ENABLE_GEMINI_PREFLIGHT_DEBUG = os.environ.get("ENABLE_GEMINI_PREFLIGHT_DEBUG", "false").lower() == "true"

# =====================================================================
# FRONTEND PATH RESOLUTION (Multi-Stage Docker Build)
# =====================================================================
# In Docker: working directory is /app
# Frontend is built in Stage 1 and copied to /app/frontend/dist
# This code runs in Stage 2 from /app, so we use relative paths

FRONTEND_DIST_DIR = os.path.join(os.getcwd(), 'frontend', 'dist')
FRONTEND_ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, 'assets')
FRONTEND_INDEX_PATH = os.path.join(FRONTEND_DIST_DIR, 'index.html')

logger.info(f"Frontend dist directory: {FRONTEND_DIST_DIR}")
logger.info(f"Frontend assets directory: {FRONTEND_ASSETS_DIR}")
logger.info(f"Frontend index path: {FRONTEND_INDEX_PATH}")
logger.info(f"Frontend dist exists: {os.path.exists(FRONTEND_DIST_DIR)}")
logger.info(f"Frontend index.html exists: {os.path.exists(FRONTEND_INDEX_PATH)}")

# =====================================================================
# STARTUP EVENTS
# =====================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup configuration for Cloud Run diagnostics."""
    port = os.environ.get("PORT", "8080")
    host = "0.0.0.0"
    api_key_status = "configured" if GEMINI_API_KEY else "missing"
    gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    logger.info("=" * 70)
    logger.info("NutriScan AI API - Starting Server")
    logger.info("=" * 70)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Gemini Model: {gemini_model}")
    logger.info(f"Gemini API Key Status: {api_key_status}")
    logger.info(f"Preflight Debug Enabled: {ENABLE_GEMINI_PREFLIGHT_DEBUG}")
    logger.info(f"Frontend Served From: {FRONTEND_DIST_DIR}")
    logger.info(f"Frontend Index Available: {os.path.exists(FRONTEND_INDEX_PATH)}")
    logger.info(f"Frontend Assets Available: {os.path.exists(FRONTEND_ASSETS_DIR)}")
    logger.info("=" * 70)


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def _mask_api_key(api_key: str | None) -> str:
    """Mask API key for logging (show first 4 and last 4 chars only)."""
    if not api_key:
        return "missing"
    if len(api_key) <= 8:
        return f"{api_key[:4]}..."
    return f"{api_key[:4]}...{api_key[-4:]}"


# =====================================================================
# API ENDPOINTS (Health & Analysis)
# =====================================================================

@app.get("/")
async def liveness():
    """
    Liveness Probe - Cloud Run Health Check Endpoint.
    
    Cloud Run pings this immediately after container startup.
    Returns quickly to pass health checks and prevent timeout failures.
    
    Returns:
        {"status": "alive"} - Indicates the API is running
    """
    return {"status": "alive"}


@app.get("/health")
async def health_check():
    """
    Health Check Endpoint - Full system status.
    
    Returns detailed information about Gemini API connectivity,
    API key configuration, and deployment environment.
    
    Returns:
        dict: Status information including Gemini connection state,
              API key presence, and preflight debug status
    """
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
    """
    Connection Test Endpoint - Verify Gemini API connectivity.
    
    Returns server time and masked API key status for diagnostics.
    
    Returns:
        dict: Server status, time, API key status, and model information
    """
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


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_food(
    file: UploadFile = File(...),
    profile: str = Form(None),
    daily_intake: str = Form(None),
):
    """
    Food Analysis Endpoint - Main Gemini Vision API integration.
    
    Accepts an image file and optional user profile/daily intake data.
    Returns detailed nutrition analysis with health advice.
    
    Args:
        file: Image file (JPEG, PNG, WebP, etc.)
        profile: JSON string of UserProfile (optional)
        daily_intake: JSON string of DailyIntakeSummary (optional)
    
    Returns:
        AnalysisResponse: Nutrition breakdown, health score, and advice
    
    Raises:
        HTTPException: 400 if not an image, 500 on processing error
    """
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
            pass

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


# =====================================================================
# STATIC FILE SERVING - React Assets & Files
# =====================================================================
# Mount /assets directory (CSS, JS bundles, images)
# This must be done BEFORE the catch-all route

if os.path.exists(FRONTEND_ASSETS_DIR):
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_ASSETS_DIR),
        name="assets"
    )
    logger.info("✓ Mounted /assets from frontend/dist/assets")
else:
    logger.warning("⚠ Frontend assets directory not found: %s", FRONTEND_ASSETS_DIR)

# Mount .well-known and other root-level static files
if os.path.exists(FRONTEND_DIST_DIR):
    app.mount(
        "/.well-known",
        StaticFiles(directory=FRONTEND_DIST_DIR),
        name="well-known"
    )
    logger.info("✓ Mounted /.well-known from frontend/dist")
else:
    logger.warning("⚠ Frontend dist directory not found: %s", FRONTEND_DIST_DIR)


# =====================================================================
# CATCH-ALL ROUTE - React Router Support (SPA)
# =====================================================================
# This MUST be defined LAST (after all API endpoints and mounts)
# It catches all remaining paths and returns index.html for React Router

@app.get("/{rest_of_path:path}")
async def serve_spa(rest_of_path: str):
    """
    Catch-All Route - Serves React Single Page Application.
    
    This route handles all paths that don't match:
    - API endpoints (/analyze, /health, /test-connection)
    - Static file mounts (/assets/*, /.well-known/*)
    
    For any other path, returns index.html so React Router can handle
    client-side routing (e.g., /dashboard, /profile, /settings, etc.)
    
    Args:
        rest_of_path: The remaining path after /
    
    Returns:
        FileResponse: index.html with text/html media type, OR
        dict: Error response if frontend build is missing
    
    Examples:
        - GET /dashboard → serves index.html (React Router handles it)
        - GET /meal/123 → serves index.html (React Router handles it)
        - GET /assets/style.css → handled by StaticFiles mount (not this route)
        - GET /analyze → handled by /analyze endpoint (not this route)
    """
    if os.path.exists(FRONTEND_INDEX_PATH):
        logger.debug(f"Serving SPA index.html for path: /{rest_of_path}")
        return FileResponse(
            path=FRONTEND_INDEX_PATH,
            media_type="text/html"
        )
    else:
        logger.warning("Frontend index.html not found at: %s", FRONTEND_INDEX_PATH)
        return {
            "error": "Frontend not found",
            "message": "The frontend build (frontend/dist/index.html) is not available. Please build the frontend with 'npm run build' in the frontend directory.",
            "path": FRONTEND_INDEX_PATH,
            "dev_mode": True,
        }
