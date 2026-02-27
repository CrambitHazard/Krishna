"""
KRISHNA — FastAPI application entry-point.

Initialises the app, mounts CORS middleware, wires up routers,
and exposes a /health endpoint.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_upload import router as upload_router
from app.config import settings
from app.models.schemas import HealthResponse


# ── lifespan (startup / shutdown hooks) ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Execute code on startup and shutdown."""
    # Startup
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting …")
    yield
    # Shutdown
    print(f"🛑 {settings.APP_NAME} shutting down …")


# ── app factory ────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Multi-agent AI tutoring platform — backend API",
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── routers ────────────────────────────────────────────────────────
    app.include_router(upload_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")

    # ── health check ───────────────────────────────────────────────────
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Health-check",
    )
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return app


# The application instance — used by uvicorn (e.g. `uvicorn app.main:app`)
app: FastAPI = create_app()
