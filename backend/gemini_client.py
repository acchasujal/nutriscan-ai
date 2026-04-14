import os
import json
from google import genai
from google.genai import types
from .schema import AnalysisResponse, UserProfile, DailyIntakeSummary

class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        
    async def analyze_food(self, image_bytes: bytes, mime_type: str, profile: UserProfile = None, daily_intake: DailyIntakeSummary = None) -> AnalysisResponse:
        if not self.client:
            return self._get_mock_response()
            
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            
            prompt = "Analyze this food image. Provide a detailed nutrition breakdown in strict JSON format."
            
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

            response = await self.client.aio.models.generate_content(
                model="gemini-1.5-flash",
                contents=[prompt, image_part],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AnalysisResponse,
                    temperature=0.2,
                ),
            )
            return AnalysisResponse.model_validate_json(response.text)
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self._get_mock_response()

    def _get_mock_response(self) -> AnalysisResponse:
        return AnalysisResponse(
            items=["Grilled Chicken Salad", "Avocado", "Cherry Tomatoes"],
            calories=450,
            protein_g=35,
            carbs_g=12,
            fat_g=28,
            sodium_mg=320,
            health_score=8.5,
            primary_concern="Looks balanced, high protein.",
            advice="Great choice! Fits well with muscle gain goals.",
            meal_type="lunch"
        )
