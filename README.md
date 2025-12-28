# SiteBuilt — Backend

This repository contains the backend for the SiteBuilt application (FastAPI + SQLAlchemy + Alembic). This README documents the project purpose, how to set it up, and the backend folder structure with descriptions for important files.

## Quick overview

- Framework: FastAPI
- DB: SQLite (development/test) and Alembic for migrations
- Python: 3.10+

## Prerequisites

- Python 3.10 or newer
- pip

## Setup

1. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   # Windows
   .\\venv\\Scripts\\activate
   # macOS / Linux
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file (copy from any example or set the environment variables required by app/config.py).

4. Run the app (development):

   ```bash
   uvicorn app.main:app --reload
   ```

## Tests

Run tests with pytest:

```bash
pytest -q
```

## Database & Migrations

- Alembic is configured via `alembic.ini` and the `alembic/` folder. Use Alembic to create and apply migrations.

## Backend folder structure

```
# Backend folder structure (excerpt)

F:\\SiteBuilt\\sitebuilt\\backend
│   .env
│   .gitignore
│   alembic.ini
│   pyproject.toml
│   render.yaml
│   requirements.txt
│   runtime.txt
│   test.db
│
├───.pytest_cache
│   └───(pytest cache files)
├───alembic
│   ├───env.py               # Alembic environment config
│   ├───README               # Alembic notes
│   ├───script.py.mako
│   └───versions             # Migration scripts
├───app
│   ├───__init__.py
│   ├───config.py            # Configuration (reads env vars)
│   ├───database.py          # DB session / engine setup
│   ├───errors.py            # Error handlers
│   ├───main.py              # FastAPI app entrypoint
│   ├───models.py            # SQLAlchemy models
│   ├───dependencies/        # Dependency overrides (auth, etc.)
│   ├───middleware/          # Middleware (e.g., Sentry context)
│   ├───routers/             # API route modules (projects, plans, photos, etc.)
│   ├───schemas/             # Pydantic schemas
│   ├───services/            # Business logic (export, storage)
│   └───utils/               # Helpers (exif, uuid)
├───tests
│   ├───conftest.py         # pytest fixtures
│   ├───test_*.py           # Unit tests for health, projects, placements, etc.
│   └───mocks/              # Mock helpers for tests
└───venv                    # Optional local virtualenv (should be gitignored)
```

## Files description

- .env — Environment variables for local development (not checked into git).
- .gitignore — Files and directories ignored by Git.
- alembic.ini — Alembic configuration for DB migrations.
- pyproject.toml — Project metadata and build config (may be empty placeholder).
- render.yaml — Render.com service configuration.
- requirements.txt — Python dependencies pinned for the project.
- runtime.txt — Python runtime specification (used by some hosts).
- test.db — SQLite database used for local testing (tracked here for convenience).

### app/ (source)
- config.py — Loads and validates environment variables and settings.
- database.py — Creates SQLAlchemy engine and session management.
- models.py — Database model definitions used by the app.
- main.py — FastAPI application and router registration.
- errors.py — Custom exception handlers and error responses.

### app/routers/
- projects.py — Endpoints to manage projects.
- plans.py — Endpoints to manage plans (PDFs, etc.).
- photos.py — Photo upload and processing endpoints.
- placements.py — Placement creation and queries.
- detections.py — Detection-related endpoints.
- export.py — Data export endpoints.
- gps.py — GPS-related endpoints.
- review.py — Endpoints for review workflow.

### app/services/
- storage.py — Abstraction for storing and retrieving files (used in tests via mocks).
- export.py — Implements export logic for project data.

### tests/
- test_health.py — Basic health-check tests.
- test_projects.py — Tests for project endpoints and logic.
- test_placements.py — Tests for placements behavior.
- mocks/ — Mock implementations used to isolate tests from external services.

## Notes & Recommendations

- Remove `test.db` from the repository and add it to `.gitignore` to avoid committing local databases.
- Commit only source files; avoid committing `venv/` or `__pycache__/` directories.
- Keep secrets (API keys, DB credentials) out of the repo; use environment variables or a secrets manager.

## Contact

If you need changes to this README or want extra sections (architecture diagram, API docs, CI/CD), tell me what to add.
