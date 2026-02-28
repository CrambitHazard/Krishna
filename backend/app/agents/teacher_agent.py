"""
KRISHNA — Teacher agent.

Uses the LLMService to generate a grounded, pedagogical response
based on the user's question and retrieved document context.

This is the "Execute" phase of the Plan-and-Execute pattern.
The teacher receives the context assembled by the PlannerAgent
and crafts a teaching response through the LLM.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.services.llm_service import LLMService, LLMServiceError

logger = logging.getLogger(__name__)

# ── System prompt ───────────────────────────────────────────────────────
_SYSTEM_PROMPT = """\
You are KRISHNA, an expert AI tutor.

Rules:
1. Answer the student's question clearly, accurately, and concisely.
2. If context from study materials is provided, base your answer on that
   context.  Cite which source(s) you used (e.g. "According to Source 1 …").
3. If no relevant context is available, answer from your general knowledge
   and explicitly note that no uploaded material was referenced.
4. Use a friendly, encouraging tone.  Break down complex topics with
   analogies and examples.
5. If you are unsure, say so honestly — do not fabricate facts.
"""


@dataclass
class TeacherResult:
    """Output of the TeacherAgent."""
    answer: str
    agent_name: str = "teacher"
    metadata: dict[str, Any] = field(default_factory=dict)


class TeacherAgent:
    """
    Generates teaching responses grounded in retrieved context.

    Uses OpenRouter via LLMService.  If the LLM call fails, falls back
    to a graceful degradation message rather than crashing.
    """

    def __init__(self) -> None:
        self._llm = LLMService()

    async def answer(
        self,
        question: str,
        context: str = "",
        **kwargs: Any,
    ) -> TeacherResult:
        """
        Generate a teaching response for *question*.

        Parameters
        ----------
        question : str
            The student's query.
        context : str
            Concatenated document chunks from the PlannerAgent
            (may be empty if nothing was retrieved).
        """
        user_prompt = self._build_prompt(question, context)

        try:
            llm_reply = await self._llm.generate_response(
                prompt=user_prompt,
                system_prompt=_SYSTEM_PROMPT,
            )
        except LLMServiceError as exc:
            logger.error("TeacherAgent LLM call failed: %s", exc)
            llm_reply = (
                "I'm having trouble connecting to my language model right now. "
                "Please try again in a moment."
            )

        return TeacherResult(
            answer=llm_reply,
            metadata={
                "had_context": bool(context),
                **kwargs,
            },
        )

    # ── prompt construction ─────────────────────────────────────────────

    @staticmethod
    def _build_prompt(question: str, context: str) -> str:
        """
        Build the user-role prompt sent to the LLM.

        If context is available, it is prepended so the model grounds
        its answer on retrieved material.
        """
        parts: list[str] = []

        if context:
            parts.append(
                "The following excerpts were retrieved from the student's "
                "uploaded study materials:\n\n"
                f"{context}\n\n"
                "---\n"
            )

        parts.append(f"Student's question:\n{question}")

        return "\n".join(parts)
