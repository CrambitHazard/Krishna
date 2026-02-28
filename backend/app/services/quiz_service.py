"""
KRISHNA — Quiz service.

Orchestrates quiz generation and evaluation.

Usage:
    from app.services.quiz_service import QuizService

    svc = QuizService()
    result = await svc.generate_quiz("photosynthesis")
    evaluation = svc.evaluate_quiz(user_answers, quiz_data)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.agents.quiz_agent import QuizAgent, QuizResult
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


@dataclass
class QuestionFeedback:
    """Feedback for a single question."""
    question: str
    options: list[str]
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


@dataclass
class EvaluationResult:
    """Output of quiz evaluation."""
    score: int
    total: int
    percentage: float
    correct_questions: list[QuestionFeedback] = field(default_factory=list)
    incorrect_questions: list[QuestionFeedback] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "total": self.total,
            "percentage": self.percentage,
            "correct_questions": [
                {
                    "question": q.question,
                    "options": q.options,
                    "user_answer": q.user_answer,
                    "correct_answer": q.correct_answer,
                    "is_correct": q.is_correct,
                    "explanation": q.explanation,
                }
                for q in self.correct_questions
            ],
            "incorrect_questions": [
                {
                    "question": q.question,
                    "options": q.options,
                    "user_answer": q.user_answer,
                    "correct_answer": q.correct_answer,
                    "is_correct": q.is_correct,
                    "explanation": q.explanation,
                }
                for q in self.incorrect_questions
            ],
        }


class QuizService:
    """
    High-level service for quiz generation and evaluation.

    Flow (generate):
      1. (Optional) Retrieve relevant document context.
      2. Pass topic + context to QuizAgent.
      3. Return structured QuizResult.

    Flow (evaluate):
      1. Accept user answers + original quiz data.
      2. Compare each answer.
      3. Return score + per-question feedback.
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
        """Generate a quiz on *topic*."""
        context = ""

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

    # ── Evaluation ──────────────────────────────────────────────────────
    def evaluate_quiz(
        self,
        user_answers: list[str],
        quiz_data: list[dict[str, Any]],
    ) -> EvaluationResult:
        """
        Evaluate user answers against the quiz.

        Parameters
        ----------
        user_answers : list[str]
            The user's answers, e.g. ["A", "C", "B", "D", "A"].
        quiz_data : list[dict]
            The original quiz questions (each with question, options,
            correct_answer, explanation).

        Returns
        -------
        EvaluationResult
            Score, percentage, and per-question feedback split into
            correct and incorrect lists.
        """
        correct_questions: list[QuestionFeedback] = []
        incorrect_questions: list[QuestionFeedback] = []

        total = min(len(user_answers), len(quiz_data))

        for i in range(total):
            q = quiz_data[i]
            user_ans = user_answers[i].strip().upper()
            correct_ans = q.get("correct_answer", "").strip().upper()

            is_correct = user_ans == correct_ans

            feedback = QuestionFeedback(
                question=q.get("question", ""),
                options=q.get("options", []),
                user_answer=user_ans,
                correct_answer=correct_ans,
                is_correct=is_correct,
                explanation=q.get("explanation", ""),
            )

            if is_correct:
                correct_questions.append(feedback)
            else:
                incorrect_questions.append(feedback)

        score = len(correct_questions)
        percentage = round((score / total) * 100, 1) if total > 0 else 0.0

        logger.info(
            "QuizService: evaluated %d questions — score %d/%d (%.1f%%).",
            total, score, total, percentage,
        )

        return EvaluationResult(
            score=score,
            total=total,
            percentage=percentage,
            correct_questions=correct_questions,
            incorrect_questions=incorrect_questions,
        )

