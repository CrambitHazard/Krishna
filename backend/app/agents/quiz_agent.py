"""
KRISHNA — Quiz agent.

Generates structured multiple-choice quizzes from a topic or
retrieved document context by prompting the LLM with a strict
JSON output schema.

The agent follows the tool-use pattern:
  1. Accept topic + optional context.
  2. Build a constrained prompt requesting JSON output.
  3. Call LLMService.
  4. Parse and validate the response into QuizResult.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from app.services.llm_service import LLMService, LLMServiceError

logger = logging.getLogger(__name__)

# ── System prompt ───────────────────────────────────────────────────────
_SYSTEM_PROMPT = """\
You are KRISHNA, an expert AI tutor that creates educational quizzes.

Rules:
1. Generate exactly {num_questions} multiple-choice questions.
2. Each question must have exactly 4 options labelled A, B, C, D.
3. Provide the correct answer as a single letter (A, B, C, or D).
4. Write a brief explanation (1-2 sentences) for the correct answer.
5. If context from study materials is provided, base questions on that context.
6. If no context is given, generate questions from general knowledge on the topic.
7. Make questions progressively harder (easy → medium → hard).
8. Respond ONLY with valid JSON — no markdown fences, no extra text.

Required JSON format:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A",
      "explanation": "..."
    }}
  ]
}}
"""


@dataclass
class QuizQuestion:
    """A single quiz question."""
    question: str
    options: list[str]
    correct_answer: str
    explanation: str


@dataclass
class QuizResult:
    """Output of the QuizAgent."""
    topic: str
    questions: list[QuizQuestion] = field(default_factory=list)
    agent_name: str = "quiz"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.questions)

    def to_dict(self) -> dict[str, Any]:
        """Serialise for JSON responses."""
        return {
            "topic": self.topic,
            "questions": [
                {
                    "question": q.question,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                }
                for q in self.questions
            ],
            "total": self.total,
            "metadata": self.metadata,
        }


class QuizAgent:
    """
    Generates MCQ quizzes by prompting the LLM with strict JSON output.

    Includes robust parsing with fallback extraction if the LLM
    wraps the JSON in markdown fences.
    """

    def __init__(self) -> None:
        self._llm = LLMService()

    async def generate(
        self,
        topic: str,
        context: str = "",
        num_questions: int = 5,
    ) -> QuizResult:
        """
        Generate a quiz for *topic*.

        Parameters
        ----------
        topic : str
            The subject to quiz on.
        context : str
            Optional retrieved document text to ground the questions.
        num_questions : int
            Number of questions to generate (3-5).
        """
        num_questions = max(3, min(num_questions, 5))

        user_prompt = self._build_prompt(topic, context, num_questions)
        system = _SYSTEM_PROMPT.format(num_questions=num_questions)

        try:
            raw = await self._llm.generate_response(
                prompt=user_prompt,
                system_prompt=system,
                max_tokens=2048,
                temperature=0.6,
            )
        except LLMServiceError as exc:
            logger.error("QuizAgent LLM call failed: %s", exc)
            return QuizResult(
                topic=topic,
                metadata={"error": str(exc)},
            )

        # Parse the LLM output into structured questions
        questions = self._parse_response(raw)

        metadata: dict[str, Any] = {
            "had_context": bool(context),
            "requested": num_questions,
            "generated": len(questions),
        }

        # If parsing failed, include the raw output for debugging
        if not questions:
            logger.error(
                "QuizAgent: parsed 0 questions from LLM output: %s", raw[:500]
            )
            metadata["error"] = (
                f"LLM responded but output could not be parsed. "
                f"Raw (first 300 chars): {raw[:300]}"
            )

        return QuizResult(
            topic=topic,
            questions=questions,
            metadata=metadata,
        )

    # ── prompt construction ─────────────────────────────────────────────

    @staticmethod
    def _build_prompt(topic: str, context: str, num_questions: int) -> str:
        parts: list[str] = []

        if context:
            parts.append(
                "Use the following study material as the basis for your questions:\n\n"
                f"{context}\n\n---\n"
            )

        parts.append(
            f"Generate {num_questions} multiple-choice questions about: {topic}"
        )
        return "\n".join(parts)

    # ── response parsing ────────────────────────────────────────────────

    @staticmethod
    def _parse_response(raw: str) -> list[QuizQuestion]:
        """
        Parse the LLM's JSON response into QuizQuestion objects.

        Handles common LLM quirks:
          • Wrapping JSON in ```json ... ``` fences.
          • Extra text before/after the JSON block.
        """
        text = raw.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        # Try to find the JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            logger.error("No JSON found in quiz response: %s", text[:200])
            return []

        json_str = text[start:end]

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse quiz JSON: %s — %s", exc, json_str[:200])
            return []

        raw_questions = data.get("questions", [])
        questions: list[QuizQuestion] = []

        for q in raw_questions:
            try:
                questions.append(
                    QuizQuestion(
                        question=q["question"],
                        options=q["options"],
                        correct_answer=q["correct_answer"],
                        explanation=q.get("explanation", ""),
                    )
                )
            except (KeyError, TypeError) as exc:
                logger.warning("Skipping malformed question: %s — %s", exc, q)
                continue

        return questions
