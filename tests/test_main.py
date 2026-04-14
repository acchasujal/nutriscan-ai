import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from backend.main import app
import json
import io

client = TestClient(app)

def test_analyze_endpoint_no_file():
    response = client.post("/analyze")
    assert response.status_code == 422

def test_analyze_endpoint_invalid_file_type():
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/analyze", files=files)
    assert response.status_code == 400

@patch("backend.gemini_client.GeminiClient.analyze_food")
def test_analyze_success_with_profile(mock_analyze):
    mock_data = {
        "items": ["Salad"],
        "calories": 200,
        "protein_g": 5,
        "carbs_g": 10,
        "fat_g": 2,
        "sodium_mg": 150,
        "health_score": 9.0,
        "primary_concern": "Balanced meal",
        "advice": "Keep eating fresh veggies!",
        "meal_type": "lunch"
    }
    
    # Fastapi depends on async, mock needs to be an async mock returning the model
    mock_return = MagicMock(**mock_data)
    mock_return.model_dump = lambda: mock_data
    mock_return.model_dump_json = lambda: json.dumps(mock_data)
    
    # Important update since gemini_client.analyze_food is async
    async_mock = AsyncMock(return_value=mock_return)
    mock_analyze.side_effect = async_mock

    img_byte_arr = io.BytesIO()
    img_byte_arr.write(b"fake-image-data")
    img_byte_arr.seek(0)
    
    profile_data = {
        "goal": "weight_loss",
        "diet": "veg",
        "conditions": ["low_sodium"],
        "daily_calorie_target": 2000
    }
    
    intake_data = {
        "total_calories": 500,
        "total_protein_g": 30,
        "total_sodium_mg": 400
    }

    files = {"file": ("test.jpg", img_byte_arr, "image/jpeg")}
    data = {
        "profile": json.dumps(profile_data),
        "daily_intake": json.dumps(intake_data)
    }

    response = client.post("/analyze", files=files, data=data)
    
    assert response.status_code == 200
    resp_data = response.json()
    assert "health_score" in resp_data
    assert "calories" in resp_data
    assert resp_data["meal_type"] == "lunch"
