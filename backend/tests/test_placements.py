from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

HEADERS = {"X-User-Id": "test-user"}

def test_invalid_placement_invalid_photo_id():
    # photo_id should be a valid UUID, but this tests non-existent photo
    invalid_uuid = str(uuid.uuid4())
    res = client.post(
        f"/photos/{invalid_uuid}/placements",
        json={"plan_id": str(uuid.uuid4()), "x": 10, "y": 10, "placement_method": "manual"},
        headers=HEADERS,
    )
    assert res.status_code == 404
    assert "Photo not found" in res.json().get("detail", "")


def test_invalid_placement_missing_plan_id():
    # Missing plan_id should raise 422 (validation error)
    invalid_uuid = str(uuid.uuid4())
    res = client.post(
        f"/photos/{invalid_uuid}/placements",
        json={"x": 10, "y": 10, "placement_method": "manual"},
        headers=HEADERS,
    )
    assert res.status_code == 422