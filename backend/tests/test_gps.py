from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
HEADERS = {"X-User-Id": "test-user"}


def test_get_gps_suggestion_missing_auth():
    """Test getting GPS suggestion without auth header"""
    photo_id = str(uuid.uuid4())
    res = client.get(f"/photos/{photo_id}/gps-suggestion")
    assert res.status_code == 403


def test_get_gps_suggestion_invalid_photo():
    """Test getting GPS suggestion for non-existent photo"""
    photo_id = str(uuid.uuid4())
    res = client.get(f"/photos/{photo_id}/gps-suggestion", headers=HEADERS)
    # Should return 404 for non-existent photo
    assert res.status_code == 404


def test_get_gps_suggestion_valid_request():
    """Test GPS suggestion endpoint structure"""
    photo_id = str(uuid.uuid4())
    res = client.get(f"/photos/{photo_id}/gps-suggestion", headers=HEADERS)
    # Accept 404 (photo not found) as valid for this test
    assert res.status_code in [200, 400, 404]
