"""
KRISHNA — Analytics routes.

GET /analytics — analyse learning progress and return insights.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, status

from app.agents.analytics_agent import AnalyticsAgent
from app.models.schemas import (
    AnalyticsResponse,
    TopicInsightSchema,
)
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

_analytics = AnalyticsAgent()
_db = DatabaseService()


@router.get(
    "/",
    response_model=AnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get learning analytics",
    description=(
        "Analyses all progress data and returns weak/strong topics "
        "with actionable study recommendations."
    ),
)
async def get_analytics() -> AnalyticsResponse:
    """Run the analytics agent on all progress data."""

    progress_data = await _db.get_progress()

    result = _analytics.analyse(progress_data)

    return AnalyticsResponse(
        weak_topics=[
            TopicInsightSchema(
                topic=t.topic,
                accuracy=t.accuracy,
                attempts=t.attempts,
                status=t.status,
                is_struggling=t.is_struggling,
            )
            for t in result.weak_topics
        ],
        strong_topics=[
            TopicInsightSchema(
                topic=t.topic,
                accuracy=t.accuracy,
                attempts=t.attempts,
                status=t.status,
                is_struggling=t.is_struggling,
            )
            for t in result.strong_topics
        ],
        moderate_topics=[
            TopicInsightSchema(
                topic=t.topic,
                accuracy=t.accuracy,
                attempts=t.attempts,
                status=t.status,
                is_struggling=t.is_struggling,
            )
            for t in result.moderate_topics
        ],
        recommendations=result.recommendations,
        summary=result.summary,
    )
