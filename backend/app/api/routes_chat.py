"""
KRISHNA — Chat routes.

Handles the conversational AI endpoints. The orchestrator agent
decides which sub-agent answers — for now we return a dummy reply,
enriched with retrieved context when documents are available.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    RetrievalRequest,
    RetrievalResponse,
    RetrievalChunk,
)
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/chat", tags=["Chat"])

_retrieval = RetrievalService()


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Sends a message to the AI tutor and receives a response.",
)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Placeholder — echoes the question back with a stub reply."""
    session_id = payload.session_id or str(uuid.uuid4())

    # Retrieve relevant context if documents have been indexed
    context_snippets: list[str] = []
    try:
        results = await _retrieval.search(payload.message, top_k=3)
        context_snippets = [r["text"][:200] for r in results]
    except Exception:
        pass

    reply = f"[KRISHNA stub] You asked: '{payload.message}'."
    if context_snippets:
        reply += f" Found {len(context_snippets)} relevant chunk(s)."
    else:
        reply += " No documents indexed yet — upload a PDF first!"

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        agent="orchestrator",
        metadata={
            "document_id": payload.document_id,
            "context_chunks": len(context_snippets),
        },
    )


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
