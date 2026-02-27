"""
KRISHNA — S3 service (placeholder).

Handles file upload / download to AWS S3.
"""

from __future__ import annotations

from app.config import settings


class S3Service:
    """Thin wrapper around S3 operations."""

    def __init__(self) -> None:
        self.bucket = settings.S3_BUCKET_NAME
        self.region = settings.AWS_REGION

    async def upload(self, key: str, data: bytes) -> str:
        """Placeholder — returns a fake S3 URL."""
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

    async def download(self, key: str) -> bytes:
        """Placeholder — returns empty bytes."""
        return b""
