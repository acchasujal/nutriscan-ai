from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from backend.main import app
import json
import io
import hashlib

from backend.schema import AnalysisResponse

client = TestClient(app)

def test_analyze_endpoint_no_file():
    response = client.post("/analyze")
    assert response.status_code == 422

def test_analyze_endpoint_invalid_file_type():
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/analyze", files=files)
    assert response.status_code == 400

@patch("backend.main.gemini.describe_image", new_callable=AsyncMock)
@patch("backend.gemini_client.GeminiClient.analyze_food")
def test_analyze_success_with_profile(mock_analyze, mock_describe_image):
    mock_describe_image.return_value = "green salad in a round bowl"
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
        "meal_type": "lunch",
        "confidence": 0.9,
        "visual_confirmation": "green leaves in a white bowl",
        "analysis_nonce": "test-nonce-1234",
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
    assert resp_data["visual_confirmation"] == "green leaves in a white bowl"

@patch("backend.main.gemini.describe_image", new_callable=AsyncMock)
@patch("backend.gemini_client.GeminiClient.analyze_food")
def test_analyze_receives_actual_file_bytes_and_different_images_change_response(mock_analyze, mock_describe_image):
    received_payloads = []
    mock_describe_image.side_effect = [
        "mostly red circle on a white background",
        "yellow triangles beside a dark curve",
    ]

    async def fake_analyze_food(image_bytes, mime_type, profile=None, daily_intake=None, analysis_nonce=None):
        received_payloads.append((image_bytes, mime_type, analysis_nonce))
        digest = hashlib.sha256(image_bytes).hexdigest()
        return AnalysisResponse(
            items=[f"meal-{digest[:8]}"],
            calories=float(len(image_bytes)),
            protein_g=float(image_bytes[0]),
            carbs_g=float(image_bytes[-1]),
            fat_g=5.0,
            sodium_mg=150.0,
            health_score=7.5,
            primary_concern=digest[:12],
            advice=f"hash:{digest[12:20]}",
            meal_type="lunch",
            confidence=0.99,
            visual_confirmation=f"detail-{digest[20:28]}",
            analysis_nonce=analysis_nonce or f"nonce-{digest[:8]}",
        )

    mock_analyze.side_effect = fake_analyze_food

    image_one = bytes((index % 251 for index in range(12 * 1024)))
    image_two = bytes(((index * 7) % 251 for index in range(14 * 1024)))

    response_one = client.post(
        "/analyze",
        files={"file": ("meal-one.jpg", image_one, "image/jpeg")},
        data={"daily_intake": json.dumps({"total_calories": 0, "total_protein_g": 0, "total_sodium_mg": 0})},
    )
    response_two = client.post(
        "/analyze",
        files={"file": ("meal-two.jpg", image_two, "image/jpeg")},
        data={"daily_intake": json.dumps({"total_calories": 0, "total_protein_g": 0, "total_sodium_mg": 0})},
    )

    assert response_one.status_code == 200
    assert response_two.status_code == 200

    assert len(received_payloads) == 2
    assert received_payloads[0][0] == image_one
    assert received_payloads[1][0] == image_two
    assert received_payloads[0][1] == "image/jpeg"
    assert received_payloads[1][1] == "image/jpeg"
    assert received_payloads[0][2] != received_payloads[1][2]
    assert len(received_payloads[0][0]) > 8 * 1024
    assert len(received_payloads[1][0]) > 8 * 1024

    body_one = response_one.json()
    body_two = response_two.json()

    assert body_one["items"] != body_two["items"]
    assert body_one["primary_concern"] != body_two["primary_concern"]
    assert body_one["advice"] != body_two["advice"]
    assert body_one["calories"] != body_two["calories"]
    assert body_one["visual_confirmation"] != body_two["visual_confirmation"]
    assert body_one["analysis_nonce"] != body_two["analysis_nonce"]


def test_test_connection_masks_key_and_returns_live_server_time(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyExampleSecret1234")

    response = client.get("/test-connection")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["gemini_api_key_status"]["present"] is True
    assert body["gemini_api_key_status"]["masked"] == "AIza...1234"
    assert body["cloud_run_compatible"] is True
    assert body["server_time"].endswith("+00:00")
