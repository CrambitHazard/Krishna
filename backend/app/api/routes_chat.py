"""
KRISHNA — Chat routes.

Handles the conversational AI endpoints. The orchestrator agent
decides which sub-agent answers — for now we return a dummy reply.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


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

    return ChatResponse(
        reply=f"[KRISHNA stub] You asked: '{payload.message}'. Real agent logic coming soon!",
        session_id=session_id,
        agent="orchestrator",
        metadata={"document_id": payload.document_id},
    )
