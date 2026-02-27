"""
KRISHNA — Teacher agent.

Responsible for explaining concepts, answering questions about
uploaded study material, and providing Socratic-style tutoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TeacherResult:
    reply: str
    metadata: dict[str, Any] = field(default_factory=dict)


class TeacherAgent:
    """Explains concepts from the knowledge base."""

    async def answer(self, question: str, **kwargs: Any) -> TeacherResult:
        """Placeholder — real LLM call goes here."""
        return TeacherResult(
            reply=f"[TeacherAgent] Placeholder answer for: {question}",
            metadata=kwargs,
        )
