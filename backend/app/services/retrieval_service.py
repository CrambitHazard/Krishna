"""
KRISHNA — Retrieval service.

Thin layer between the API and the vector store.  Accepts a natural-
language query and returns the most relevant chunks.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RetrievalService:
    """Searches the FAISS vector store for relevant document chunks."""

    def __init__(self) -> None:
        self._store = VectorStore.get_instance()

    async def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the *top_k* most similar chunks for a given *query*.

        Returns
        -------
        list[dict]
            Each element has ``text``, ``score``, and ``metadata`` keys.
        """
        results = self._store.search(query, top_k=top_k)
        logger.info(
            "Retrieval for '%s' returned %d results.", query[:60], len(results)
        )
        return results
