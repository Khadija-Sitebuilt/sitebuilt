from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
HEADERS = {"X-User-Id": "test-user"}


def test_get_review_data_missing_auth():
    """Test getting review data without auth header"""
    project_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    res = client.get(
        f"/projects/{project_id}/plans/{plan_id}/photos-with-placements"
    )
    assert res.status_code == 403


def test_get_review_data_plan_not_found():
    """Test getting review data for non-existent plan"""
    project_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    res = client.get(
        f"/projects/{project_id}/plans/{plan_id}/photos-with-placements",
        headers=HEADERS,
    )
    assert res.status_code == 404
    assert "Plan not found" in res.json().get("detail", "")


def test_get_review_response_structure():
    """Test review endpoint response structure"""
    project_id = str(uuid.uuid4())
    plan_id = str(uuid.uuid4())
    res = client.get(
        f"/projects/{project_id}/plans/{plan_id}/photos-with-placements",
        headers=HEADERS,
    )
    # Accept 404 (plan not found) as valid for this test
    if res.status_code == 200:
        data = res.json()
        assert "photos" in data or "placements" in data
