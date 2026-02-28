"""
KRISHNA — Quiz routes.

POST /quiz — generate a multiple-choice quiz on a topic.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    QuizQuestionSchema,
    QuizRequest,
    QuizResponse,
)
from app.services.quiz_service import QuizService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

_quiz_service = QuizService()


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
