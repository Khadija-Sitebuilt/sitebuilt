from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
PROJECT_ID = str(uuid.uuid4())


def test_upload_plan_missing_file():
    """Test uploading a plan without a file"""
    res = client.post(
        f"/projects/{PROJECT_ID}/plans",
    )
    assert res.status_code == 422


def test_upload_plan_invalid_file_type():
    """Test uploading a non-PDF file"""
    with open("tests/photo.jpg", "rb") as f:
        res = client.post(
            f"/projects/{PROJECT_ID}/plans",
            files={"file": ("test.jpg", f, "image/jpeg")},
        )
    assert res.status_code == 400
    assert "Only PDF files are allowed" in res.json()["detail"]

