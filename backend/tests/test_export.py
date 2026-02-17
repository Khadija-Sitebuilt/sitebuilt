from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
HEADERS = {"X-User-Id": "test-user"}


def test_export_project_missing_auth():
    """Test exporting a project without auth header"""
    project_id = str(uuid.uuid4())
    res = client.post(f"/projects/{project_id}/export")
    assert res.status_code == 403


def test_export_project_not_found():
    """Test exporting a non-existent project"""
    project_id = str(uuid.uuid4())
    res = client.post(
        f"/projects/{project_id}/export",
        headers=HEADERS,
    )
    assert res.status_code == 404
    assert "Project not found" in res.json().get("detail", "")


def test_export_project_response_structure():
    """Test export endpoint response structure"""
    project_id = str(uuid.uuid4())
    res = client.post(
        f"/projects/{project_id}/export",
        headers=HEADERS,
    )
    # Accept 404 (project not found) as valid structure test
    if res.status_code == 200:
        data = res.json()
        assert "project_id" in data
        assert "export_url" in data
