"""
KRISHNA — FAISS vector store.

Provides an in-memory FAISS index with metadata bookkeeping so we can
map vector IDs back to the original text chunks plus their metadata.

The index uses inner-product search (IndexFlatIP) — because the
EmbeddingEngine already L2-normalises its output, IP == cosine similarity.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import faiss
import numpy as np

from app.core.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)


@dataclass
class ChunkRecord:
    """A single stored chunk with its metadata."""
    chunk_id: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore:
    """In-memory FAISS index with chunk metadata."""

    _instance: VectorStore | None = None

    def __init__(self, dimension: int | None = None) -> None:
        dim = dimension or EmbeddingEngine.dimension()
        self._index: faiss.IndexFlatIP = faiss.IndexFlatIP(dim)
        self._records: list[ChunkRecord] = []
        self._next_id: int = 0
        logger.info("FAISS VectorStore initialised (dim=%d).", dim)

    # ── singleton accessor ──────────────────────────────────────────────
    @classmethod
    def get_instance(cls) -> VectorStore:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── write ───────────────────────────────────────────────────────────
    def add_documents(
        self,
        chunks: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> list[int]:
        """
        Embed *chunks*, add them to the FAISS index, and store metadata.

        Parameters
        ----------
        chunks : list[str]
            Text segments to index.
        metadatas : list[dict] | None
            Optional per-chunk metadata (e.g. filename, page number).

        Returns
        -------
        list[int]
            The IDs assigned to the newly added chunks.
        """
        if not chunks:
            return []

        engine = EmbeddingEngine.get_instance()
        vectors = engine.generate_embeddings(chunks)          # (N, dim)

        metas = metadatas or [{} for _ in chunks]
        ids: list[int] = []

        for text, meta in zip(chunks, metas):
            record = ChunkRecord(
                chunk_id=self._next_id,
                text=text,
                metadata=meta,
            )
            self._records.append(record)
            ids.append(self._next_id)
            self._next_id += 1

        self._index.add(vectors)
        logger.info(
            "Added %d chunks to index (total=%d).", len(chunks), self._index.ntotal
        )
        return ids

    # ── read ────────────────────────────────────────────────────────────
    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the *top_k* most similar chunks for *query*.

        Returns
        -------
        list[dict]
            Each dict contains ``text``, ``score``, and ``metadata``.
        """
        if self._index.ntotal == 0:
            return []

        engine = EmbeddingEngine.get_instance()
        query_vec = engine.generate_embeddings([query])       # (1, dim)

        k = min(top_k, self._index.ntotal)
        distances, indices = self._index.search(query_vec, k)

        results: list[dict[str, Any]] = []
        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            record = self._records[int(idx)]
            results.append({
                "text": record.text,
                "score": float(score),
                "metadata": record.metadata,
            })

        return results

    # ── metadata ────────────────────────────────────────────────────────
    @property
    def total_chunks(self) -> int:
        """Return the number of vectors currently in the index."""
        return self._index.ntotal
