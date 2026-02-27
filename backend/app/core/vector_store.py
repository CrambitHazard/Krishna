"""
KRISHNA — Vector store core module (placeholder).

Will interface with a vector database (Pinecone / Qdrant / Chroma, etc.).
"""

from __future__ import annotations

from typing import Any


class VectorStore:
    """CRUD operations on the vector database."""

    async def upsert(self, doc_id: str, vectors: list[list[float]], metadata: list[dict[str, Any]]) -> None:
        """Placeholder — no-op."""
        pass

    async def query(self, vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """Placeholder — returns empty results."""
        return []
