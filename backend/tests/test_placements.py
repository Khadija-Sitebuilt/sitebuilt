from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invalid_placement_invalid_plan_id():
    # plan_id is not an integer → should raise 400
    res = client.post(
        "/photos/valid-photo/placement",
        json={"plan_id": "x", "x": 10, "y": 10, "placement_method": "manual"},
        headers={"X-User-Id": "test-user"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid plan_id"


def test_invalid_placement_invalid_photo_id():
    # photo_id is explicitly "invalid-id" → should raise 404
    res = client.post(
        "/photos/invalid-id/placement",
        json={"plan_id": "123", "x": 10, "y": 10, "placement_method": "manual"},
        headers={"X-User-Id": "test-user"},
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Photo not found"