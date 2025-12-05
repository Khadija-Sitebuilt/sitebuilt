# tests/test_projects.py

import os
import sys
import pytest

# --- Ensure backend root is on sys.path so `import app` works ---

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)  # one level up from tests/

if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app import models
from app.database import get_db

# --- Test database: file-based SQLite (shared across connections) ---

# This creates a SQLite DB file in the backend directory: ./test.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# --- Override FastAPI's DB dependency to use the test DB ---

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# --- Auto setup DB schema before each test ---

@pytest.fixture(autouse=True)
def setup_database():
    # Drop and recreate all tables before each test
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield
    # (Optional) cleanup after test; for SQLite file it's usually fine to leave


# --- Actual tests ---

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_create_and_list_projects():
    headers = {"X-User-Id": "test-user-123"}

    # Create project
    response = client.post(
        "/projects",
        json={"name": "Test Project", "description": "Demo"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Demo"

    # List projects
    response2 = client.get("/projects", headers=headers)
    assert response2.status_code == 200
    projects = response2.json()
    assert isinstance(projects, list)
    assert len(projects) == 1
    assert projects[0]["name"] == "Test Project"
