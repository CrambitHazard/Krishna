"""
KRISHNA — Quiz routes.

POST /quiz       — generate a multiple-choice quiz on a topic.
POST /quiz/evaluate — evaluate user answers and return score + feedback.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    QuestionFeedbackSchema,
    QuizEvaluateRequest,
    QuizEvaluateResponse,
    QuizQuestionSchema,
    QuizRequest,
    QuizResponse,
)
from app.services.quiz_service import QuizService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

_quiz_service = QuizService()


# ── POST /quiz — generate quiz ─────────────────────────────────────────
@router.post(
    "/",
    response_model=QuizResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a quiz",
    description=(
        "Generates 3-5 multiple-choice questions on a topic, "
        "optionally grounded on uploaded study materials."
    ),
)
async def generate_quiz(payload: QuizRequest) -> QuizResponse:
    """Generate a structured MCQ quiz via the QuizAgent."""

    try:
        result = await _quiz_service.generate_quiz(
            topic=payload.topic,
            num_questions=payload.num_questions,
            use_context=payload.use_context,
        )
    except Exception as exc:
        logger.exception("Quiz generation failed for '%s'", payload.topic[:80])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quiz generation error: {exc}",
        ) from exc

    if not result.questions:
        error_reason = result.metadata.get("error", "LLM returned unparseable output.")
        logger.error(
            "Quiz generation returned 0 questions for '%s': %s",
            payload.topic[:80], error_reason,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to generate quiz questions: {error_reason}",
        )

    return QuizResponse(
        topic=result.topic,
        questions=[
            QuizQuestionSchema(
                question=q.question,
                options=q.options,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
            )
            for q in result.questions
        ],
        total=result.total,
        metadata=result.metadata,
    )


# ── POST /quiz/evaluate — grade user answers ──────────────────────────
@router.post(
    "/evaluate",
    response_model=QuizEvaluateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate quiz answers",
    description=(
        "Accepts user answers and the original quiz data, "
        "returns a score with per-question feedback and explanations."
    ),
)
async def evaluate_quiz(payload: QuizEvaluateRequest) -> QuizEvaluateResponse:
    """Grade user answers against the quiz and return feedback."""

    if len(payload.user_answers) != len(payload.quiz_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Mismatch: {len(payload.user_answers)} answers provided "
                f"for {len(payload.quiz_data)} questions."
            ),
        )

    quiz_dicts = [q.model_dump() for q in payload.quiz_data]

    result = _quiz_service.evaluate_quiz(
        user_answers=payload.user_answers,
        quiz_data=quiz_dicts,
    )

    return QuizEvaluateResponse(
        score=result.score,
        total=result.total,
        percentage=result.percentage,
        correct_questions=[
            QuestionFeedbackSchema(
                question=q.question,
                options=q.options,
                user_answer=q.user_answer,
                correct_answer=q.correct_answer,
                is_correct=q.is_correct,
                explanation=q.explanation,
            )
            for q in result.correct_questions
        ],
        incorrect_questions=[
            QuestionFeedbackSchema(
                question=q.question,
                options=q.options,
                user_answer=q.user_answer,
                correct_answer=q.correct_answer,
                is_correct=q.is_correct,
                explanation=q.explanation,
            )
            for q in result.incorrect_questions
        ],
    )
