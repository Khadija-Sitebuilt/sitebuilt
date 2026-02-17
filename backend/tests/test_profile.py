from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
HEADERS = {"X-User-Id": "test-user"}


def test_get_profile():
    """Test getting user profile"""
    res = client.get("/me", headers=HEADERS)
    # Should return 200 if user exists in DB
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert "auth_uid" in data


def test_get_profile_missing_auth():
    """Test getting profile without auth header"""
    res = client.get("/me")
    assert res.status_code == 403


def test_update_profile_missing_auth():
    """Test updating profile without auth header"""
    res = client.patch("/me", json={"full_name": "test"})
    assert res.status_code == 403


def test_update_profile_with_auth():
    """Test updating profile with valid auth header"""
    res = client.patch(
        "/me",
        json={"full_name": "Updated Name"},
        headers=HEADERS,
    )
    # Should return 200 on success
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
