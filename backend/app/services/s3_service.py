"""
KRISHNA — S3 service.

Handles file upload / download to AWS S3 using boto3.

Security notes (from file-uploads skill):
  • Filenames are sanitised before use as S3 keys.
  • Upload size is bounded by MAX_UPLOAD_SIZE_MB in settings.
  • Keys are prefixed with ``documents/`` to namespace uploads.

Usage:
    from app.services.s3_service import S3Service

    s3 = S3Service()
    url = await s3.upload_file("/tmp/doc.pdf", "lecture.pdf")
    await s3.download_file("documents/abc123/lecture.pdf", "/tmp/out.pdf")
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.utils.file_utils import safe_filename

logger = logging.getLogger(__name__)


class S3ServiceError(Exception):
    """Raised when an S3 operation fails."""


class S3Service:
    """
    Thin, async-safe wrapper around boto3 S3 operations.

    All boto3 calls are blocking, so they are dispatched to a thread
    via ``asyncio.to_thread`` to keep the event loop responsive.
    """

    def __init__(self) -> None:
        self._bucket = settings.S3_BUCKET_NAME
        self._region = settings.AWS_REGION

        # Build the boto3 client.
        # If explicit keys are in .env, use them.
        # Otherwise, let boto3 auto-discover from IAM instance role,
        # environment, or ~/.aws/credentials.
        client_kwargs: dict = {"region_name": self._region}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

        self._client = boto3.client("s3", **client_kwargs)

        if not self._bucket:
            logger.warning(
                "S3_BUCKET_NAME is empty — S3 uploads will be skipped. "
                "Set it in .env to enable cloud storage."
            )

    # ── properties ──────────────────────────────────────────────────────
    @property
    def is_configured(self) -> bool:
        """Return True if bucket name is set. Credentials may come from IAM role."""
        return bool(self._bucket)

    # ── upload ──────────────────────────────────────────────────────────
    async def upload_file(
        self,
        file_path: str,
        filename: str,
        *,
        document_id: str | None = None,
    ) -> str:
        """
        Upload a local file to S3.

        Parameters
        ----------
        file_path : str
            Absolute path to the file on disk.
        filename : str
            Original filename (will be sanitised).
        document_id : str | None
            Optional document ID used to namespace the S3 key.

        Returns
        -------
        str
            The S3 object key (e.g. ``documents/<doc_id>/lecture.pdf``).

        Raises
        ------
        S3ServiceError
            If the upload fails or S3 is not configured.
        """
        if not self.is_configured:
            raise S3ServiceError(
                "S3 is not configured. Set AWS_ACCESS_KEY_ID, "
                "AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME in .env."
            )

        clean_name = safe_filename(filename)
        doc_id = document_id or str(uuid.uuid4())
        s3_key = f"documents/{doc_id}/{clean_name}"

        logger.info("Uploading '%s' → s3://%s/%s", file_path, self._bucket, s3_key)

        try:
            await asyncio.to_thread(
                self._client.upload_file,
                file_path,           # local path
                self._bucket,        # bucket
                s3_key,              # key
            )
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 upload failed for '%s': %s", s3_key, exc)
            raise S3ServiceError(f"S3 upload failed: {exc}") from exc

        logger.info("Upload complete: %s", s3_key)
        return s3_key

    # ── download ────────────────────────────────────────────────────────
    async def download_file(self, key: str, local_path: str) -> None:
        """
        Download an S3 object to a local file.

        Parameters
        ----------
        key : str
            The S3 object key.
        local_path : str
            Destination path on disk (parent dirs will be created).
        """
        if not self.is_configured:
            raise S3ServiceError("S3 is not configured.")

        # Ensure the destination directory exists
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info("Downloading s3://%s/%s → '%s'", self._bucket, key, local_path)

        try:
            await asyncio.to_thread(
                self._client.download_file,
                self._bucket,
                key,
                local_path,
            )
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 download failed for '%s': %s", key, exc)
            raise S3ServiceError(f"S3 download failed: {exc}") from exc

        logger.info("Download complete: %s", local_path)

    # ── URL helper ──────────────────────────────────────────────────────
    def get_url(self, key: str) -> str:
        """Return the public URL for an S3 object (assumes public-read or signed)."""
        return f"https://{self._bucket}.s3.{self._region}.amazonaws.com/{key}"
