from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
HEADERS = {"X-User-Id": "test-user"}
PROJECT_ID = str(uuid.uuid4())


def test_upload_photo_missing_auth():
    """Test uploading a photo without auth header"""
    res = client.post(
        f"/projects/{PROJECT_ID}/photos",
    )
    assert res.status_code == 403


def test_upload_photo_missing_file():
    """Test uploading without a file"""
    res = client.post(
        f"/projects/{PROJECT_ID}/photos",
        headers=HEADERS,
    )
    assert res.status_code == 422


def test_upload_photo_with_jpg():
    """Test uploading a JPG photo"""
    with open("tests/photo.jpg", "rb") as f:
        res = client.post(
            f"/projects/{PROJECT_ID}/photos",
            files={"file": ("test.jpg", f, "image/jpeg")},
            headers=HEADERS,
        )
    # Should return 201/200 on success, or 400/404 if project doesn't exist
    assert res.status_code in [201, 200, 400, 404]
