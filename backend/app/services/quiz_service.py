"""
KRISHNA — Quiz service.

Orchestrates quiz generation by optionally retrieving context
from the vector store, then delegating to the QuizAgent.

Usage:
    from app.services.quiz_service import QuizService

    svc = QuizService()
    result = await svc.generate_quiz("photosynthesis")
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.quiz_agent import QuizAgent, QuizResult
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


class QuizService:
    """
    High-level service for quiz generation.

    Flow:
      1. (Optional) Retrieve relevant document context via RetrievalService.
      2. Pass topic + context to QuizAgent.
      3. Return structured QuizResult.
    """

    def __init__(self) -> None:
        self._agent = QuizAgent()
        self._retrieval = RetrievalService()

    async def generate_quiz(
        self,
        topic: str,
        *,
        num_questions: int = 5,
        use_context: bool = True,
    ) -> QuizResult:
        """
        Generate a quiz on *topic*.

        Parameters
        ----------
        topic : str
            The subject to quiz on.
        num_questions : int
            Number of MCQs to generate (3-5).
        use_context : bool
            If True, retrieve relevant chunks from the vector store
            to ground the questions on uploaded materials.

        Returns
        -------
        QuizResult
            Contains the structured list of questions.
        """
        context = ""

        # ── Optionally retrieve context from indexed docs ───────────────
        if use_context:
            try:
                results = await self._retrieval.search(topic, top_k=3)
                if results:
                    context = "\n\n---\n\n".join(
                        r["text"] for r in results
                    )
                    logger.info(
                        "QuizService: using %d retrieved chunks for '%s'.",
                        len(results), topic[:60],
                    )
            except Exception as exc:
                logger.warning(
                    "QuizService: retrieval failed (generating without context): %s",
                    exc,
                )

        # ── Generate quiz ───────────────────────────────────────────────
        result = await self._agent.generate(
            topic=topic,
            context=context,
            num_questions=num_questions,
        )

        logger.info(
            "QuizService: generated %d questions for '%s'.",
            result.total, topic[:60],
        )

        return result
