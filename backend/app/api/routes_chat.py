"""
KRISHNA — Chat routes.

Handles the conversational AI endpoints.  The /chat endpoint now
delegates to the full multi-agent pipeline:

    Orchestrator → Planner → Retrieval → Teacher → Response
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, status

from app.agents.orchestrator import Orchestrator
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    RetrievalChunk,
    RetrievalRequest,
    RetrievalResponse,
    SourceReference,
)
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# ── shared singletons ──────────────────────────────────────────────────
_orchestrator = Orchestrator()
_retrieval = RetrievalService()


# ── POST /chat — full multi-agent pipeline ─────────────────────────────
@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description=(
        "Sends a message through the multi-agent pipeline: "
        "Planner retrieves context → Teacher generates a grounded answer."
    ),
)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Run the full Orchestrator → Planner → Teacher pipeline."""
    session_id = payload.session_id or str(uuid.uuid4())

    try:
        result = await _orchestrator.handle(payload.query)
    except Exception as exc:
        logger.exception("Agent pipeline failed for '%s'", payload.query[:80])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent pipeline error: {exc}",
        ) from exc

    return ChatResponse(
        answer=result.answer,
        sources=[
            SourceReference(**src) for src in result.sources
        ],
        session_id=session_id,
        agent=result.agent,
        metadata={
            **result.metadata,
            "document_id": payload.document_id,
        },
    )


# ── POST /chat/retrieve — direct semantic search ──────────────────────
@router.post(
    "/retrieve",
    response_model=RetrievalResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve relevant chunks",
    description="Performs semantic search over indexed documents.",
)
async def retrieve(payload: RetrievalRequest) -> RetrievalResponse:
    """Return the top-k most relevant document chunks for a query."""
    results = await _retrieval.search(payload.query, top_k=payload.top_k)

    return RetrievalResponse(
        query=payload.query,
        results=[
            RetrievalChunk(
                text=r["text"],
                score=r["score"],
                metadata=r["metadata"],
            )
            for r in results
        ],
        total=len(results),
    )
