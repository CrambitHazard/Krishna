"""
KRISHNA — Quiz routes.

POST /quiz         — generate a multiple-choice quiz on a topic.
POST /quiz/submit  — submit answers for grading + persist to DB.
GET  /progress     — combined progress + analytics + recommendations.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, status

from app.agents.analytics_agent import AnalyticsAgent
from app.models.schemas import (
    ProgressResponse,
    QuestionFeedbackSchema,
    QuizQuestionSchema,
    QuizRequest,
    QuizResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    TopicInsightSchema,
    TopicProgressSchema,
)
from app.services.database_service import DatabaseService
from app.services.quiz_service import QuizService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

_quiz_service = QuizService()
_db = DatabaseService()
_analytics = AnalyticsAgent()


# ═══════════════════════════════════════════════════════════════════════
#  POST /quiz — generate quiz
# ═══════════════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════════════
#  POST /quiz/submit — grade answers + persist
# ═══════════════════════════════════════════════════════════════════════
@router.post(
    "/submit",
    response_model=QuizSubmitResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit quiz answers",
    description=(
        "Submit user answers for grading. Returns score with "
        "per-question feedback. Saves attempt and updates progress."
    ),
)
async def submit_quiz(payload: QuizSubmitRequest) -> QuizSubmitResponse:
    """Grade user answers, persist attempt, update progress."""

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

    # ── Persist to database ─────────────────────────────────────────
    session_id = str(uuid.uuid4())
    try:
        await _db.save_quiz_attempt(
            session_id=session_id,
            topic=payload.topic,
            score=result.score,
            total=result.total,
            details=result.to_dict(),
        )
        await _db.update_progress(
            topic=payload.topic,
            score=result.score,
            total=result.total,
        )
    except Exception as exc:
        logger.warning("Failed to persist quiz attempt: %s", exc)

    return QuizSubmitResponse(
        score=result.score,
        total=result.total,
        percentage=result.percentage,
        topic=payload.topic,
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


# ═══════════════════════════════════════════════════════════════════════
#  GET /progress — combined progress + analytics
# ═══════════════════════════════════════════════════════════════════════
@router.get(
    "/progress",
    response_model=ProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get learning progress",
    description=(
        "Returns per-topic progress data combined with analytics: "
        "weak/strong topic classification and study recommendations."
    ),
)
async def get_progress() -> ProgressResponse:
    """Return progress + weak topics + recommendations in one call."""

    progress_data = await _db.get_progress()
    analytics_result = _analytics.analyse(progress_data)

    return ProgressResponse(
        topics=[
            TopicProgressSchema(
                topic=p.get("topic", ""),
                accuracy=p.get("accuracy", 0.0),
                attempts=p.get("attempts", 0),
                total_score=p.get("total_score", 0),
                total_questions=p.get("total_questions", 0),
                last_updated=p.get("last_updated", ""),
            )
            for p in progress_data
        ],
        weak_topics=[
            TopicInsightSchema(
                topic=t.topic,
                accuracy=t.accuracy,
                attempts=t.attempts,
                status=t.status,
                is_struggling=t.is_struggling,
            )
            for t in analytics_result.weak_topics
        ],
        strong_topics=[
            TopicInsightSchema(
                topic=t.topic,
                accuracy=t.accuracy,
                attempts=t.attempts,
                status=t.status,
                is_struggling=t.is_struggling,
            )
            for t in analytics_result.strong_topics
        ],
        recommendations=analytics_result.recommendations,
        summary=analytics_result.summary,
    )
