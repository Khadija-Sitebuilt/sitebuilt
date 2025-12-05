# app/main.py
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import projects as projects_router

# Create DB tables on startup (simple for MVP)
Base.metadata.create_all(bind=engine)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.env,
        traces_sample_rate=0.2,
    )

app = FastAPI(
    title="SiteBuilt Backend",
    version="0.1.0",
)

# CORS for frontend (Next.js on Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


app.include_router(projects_router.router)
