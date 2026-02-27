"""
KRISHNA — Configuration module.

Loads environment variables from .env and exposes them via a
pydantic-settings Settings singleton so every module can do:

    from app.config import settings
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ── resolve the project-root .env ──────────────────────────────────────
# The .env lives at  krishna/.env  (two levels above this file).
_ENV_FILE: Path = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Central configuration — all values can be overridden via env vars."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── app metadata ───────────────────────────────────────────────────
    APP_NAME: str = "KRISHNA"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ── server ─────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ───────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]

    # ── LLM provider (placeholder) ─────────────────────────────────────
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"

    # ── AWS / S3 (placeholder) ─────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # ── Vector DB (placeholder) ────────────────────────────────────────
    VECTOR_DB_URL: str = ""

    # ── Upload limits ──────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env only once)."""
    return Settings()


settings: Settings = get_settings()
