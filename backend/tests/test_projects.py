from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

HEADERS = {"X-User-Id": "test-user"}

def test_create_project():
    res = client.post(
        "/projects",
        json={"name": "Test Project", "description": "Demo"},
        headers=HEADERS,
    )
    assert res.status_code == 201
    assert "id" in res.json()
