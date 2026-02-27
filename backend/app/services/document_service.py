"""
KRISHNA — Document service (placeholder).

Will handle document parsing, chunking, and storage coordination.
"""

from __future__ import annotations


class DocumentService:
    """Processes uploaded documents for the knowledge pipeline."""

    async def process(self, filename: str, content: bytes) -> dict:
        """Placeholder — returns a stub acknowledgement."""
        return {
            "filename": filename,
            "status": "pending",
            "chunks": 0,
        }
