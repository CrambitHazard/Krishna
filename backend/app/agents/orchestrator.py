"""
KRISHNA — Orchestrator agent.

Decides which sub-agent (teacher, planner, etc.) should handle an
incoming query. Placeholder for the multi-agent routing logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Standardised wrapper returned by every agent."""

    reply: str
    agent_name: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Routes queries to the appropriate sub-agent."""

    def __init__(self) -> None:
        # Future: initialise sub-agents here
        pass

    async def handle(self, message: str, **kwargs: Any) -> AgentResult:
        """
        Decide which agent handles *message* and return the result.

        Currently returns a placeholder response.
        """
        return AgentResult(
            reply=f"[Orchestrator] Received: {message}",
            agent_name="orchestrator",
            metadata=kwargs,
        )
