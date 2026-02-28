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


# ── Quiz ────────────────────────────────────────────────────────────────
class QuizQuestionSchema(BaseModel):
    """A single MCQ question."""
    question: str
    options: list[str]
    correct_answer: str
    explanation: str


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=1024)
    num_questions: int = Field(default=5, ge=3, le=5)
    use_context: bool = Field(
        default=True,
        description="If true, ground questions on uploaded documents.",
    )


class QuizResponse(BaseModel):
    topic: str
    questions: list[QuizQuestionSchema]
    total: int
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── Quiz Evaluation ────────────────────────────────────────────────────
class QuizEvaluateRequest(BaseModel):
    """User's answers submitted for grading."""
    user_answers: list[str] = Field(
        ...,
        min_length=1,
        description="List of user answers, e.g. ['A', 'C', 'B', 'D', 'A']",
    )
    quiz_data: list[QuizQuestionSchema] = Field(
        ...,
        min_length=1,
        description="The original quiz questions to evaluate against.",
    )


class QuestionFeedbackSchema(BaseModel):
    """Per-question feedback after evaluation."""
    question: str
    options: list[str]
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


class QuizEvaluateResponse(BaseModel):
    """Evaluation result with score and per-question feedback."""
    score: int
    total: int
    percentage: float
    correct_questions: list[QuestionFeedbackSchema]
    incorrect_questions: list[QuestionFeedbackSchema]

