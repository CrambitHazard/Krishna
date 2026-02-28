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
    total_pages: int
    total_chunks: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


# ── Retrieval ───────────────────────────────────────────────────────────
class RetrievalChunk(BaseModel):
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4096)
    top_k: int = Field(default=3, ge=1, le=20)


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalChunk]
    total: int


# ── Chat (multi-agent pipeline) ────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4096)
    session_id: str | None = None
    document_id: str | None = None


class SourceReference(BaseModel):
    """A single source chunk used to ground the answer."""
    chunk_index: int | None = None
    filename: str = "unknown"
    document_id: str = ""
    score: float = 0.0


class ChatResponse(BaseModel):
    """Structured output from the multi-agent pipeline."""
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    session_id: str
    agent: str = "orchestrator"
    metadata: dict[str, Any] = Field(default_factory=dict)
