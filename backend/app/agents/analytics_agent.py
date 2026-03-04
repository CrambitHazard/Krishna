"""
KRISHNA — Analytics agent.

Deterministic agent that analyses learning progress data and
categorises topics into weak / strong / improving, then generates
actionable study recommendations.

No LLM calls — pure rule-based logic.

Rules
-----
  • accuracy < 60%  → weak
  • accuracy > 80%  → strong
  • 60% ≤ accuracy ≤ 80% → moderate
  • attempts ≥ 3 with accuracy < 60% → struggling (high priority)
  • attempts == 1 → needs more practice (insufficient data)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ── thresholds ──────────────────────────────────────────────────────────
_WEAK_THRESHOLD = 60.0
_STRONG_THRESHOLD = 80.0
_STRUGGLING_MIN_ATTEMPTS = 3


@dataclass
class TopicInsight:
    """Analysis of a single topic."""
    topic: str
    accuracy: float
    attempts: int
    status: str           # "weak" | "strong" | "moderate"
    is_struggling: bool   # many attempts but still weak


@dataclass
class AnalyticsResult:
    """Output of the AnalyticsAgent."""
    weak_topics: list[TopicInsight] = field(default_factory=list)
    strong_topics: list[TopicInsight] = field(default_factory=list)
    moderate_topics: list[TopicInsight] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def _insight(t: TopicInsight) -> dict[str, Any]:
            return {
                "topic": t.topic,
                "accuracy": t.accuracy,
                "attempts": t.attempts,
                "status": t.status,
                "is_struggling": t.is_struggling,
            }

        return {
            "weak_topics": [_insight(t) for t in self.weak_topics],
            "strong_topics": [_insight(t) for t in self.strong_topics],
            "moderate_topics": [_insight(t) for t in self.moderate_topics],
            "recommendations": self.recommendations,
            "summary": self.summary,
        }


class AnalyticsAgent:
    """
    Deterministic analytics agent.

    Input:  list of progress dicts (from DatabaseService.get_progress)
    Output: AnalyticsResult with categorised topics + recommendations
    """

    def analyse(self, progress_data: list[dict[str, Any]]) -> AnalyticsResult:
        """
        Analyse progress data and return structured insights.

        Parameters
        ----------
        progress_data : list[dict]
            Each dict has: topic, accuracy, attempts, total_score,
            total_questions, last_updated.
        """
        weak: list[TopicInsight] = []
        strong: list[TopicInsight] = []
        moderate: list[TopicInsight] = []
        recommendations: list[str] = []

        if not progress_data:
            return AnalyticsResult(
                recommendations=["No progress data yet. Start by taking a quiz!"],
                summary={"total_topics": 0},
            )

        for entry in progress_data:
            topic = entry.get("topic", "unknown")
            accuracy = float(entry.get("accuracy", 0))
            attempts = int(entry.get("attempts", 0))

            is_struggling = (
                accuracy < _WEAK_THRESHOLD
                and attempts >= _STRUGGLING_MIN_ATTEMPTS
            )

            if accuracy < _WEAK_THRESHOLD:
                status = "weak"
            elif accuracy > _STRONG_THRESHOLD:
                status = "strong"
            else:
                status = "moderate"

            insight = TopicInsight(
                topic=topic,
                accuracy=accuracy,
                attempts=attempts,
                status=status,
                is_struggling=is_struggling,
            )

            if status == "weak":
                weak.append(insight)
            elif status == "strong":
                strong.append(insight)
            else:
                moderate.append(insight)

        # ── sort: worst first for weak, best first for strong ───────────
        weak.sort(key=lambda t: t.accuracy)
        strong.sort(key=lambda t: t.accuracy, reverse=True)

        # ── generate recommendations ────────────────────────────────────
        recommendations = self._generate_recommendations(weak, strong, moderate)

        # ── summary stats ───────────────────────────────────────────────
        all_accuracies = [float(e.get("accuracy", 0)) for e in progress_data]
        summary = {
            "total_topics": len(progress_data),
            "weak_count": len(weak),
            "strong_count": len(strong),
            "moderate_count": len(moderate),
            "overall_accuracy": round(
                sum(all_accuracies) / len(all_accuracies), 1
            ) if all_accuracies else 0.0,
        }

        logger.info(
            "AnalyticsAgent: %d topics — %d weak, %d moderate, %d strong.",
            len(progress_data), len(weak), len(moderate), len(strong),
        )

        return AnalyticsResult(
            weak_topics=weak,
            strong_topics=strong,
            moderate_topics=moderate,
            recommendations=recommendations,
            summary=summary,
        )

    # ── recommendation engine ───────────────────────────────────────────
    @staticmethod
    def _generate_recommendations(
        weak: list[TopicInsight],
        strong: list[TopicInsight],
        moderate: list[TopicInsight],
    ) -> list[str]:
        recs: list[str] = []

        # Struggling topics (highest priority)
        struggling = [t for t in weak if t.is_struggling]
        if struggling:
            names = ", ".join(t.topic for t in struggling)
            recs.append(
                f"You're struggling with: {names}. "
                f"Consider reviewing the study material before retaking quizzes."
            )

        # Weak topics (need work)
        just_weak = [t for t in weak if not t.is_struggling]
        if just_weak:
            names = ", ".join(t.topic for t in just_weak)
            recs.append(
                f"Weak areas to focus on: {names}. "
                f"Try taking more quizzes to improve."
            )

        # Single-attempt topics
        low_attempts = [t for t in weak + moderate if t.attempts == 1]
        if low_attempts:
            names = ", ".join(t.topic for t in low_attempts)
            recs.append(
                f"Topics with only 1 attempt: {names}. "
                f"Take more quizzes for a reliable accuracy reading."
            )

        # Moderate topics (close to strong)
        almost_strong = [t for t in moderate if t.accuracy >= 70]
        if almost_strong:
            names = ", ".join(t.topic for t in almost_strong)
            recs.append(
                f"Almost there on: {names}. "
                f"One more good quiz could push these to strong!"
            )

        # Strong topics (positive reinforcement)
        if strong:
            names = ", ".join(t.topic for t in strong)
            recs.append(
                f"Great work on: {names}! Keep it up."
            )

        if not recs:
            recs.append("Keep practising to build your progress profile!")

        return recs
