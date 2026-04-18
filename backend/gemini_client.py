import os
import logging
from datetime import datetime, timezone
from google import genai
from google.genai.errors import ClientError
from google.genai import types
from .schema import AnalysisResponse, UserProfile, DailyIntakeSummary

logger = logging.getLogger(__name__)
DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


SYSTEM_PROMPT = """You are NutriScan AI, a food-vision nutrition analyst.

Return strictly valid JSON that matches the provided schema exactly.
Do not wrap the response in markdown.
Use the supplied request nonce verbatim in the `analysis_nonce` field.
Populate `visual_confirmation` with one concrete visual detail that is unique to the uploaded image, such as a color, object, plating detail, garnish, or visible eating state.
If no food is visible, say so clearly in `items`, `primary_concern`, `advice`, and `visual_confirmation` while still returning valid JSON.
Base every field on the current image and never reuse details from prior requests.
"""

class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = DEFAULT_GEMINI_MODEL
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def _require_client(self) -> genai.Client:
        if not self.client:
            logger.error("No GEMINI_API_KEY found.")
            raise ValueError("GEMINI_API_KEY is not configured")

        return self.client

    def _build_image_part(self, image_bytes: bytes, mime_type: str) -> types.Part:
        if not image_bytes:
            raise ValueError("Uploaded image is empty")

        return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    async def get_connection_status(self) -> dict:
        if not self.client:
            return {
                "ok": False,
                "state": "missing_api_key",
                "message": "GEMINI_API_KEY is not configured.",
                "model": self.model_name,
            }

        try:
            await self.client.aio.models.generate_content(
                model=self.model_name,
                contents="ping",
            )
            return {
                "ok": True,
                "state": "working",
                "message": "Successful",
                "model": self.model_name,
            }
        except ClientError as e:
            message = str(e)
            state = "error"
            lowered = message.lower()
            if "resource_exhausted" in lowered or "quota" in lowered or "429" in lowered:
                state = "quota_exhausted"
                message = "Gemini API quota exhausted. Please wait and retry."
            elif "not_found" in lowered or "404" in lowered:
                state = "model_not_found"
                message = f"Configured Gemini model is unavailable: {self.model_name}"

            return {
                "ok": False,
                "state": state,
                "message": message,
                "model": self.model_name,
            }
        except Exception as e:
            return {
                "ok": False,
                "state": "error",
                "message": str(e),
                "model": self.model_name,
            }

    async def describe_image(self, image_bytes: bytes, mime_type: str) -> str:
        client = self._require_client()
        image_part = self._build_image_part(image_bytes, mime_type)
        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents=[
                image_part,
                "Describe the colors and main shapes in this image.",
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
            ),
        )

        return (response.text or "").strip()

    async def analyze_food(
        self,
        image_bytes: bytes,
        mime_type: str,
        profile: UserProfile = None,
        daily_intake: DailyIntakeSummary = None,
        analysis_nonce: str | None = None,
    ) -> AnalysisResponse:
        client = self._require_client()
        logger.info(f"Received image for analysis. Size: {len(image_bytes)} bytes, MIME type: {mime_type}")

        try:
            image_part = self._build_image_part(image_bytes, mime_type)
            nonce = analysis_nonce or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")

            prompt = f"""Analyze this food image and provide a detailed nutrition breakdown in strict JSON format.

Request nonce:
- analysis_nonce: {nonce}

Hard requirements:
- The JSON must include `analysis_nonce` exactly equal to "{nonce}".
- The JSON must include `visual_confirmation` with one unique visible detail from this exact photo.
- Include `confidence` as a number from 0.0 to 1.0.
- Nutrition values must be realistic estimates based only on what is visible. Do not invent hidden ingredients or exact serving sizes.
- If the image is ambiguous, lower confidence and keep calorie/macronutrient estimates conservative.
- Never return markdown, commentary, or extra keys.
"""

            if profile and daily_intake:
                prompt += f"""
User Profile Context:
- Goal: {profile.goal}
- Diet: {profile.diet}
- Conditions: {', '.join(profile.conditions) if profile.conditions else 'None'}
- Daily Calorie Target: {profile.daily_calorie_target}

Today's Cumulative Intake (before this meal):
- Calories: {daily_intake.total_calories}
- Protein: {daily_intake.total_protein_g}g
- Sodium: {daily_intake.total_sodium_mg}mg

Personalize the 'primary_concern' and 'advice' strictly based on this context. 
If this meal will push them over their calorie or sodium targets, warn them.
"""

            logger.info("Sending request to Gemini API with image and prompt...")
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=AnalysisResponse,
                    temperature=0.1,
                ),
            )
            
            logger.info(f"Received response from Gemini API: {response.text}")
            
            try:
                # Add parsing + fallback handling if response malformed
                return AnalysisResponse.model_validate_json(response.text)
            except Exception as parse_e:
                logger.error(f"Failed to parse JSON response: {parse_e}")
                logger.error(f"Raw response was: {response.text}")
                # Try a fallback if JSON is malformed
                # We can strip markdown if present just in case
                cleaned_text = response.text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                return AnalysisResponse.model_validate_json(cleaned_text.strip())
                
        except Exception as e:
            logger.error(f"Gemini API Error: {e}", exc_info=True)
            raise e

    async def test_connection(self) -> bool:
        status = await self.get_connection_status()
        if not status["ok"]:
            logger.error("Connection test failed: %s", status["message"])
        return status["ok"]
