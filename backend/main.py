import os
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from .gemini_client import GeminiClient
from .schema import AnalysisResponse, UserProfile, DailyIntakeSummary

app = FastAPI(title="NutriScan AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini = GeminiClient()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_food(
    file: UploadFile = File(...),
    profile: str = Form(None),
    daily_intake: str = Form(None)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Parse context models if provided
    user_prof = None
    if profile:
        try:
            user_prof = UserProfile.validate_json(profile)
        except Exception:
            pass # ignore parse errors for graceful degradation
            
    intake_sum = None
    if daily_intake:
        try:
            intake_sum = DailyIntakeSummary.validate_json(daily_intake)
        except Exception:
            pass

    try:
        contents = await file.read()
        result = await gemini.analyze_food(
            image_bytes=contents, 
            mime_type=file.content_type,
            profile=user_prof,
            daily_intake=intake_sum
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

frontend_path = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if os.path.exists(os.path.join(frontend_path, "index.html")):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    return {"message": "Development mode: Frontend not built yet."}
