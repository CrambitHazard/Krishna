"""
KRISHNA — Teacher agent (adaptive).

Uses the LLMService to generate a grounded, pedagogical response
based on the user's question and retrieved document context.

Adaptive Teaching
-----------------
Before generating a response, the teacher queries the student's
progress from the database and adapts its teaching style:

  • **Weak topic** (accuracy < 60%): simpler language, more examples,
    analogies, step-by-step breakdowns, revision suggestions.
  • **Moderate topic** (60-80%): balanced explanation with some depth.
  • **Strong topic** (accuracy > 80%): advanced explanation, deeper
    nuances, edge cases, connections to related concepts.
  • **No data**: default balanced teaching style.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.agents.analytics_agent import AnalyticsAgent
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService, LLMServiceError

logger = logging.getLogger(__name__)

# ── adaptive system prompts ─────────────────────────────────────────────

_BASE_PROMPT = """\
You are KRISHNA, an expert AI tutor.

Core rules:
1. Answer the student's question clearly, accurately, and concisely.
2. If context from study materials is provided, base your answer on that
   context.  Cite which source(s) you used (e.g. "According to Source 1 …").
3. If no relevant context is available, answer from your general knowledge
   and explicitly note that no uploaded material was referenced.
4. If you are unsure, say so honestly — do not fabricate facts.
"""

_WEAK_ADDENDUM = """
ADAPTIVE TEACHING MODE — BEGINNER LEVEL:
The student is still building foundational knowledge on this topic.
• Use simple, everyday language — avoid jargon or define it immediately.
• Break down the concept step-by-step.
• Include at least 2 concrete, relatable examples or analogies.
• Summarise key takeaways at the end in bullet points.
• Encourage the student and suggest reviewing the topic again.
• If relevant, suggest specific areas to revise.
"""

_MODERATE_ADDENDUM = """
ADAPTIVE TEACHING MODE — INTERMEDIATE LEVEL:
The student has a decent grasp but hasn't fully mastered this topic.
• Provide a clear, thorough explanation with moderate depth.
• Include 1-2 examples to reinforce understanding.
• Highlight common mistakes or misconceptions.
• Connect the concept to broader ideas where relevant.
"""

_STRONG_ADDENDUM = """
ADAPTIVE TEACHING MODE — ADVANCED LEVEL:
The student already has strong command of this topic.
• Provide an advanced, nuanced explanation.
• Explore edge cases, exceptions, or deeper implications.
• Connect to related advanced concepts.
• Challenge the student with a thought-provoking follow-up question.
• You can use technical terminology freely.
"""


@dataclass
class TeacherResult:
    """Output of the TeacherAgent."""
    answer: str
    agent_name: str = "teacher"
    metadata: dict[str, Any] = field(default_factory=dict)


class TeacherAgent:
    """
    Generates adaptive teaching responses grounded in retrieved context.

    Before calling the LLM, queries the student's progress on the
    topic to adjust the teaching style (simple ↔ advanced).
    """

    def __init__(self) -> None:
        self._llm = LLMService()
        self._db = DatabaseService()
        self._analytics = AnalyticsAgent()

    async def answer(
        self,
        question: str,
        context: str = "",
        **kwargs: Any,
    ) -> TeacherResult:
        """
        Generate an adaptive teaching response for *question*.

        Parameters
        ----------
        question : str
            The student's query.
        context : str
            Concatenated document chunks from the PlannerAgent
            (may be empty if nothing was retrieved).
        """
        # ── Step 1: Determine teaching level ────────────────────────────
        level, level_meta = await self._get_topic_level(question)

        # ── Step 2: Build adaptive prompt ───────────────────────────────
        system_prompt = self._build_system_prompt(level)
        user_prompt = self._build_prompt(question, context)

        # ── Step 3: Generate response ───────────────────────────────────
        try:
            llm_reply = await self._llm.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
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
                "teaching_level": level,
                **level_meta,
                **kwargs,
            },
        )

    # ── adaptive level detection ────────────────────────────────────────

    async def _get_topic_level(
        self, question: str
    ) -> tuple[str, dict[str, Any]]:
        """
        Query progress data and determine the teaching level.

        Extracts key terms from the question and checks progress
        for any matching topic. Returns ("weak"|"moderate"|"strong"|"default")
        and metadata about the match.
        """
        try:
            progress_data = await self._db.get_progress()
        except Exception as exc:
            logger.warning("TeacherAgent: could not fetch progress: %s", exc)
            return "default", {}

        if not progress_data:
            return "default", {"reason": "no_progress_data"}

        # Run analytics on all progress
        analytics = self._analytics.analyse(progress_data)

        # Try to find a matching topic by checking if the question
        # contains any tracked topic name (case-insensitive)
        question_lower = question.lower()

        # Check weak topics first (prioritise helping)
        for t in analytics.weak_topics:
            if t.topic.lower() in question_lower:
                logger.info(
                    "TeacherAgent: topic '%s' is WEAK (%.1f%%, %d attempts).",
                    t.topic, t.accuracy, t.attempts,
                )
                return "weak", {
                    "matched_topic": t.topic,
                    "accuracy": t.accuracy,
                    "attempts": t.attempts,
                    "is_struggling": t.is_struggling,
                }

        # Then moderate
        for t in analytics.moderate_topics:
            if t.topic.lower() in question_lower:
                logger.info(
                    "TeacherAgent: topic '%s' is MODERATE (%.1f%%).",
                    t.topic, t.accuracy,
                )
                return "moderate", {
                    "matched_topic": t.topic,
                    "accuracy": t.accuracy,
                    "attempts": t.attempts,
                }

        # Then strong
        for t in analytics.strong_topics:
            if t.topic.lower() in question_lower:
                logger.info(
                    "TeacherAgent: topic '%s' is STRONG (%.1f%%).",
                    t.topic, t.accuracy,
                )
                return "strong", {
                    "matched_topic": t.topic,
                    "accuracy": t.accuracy,
                    "attempts": t.attempts,
                }

        return "default", {"reason": "no_topic_match"}

    # ── prompt construction ─────────────────────────────────────────────

    @staticmethod
    def _build_system_prompt(level: str) -> str:
        """Build the system prompt with the appropriate teaching addendum."""
        if level == "weak":
            return _BASE_PROMPT + _WEAK_ADDENDUM
        elif level == "strong":
            return _BASE_PROMPT + _STRONG_ADDENDUM
        elif level == "moderate":
            return _BASE_PROMPT + _MODERATE_ADDENDUM
        else:
            return _BASE_PROMPT

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
