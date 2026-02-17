from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
HEADERS = {"X-User-Id": "test-user"}


def test_create_report_missing_auth():
    """Test creating a report without auth header"""
    project_id = str(uuid.uuid4())
    res = client.post(f"/projects/{project_id}/reports")
    assert res.status_code == 403


def test_create_report_project_not_found():
    """Test creating a report for non-existent project"""
    project_id = str(uuid.uuid4())
    res = client.post(
        f"/projects/{project_id}/reports",
        headers=HEADERS,
    )
    assert res.status_code == 404


def test_get_report_missing_auth():
    """Test getting a list of reports without auth header"""
    project_id = str(uuid.uuid4())
    res = client.get(f"/projects/{project_id}/reports")
    assert res.status_code == 403


def test_list_reports_missing_auth():
    """Test listing reports without auth header"""
    project_id = str(uuid.uuid4())
    res = client.get(f"/projects/{project_id}/reports")
    assert res.status_code == 403
