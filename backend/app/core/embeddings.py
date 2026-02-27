"""
KRISHNA — Embeddings core module (placeholder).

Will wrap the embedding model used to vectorise document chunks.
"""

from __future__ import annotations


class EmbeddingEngine:
    """Generates embeddings for text chunks."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Placeholder — returns zero vectors."""
        return [[0.0] * 768 for _ in texts]
