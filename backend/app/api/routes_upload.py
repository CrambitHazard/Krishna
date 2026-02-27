"""
KRISHNA — Upload routes.

Handles document upload endpoints. Business logic is deferred
to the services layer (not yet implemented).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, status

from app.models.schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Accepts a file upload and returns a placeholder document reference.",
)
async def upload_document(
    file: UploadFile = File(..., description="The document to upload"),
) -> UploadResponse:
    """Placeholder — returns a dummy upload confirmation."""
    return UploadResponse(
        filename=file.filename or "untitled",
        message="Document received (processing not yet implemented).",
        document_id=str(uuid.uuid4()),
        uploaded_at=datetime.utcnow(),
    )
