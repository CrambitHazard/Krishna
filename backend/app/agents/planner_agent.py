"""
KRISHNA — Planner agent.

Determines the retrieval strategy for a user query.

Responsibilities:
  1. Decide how many chunks to retrieve (top_k).
  2. Call the RetrievalService to fetch relevant document context.
  3. Return the retrieved chunks in a structured result so the
     downstream TeacherAgent can use them to generate a grounded answer.

This is the "Plan" phase of the Plan-and-Execute pattern described
in the AI Agents Architect skill.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

# ── tunables ────────────────────────────────────────────────────────────
_DEFAULT_TOP_K = 3
_MIN_RELEVANCE_SCORE = 0.15     # discard chunks below this similarity


@dataclass
class RetrievedChunk:
    """A single chunk surfaced by the planner."""
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlannerResult:
    """Output of the PlannerAgent — contains the retrieval plan + fetched context."""
    query: str
    strategy: str                             # human-readable label
    chunks: list[RetrievedChunk] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_context(self) -> bool:
        return len(self.chunks) > 0

    def context_text(self) -> str:
        """Concatenate retrieved chunks into a single context block."""
        if not self.chunks:
            return ""
        parts = [
            f"[Source {i+1} | score {c.score:.2f}]\n{c.text}"
            for i, c in enumerate(self.chunks)
        ]
        return "\n\n---\n\n".join(parts)

    def source_list(self) -> list[dict[str, Any]]:
        """Return a list of source references for the final response."""
        return [
            {
                "chunk_index": c.metadata.get("chunk_index"),
                "filename": c.metadata.get("filename", "unknown"),
                "document_id": c.metadata.get("document_id", ""),
                "score": round(c.score, 4),
            }
            for c in self.chunks
        ]


class PlannerAgent:
    """
    Determines retrieval strategy and fetches relevant document chunks.

    Currently uses a simple single-pass dense retrieval with a relevance
    threshold.  Future enhancements:
      • Query classification (factual / conceptual / procedural)
      • Adaptive top_k based on query complexity
      • Hybrid search (keyword + semantic)
    """

    def __init__(self) -> None:
        self._retrieval = RetrievalService()

    async def plan(
        self,
        query: str,
        *,
        top_k: int = _DEFAULT_TOP_K,
    ) -> PlannerResult:
        """
        Execute the retrieval plan for *query*.

        Steps
        -----
        1. Call the vector store via RetrievalService.
        2. Filter out low-relevance results.
        3. Package everything into a PlannerResult.
        """
        logger.info("PlannerAgent: planning retrieval for '%s'", query[:80])

        # ── Step 1: retrieve ────────────────────────────────────────────
        raw_results = await self._retrieval.search(query, top_k=top_k)

        # ── Step 2: filter by relevance threshold ───────────────────────
        chunks: list[RetrievedChunk] = []
        for r in raw_results:
            if r["score"] >= _MIN_RELEVANCE_SCORE:
                chunks.append(
                    RetrievedChunk(
                        text=r["text"],
                        score=r["score"],
                        metadata=r.get("metadata", {}),
                    )
                )

        strategy = (
            f"dense_retrieval(top_k={top_k}, "
            f"threshold={_MIN_RELEVANCE_SCORE}, "
            f"returned={len(chunks)})"
        )

        logger.info(
            "PlannerAgent: retrieved %d/%d chunks above threshold %.2f",
            len(chunks), len(raw_results), _MIN_RELEVANCE_SCORE,
        )

        return PlannerResult(
            query=query,
            strategy=strategy,
            chunks=chunks,
            metadata={"top_k": top_k, "raw_count": len(raw_results)},
        )
