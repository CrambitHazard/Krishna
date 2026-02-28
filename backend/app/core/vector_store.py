"""
KRISHNA — FAISS vector store with disk persistence.

Provides a FAISS index with metadata bookkeeping so we can
map vector IDs back to the original text chunks plus their metadata.

The index uses inner-product search (IndexFlatIP) — because the
EmbeddingEngine already L2-normalises its output, IP == cosine similarity.

Persistence
-----------
The index and chunk records are saved to disk after every write.
On startup, if a saved index exists, it is loaded automatically —
so uploaded documents survive server restarts.

Storage layout (inside DATA_DIR):
    faiss_index/
        index.bin        ← the FAISS binary index
        records.json     ← chunk texts + metadata
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.core.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)

# ── persistence directory ───────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "faiss_index"
_INDEX_PATH = _DATA_DIR / "index.bin"
_RECORDS_PATH = _DATA_DIR / "records.json"


@dataclass
class ChunkRecord:
    """A single stored chunk with its metadata."""
    chunk_id: int
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ChunkRecord:
        return cls(
            chunk_id=d["chunk_id"],
            text=d["text"],
            metadata=d.get("metadata", {}),
        )


class VectorStore:
    """FAISS index with chunk metadata and disk persistence."""

    _instance: VectorStore | None = None

    def __init__(self, dimension: int | None = None) -> None:
        dim = dimension or EmbeddingEngine.dimension()
        self._dim = dim
        self._index: faiss.IndexFlatIP = faiss.IndexFlatIP(dim)
        self._records: list[ChunkRecord] = []
        self._next_id: int = 0

        # Try to load existing index from disk
        self._load()

        logger.info(
            "FAISS VectorStore ready (dim=%d, chunks=%d).",
            dim, self._index.ntotal,
        )

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
        Embed *chunks*, add them to the FAISS index, store metadata,
        and persist to disk.

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

        # Persist after every write
        self._save()

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

    # ── persistence ─────────────────────────────────────────────────────
    def _save(self) -> None:
        """Save the FAISS index and chunk records to disk."""
        try:
            _DATA_DIR.mkdir(parents=True, exist_ok=True)

            # Save FAISS index
            faiss.write_index(self._index, str(_INDEX_PATH))

            # Save records as JSON
            records_data = {
                "next_id": self._next_id,
                "records": [r.to_dict() for r in self._records],
            }
            _RECORDS_PATH.write_text(
                json.dumps(records_data, ensure_ascii=False),
                encoding="utf-8",
            )

            logger.debug(
                "Saved FAISS index (%d vectors) and %d records to %s.",
                self._index.ntotal, len(self._records), _DATA_DIR,
            )
        except Exception as exc:
            logger.error("Failed to save FAISS index to disk: %s", exc)

    def _load(self) -> None:
        """Load the FAISS index and chunk records from disk (if they exist)."""
        if not _INDEX_PATH.exists() or not _RECORDS_PATH.exists():
            logger.info("No saved FAISS index found — starting fresh.")
            return

        try:
            # Load FAISS index
            self._index = faiss.read_index(str(_INDEX_PATH))

            # Load records
            raw = _RECORDS_PATH.read_text(encoding="utf-8")
            data = json.loads(raw)
            self._next_id = data.get("next_id", 0)
            self._records = [
                ChunkRecord.from_dict(r) for r in data.get("records", [])
            ]

            logger.info(
                "Loaded FAISS index from disk: %d vectors, %d records.",
                self._index.ntotal, len(self._records),
            )
        except Exception as exc:
            logger.error(
                "Failed to load FAISS index from disk: %s — starting fresh.", exc
            )
            dim = self._dim
            self._index = faiss.IndexFlatIP(dim)
            self._records = []
            self._next_id = 0
