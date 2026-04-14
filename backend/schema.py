from pydantic import BaseModel
from typing import List, Optional

class UserProfile(BaseModel):
    goal: str  # weight_loss | muscle_gain | maintain
    diet: str  # veg | non-veg
    conditions: List[str]  # e.g., ["low_sodium", "high_protein"]
    daily_calorie_target: int

class DailyIntakeSummary(BaseModel):
    total_calories: float
    total_protein_g: float
    total_sodium_mg: float

class AnalysisResponse(BaseModel):
    items: List[str]
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    sodium_mg: float
    health_score: float  # 1-10
    primary_concern: str
    advice: str
    meal_type: str  # breakfast | lunch | dinner | snack
