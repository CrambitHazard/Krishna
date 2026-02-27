"""
KRISHNA — Upload routes.

Handles document upload: reads the PDF, extracts text, chunks it,
embeds chunks, and stores them in the FAISS vector index.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.schemas import UploadResponse
from app.services.document_service import DocumentService
from app.utils.file_utils import is_allowed_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

# Shared service instance
_doc_service = DocumentService()


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description=(
        "Accepts a PDF file, extracts text, chunks it into segments, "
        "generates embeddings, and stores them in the vector index."
    ),
)
async def upload_document(
    file: UploadFile = File(..., description="PDF document to upload"),
) -> UploadResponse:
    """Process a PDF upload through the full ingestion pipeline."""

    filename = file.filename or "untitled.pdf"

    # ── validation ──────────────────────────────────────────────────────
    if not is_allowed_file(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: .pdf, .txt, .md, .docx, .pptx",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # ── ingestion pipeline ──────────────────────────────────────────────
    try:
        result = await _doc_service.process(filename, content)
    except Exception as exc:
        logger.exception("Document processing failed for '%s'", filename)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process document: {exc}",
        ) from exc

    return UploadResponse(
        filename=result.filename,
        message=f"Document ingested successfully — {result.total_chunks} chunks indexed.",
        document_id=result.document_id,
        total_pages=result.total_pages,
        total_chunks=result.total_chunks,
        uploaded_at=datetime.utcnow(),
    )
