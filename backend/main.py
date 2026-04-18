import os
import logging
from datetime import datetime, timezone
from uuid import uuid4
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini = GeminiClient()
ENABLE_GEMINI_PREFLIGHT_DEBUG = os.environ.get("ENABLE_GEMINI_PREFLIGHT_DEBUG", "false").lower() == "true"


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
    logger.info("="*60)


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

frontend_path = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if os.path.exists(os.path.join(frontend_path, "index.html")):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    return {"message": "Development mode: Frontend not built yet."}
