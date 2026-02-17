# app/main.py

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine

# Routers
from app.routers import (
    projects,
    plans,
    photos,
    placements,
    review,
    gps,
    detections,
    export,profile as profile_router,
    reports
)

# -----------------------
# Sentry (before app init)
# -----------------------
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.env,
        traces_sample_rate=0.2,
    )

# -----------------------
# FastAPI App
# -----------------------
app = FastAPI(
    title="SiteBuilt Backend",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

from app.middleware.sentry_context import SentryContextMiddleware

app.add_middleware(SentryContextMiddleware)



from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from .errors import http_exception_handler, request_validation_error_handler, unhandled_exception_handler

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# -----------------------
# CORS (Vercel frontend)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Startup Event
# -----------------------
# @app.on_event("startup")
# def on_startup():
#     """
#     Create tables if they don't exist.
#     IMPORTANT: No drop_all in production.
#     """
# -----------------------
@app.get("/", tags=["system"])
def root():
    return {
        "service": "SiteBuilt Backend",
        "status": "running"
    }


# Health Check
# -----------------------
@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}

# -----------------------
# Routers
# -----------------------
app.include_router(projects.router)
app.include_router(plans.router)
app.include_router(photos.router)
app.include_router(placements.router)
app.include_router(review.router)
app.include_router(gps.router)
app.include_router(detections.router)
app.include_router(export.router)
app.include_router(profile_router.router)
app.include_router(reports.router)
