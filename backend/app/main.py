"""
KRISHNA — FastAPI application entry-point.

Initialises the app, mounts CORS middleware, wires up routers,
and exposes a /health endpoint. Pre-loads the embedding model and
FAISS index on startup.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_analytics import router as analytics_router
from app.api.routes_chat import router as chat_router
from app.api.routes_quiz import router as quiz_router
from app.api.routes_upload import router as upload_router
from app.config import settings
from app.models.schemas import HealthResponse

logger = logging.getLogger(__name__)

# ── configure root logger ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)


# ── lifespan (startup / shutdown hooks) ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Execute code on startup and shutdown."""
    # ── Startup ─────────────────────────────────────────────────────────
    logger.info("🚀 %s v%s starting …", settings.APP_NAME, settings.APP_VERSION)

    # Pre-warm singletons so the first request isn't slow
    from app.core.embeddings import EmbeddingEngine
    from app.core.vector_store import VectorStore

    EmbeddingEngine.get_instance()
    VectorStore.get_instance()
    logger.info("Core singletons ready.")

    yield

    # ── Shutdown ────────────────────────────────────────────────────────
    logger.info("🛑 %s shutting down …", settings.APP_NAME)


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
    app.include_router(quiz_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")

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
