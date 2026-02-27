"""
KRISHNA — Retrieval service (placeholder).

Will handle vector-similarity search over embedded document chunks.
"""

from __future__ import annotations

from typing import Any


class RetrievalService:
    """Searches the vector store for relevant chunks."""

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Placeholder — returns an empty result set."""
        return []
