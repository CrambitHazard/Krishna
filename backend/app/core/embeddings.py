"""
KRISHNA — Embedding engine.

Wraps *sentence-transformers* (all-MiniLM-L6-v2) behind a lazy-loaded
singleton so the model is downloaded / loaded only once, on first use.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# ── Model config ────────────────────────────────────────────────────────
_MODEL_NAME: str = "all-MiniLM-L6-v2"
_EMBEDDING_DIM: int = 384          # output dimension of MiniLM-L6-v2


class EmbeddingEngine:
    """Generates dense vector embeddings using sentence-transformers."""

    _instance: EmbeddingEngine | None = None   # singleton guard

    def __init__(self) -> None:
        self._model = None  # lazy-loaded

    # ── singleton accessor ──────────────────────────────────────────────
    @classmethod
    def get_instance(cls) -> EmbeddingEngine:
        """Return the global EmbeddingEngine (creates it on first call)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── lazy model loading ──────────────────────────────────────────────
    def _load_model(self):
        """Load the sentence-transformer model on first encode call."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model '%s' …", _MODEL_NAME)
            self._model = SentenceTransformer(_MODEL_NAME)
            logger.info("Embedding model ready (dim=%d).", _EMBEDDING_DIM)

    # ── public API ──────────────────────────────────────────────────────
    @staticmethod
    def dimension() -> int:
        """Return the embedding vector dimensionality."""
        return _EMBEDDING_DIM

    def generate_embeddings(self, text_list: list[str]) -> NDArray[np.float32]:
        """
        Encode a list of strings into an (N, 384) float32 numpy matrix.

        Parameters
        ----------
        text_list : list[str]
            Texts to embed.

        Returns
        -------
        np.ndarray
            Shape ``(len(text_list), 384)`` — one row per input text.
        """
        self._load_model()
        vectors: NDArray[np.float32] = self._model.encode(
            text_list,
            convert_to_numpy=True,
            normalize_embeddings=True,   # unit-norm → cosine = dot product
            show_progress_bar=False,
        )
        return vectors.astype(np.float32)
