"""
KRISHNA — Upload routes.

Handles document upload through this pipeline:
  1. Validate the file (extension, size).
  2. Save temporarily to disk.
  3. Upload to S3 (if configured).
  4. Process (extract → chunk → embed → FAISS) from the local copy.
  5. Clean up the temp file.
"""

from __future__ import annotations

import logging
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import settings
from app.models.schemas import UploadResponse
from app.services.document_service import DocumentService
from app.services.s3_service import S3Service, S3ServiceError
from app.utils.file_utils import is_allowed_file, safe_filename

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

# ── shared service instances ────────────────────────────────────────────
_doc_service = DocumentService()
_s3_service = S3Service()


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description=(
        "Accepts a PDF file, saves it locally, uploads it to S3, "
        "then extracts text, chunks, embeds, and indexes in FAISS."
    ),
)
async def upload_document(
    file: UploadFile = File(..., description="PDF document to upload"),
) -> UploadResponse:
    """Full upload pipeline: validate → save → S3 → process → cleanup."""

    filename = safe_filename(file.filename or "untitled.pdf")

    # ── 1. Validate extension ───────────────────────────────────────────
    if not is_allowed_file(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed: .pdf, .txt, .md, .docx, .pptx",
        )

    # ── 2. Read and validate size ───────────────────────────────────────
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit.",
        )

    # ── 3. Save to temp file ────────────────────────────────────────────
    suffix = Path(filename).suffix
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, prefix="krishna_"
    )
    tmp_path = Path(tmp.name)
    try:
        tmp.write(content)
        tmp.close()
        logger.info("Saved temp file: %s (%d bytes)", tmp_path, len(content))

        # ── 4. Upload to S3 (non-blocking, best-effort) ────────────────
        s3_key: str | None = None
        if _s3_service.is_configured:
            try:
                s3_key = await _s3_service.upload_file(
                    file_path=str(tmp_path),
                    filename=filename,
                )
                logger.info("S3 upload complete: %s", s3_key)
            except S3ServiceError as exc:
                # Log but don't block processing — S3 is optional
                logger.warning("S3 upload failed (continuing): %s", exc)
        else:
            logger.info("S3 not configured — skipping cloud upload.")

        # ── 5. Process document from local copy ─────────────────────────
        try:
            result = await _doc_service.process(filename, content)
        except Exception as exc:
            logger.exception("Document processing failed for '%s'", filename)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process document: {exc}",
            ) from exc

    finally:
        # ── 6. Clean up temp file ───────────────────────────────────────
        try:
            tmp_path.unlink(missing_ok=True)
            logger.debug("Cleaned up temp file: %s", tmp_path)
        except OSError:
            logger.warning("Could not delete temp file: %s", tmp_path)

    return UploadResponse(
        filename=result.filename,
        message=(
            f"Document ingested successfully — "
            f"{result.total_chunks} chunks indexed."
            + (f" S3 key: {s3_key}" if s3_key else "")
        ),
        document_id=result.document_id,
        total_pages=result.total_pages,
        total_chunks=result.total_chunks,
        uploaded_at=datetime.utcnow(),
    )
