"""
KRISHNA — Quiz routes.

POST /quiz            — generate a multiple-choice quiz on a topic.
POST /quiz/evaluate   — evaluate user answers and return score + feedback.
GET  /quiz/progress   — retrieve learning progress.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.models.schemas import (
    QuestionFeedbackSchema,
    QuizEvaluateRequest,
    QuizEvaluateResponse,
    QuizQuestionSchema,
    QuizRequest,
    QuizResponse,
)
from app.services.database_service import DatabaseService
from app.services.quiz_service import QuizService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

_quiz_service = QuizService()
_db = DatabaseService()


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

    # ── Persist to database (fire-and-forget) ───────────────────────
    topic = quiz_dicts[0].get("question", "unknown")[:60] if quiz_dicts else "unknown"
    # Use a proper topic if one was embedded in the request
    session_id = str(uuid.uuid4())
    try:
        await _db.save_quiz_attempt(
            session_id=session_id,
            topic=topic,
            score=result.score,
            total=result.total,
            details=result.to_dict(),
        )
        await _db.update_progress(
            topic=topic,
            score=result.score,
            total=result.total,
        )
    except Exception as exc:
        logger.warning("Failed to persist quiz attempt: %s", exc)

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


# ── GET /quiz/progress — learning progress ─────────────────────────────
@router.get(
    "/progress",
    status_code=status.HTTP_200_OK,
    summary="Get learning progress",
    description="Retrieve per-topic learning progress (accuracy, attempts).",
)
async def get_progress(
    topic: str | None = Query(None, description="Filter by topic"),
) -> list[dict]:
    """Return progress for a specific topic or all topics."""
    return await _db.get_progress(topic=topic)
