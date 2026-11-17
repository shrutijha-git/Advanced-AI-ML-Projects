
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from app import app


def test_home_page():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"SpamShield AI" in response.data


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_empty_message():
    client = app.test_client()

    response = client.post(
        "/api/predict",
        json={"message": ""},
    )

    assert response.status_code == 400


def test_invalid_json():
    client = app.test_client()

    response = client.post(
        "/api/predict",
        data="not-json",
        content_type="text/plain",
    )

    assert response.status_code == 400


def test_prediction():
    client = app.test_client()

    response = client.post(
        "/api/predict",
        json={
            "message": "Congratulations! You won a free prize!"
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["prediction"] in {"Spam", "Not Spam"}
    assert 0 <= data["spam_probability"] <= 100
    assert 0 <= data["confidence"] <= 100
