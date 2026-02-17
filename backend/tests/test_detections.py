from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)


def test_get_detections():
    """Test getting detections for a photo"""
    photo_id = str(uuid.uuid4())
    res = client.get(f"/photos/{photo_id}/detections")
    assert res.status_code == 200
    data = res.json()
    assert "photo_id" in data
    assert "detections" in data
    assert isinstance(data["detections"], list)


def test_get_detections_response_structure():
    """Test detections response has expected fields"""
    photo_id = str(uuid.uuid4())
    res = client.get(f"/photos/{photo_id}/detections")
    assert res.status_code == 200
    data = res.json()
    
    # Check response structure
    assert data["photo_id"] == photo_id
    if len(data["detections"]) > 0:
        detection = data["detections"][0]
        assert "label" in detection
        assert "confidence" in detection
        assert "bbox" in detection
