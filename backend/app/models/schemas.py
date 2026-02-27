"""
KRISHNA — Pydantic schemas (request / response models).

Keep all shared data contracts here so routers and services
import from one place.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Health ──────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"


# ── Upload ──────────────────────────────────────────────────────────────
class UploadResponse(BaseModel):
    filename: str
    message: str
    document_id: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


# ── Chat ────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    session_id: str | None = None
    document_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    agent: str = "orchestrator"
    metadata: dict[str, Any] = Field(default_factory=dict)
