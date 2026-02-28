"""
KRISHNA — Orchestrator agent.

Entry point for all user queries.  Implements the Plan-and-Execute
multi-agent pattern:

    User query
      → Orchestrator.handle()
        → PlannerAgent.plan()       # retrieve relevant context
        → TeacherAgent.answer()     # generate grounded response
      → structured OrchestratorResult

Design notes (from AI Agents Architect skill):
  • Each agent has a single responsibility.
  • The orchestrator owns the control flow — sub-agents are stateless.
  • Errors in any agent are caught and surfaced, never silently swallowed.
  • Iteration limits aren't needed yet (linear pipeline), but the
    architecture supports adding a ReAct loop later.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from app.agents.planner_agent import PlannerAgent
from app.agents.teacher_agent import TeacherAgent

logger = logging.getLogger(__name__)


# ── Structured output ──────────────────────────────────────────────────
@dataclass
class OrchestratorResult:
    """
    Final structured output returned by the orchestrator.

    Matches the contract requested by the user:
        { "answer": "...", "sources": [...] }
    plus additional agent metadata.
    """
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    agent: str = "orchestrator"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict (for JSON responses)."""
        return {
            "answer": self.answer,
            "sources": self.sources,
            "agent": self.agent,
            "metadata": self.metadata,
        }


class Orchestrator:
    """
    Central controller — routes every user query through the
    Planner → Retrieval → Teacher pipeline and returns a
    structured result.
    """

    def __init__(self) -> None:
        self._planner = PlannerAgent()
        self._teacher = TeacherAgent()
        logger.info("Orchestrator initialised with Planner + Teacher agents.")

    async def handle(
        self,
        message: str,
        **kwargs: Any,
    ) -> OrchestratorResult:
        """
        Full agent pipeline for *message*.

        Steps
        -----
        1. **Plan** — PlannerAgent determines retrieval strategy and
           fetches relevant chunks from the vector store.
        2. **Teach** — TeacherAgent generates a grounded answer using
           the retrieved context and the LLM.
        3. **Package** — Assemble the structured result with sources.

        Returns
        -------
        OrchestratorResult
            Contains ``answer``, ``sources``, ``agent``, and ``metadata``.
        """
        t0 = time.perf_counter()

        # ── Step 1: Plan + Retrieve ─────────────────────────────────────
        logger.info("Orchestrator: starting pipeline for '%s'", message[:80])

        planner_result = await self._planner.plan(message)

        # ── Step 2: Teach ───────────────────────────────────────────────
        context_text = planner_result.context_text()

        teacher_result = await self._teacher.answer(
            question=message,
            context=context_text,
        )

        # ── Step 3: Package ─────────────────────────────────────────────
        elapsed = round(time.perf_counter() - t0, 3)

        sources = planner_result.source_list()

        result = OrchestratorResult(
            answer=teacher_result.answer,
            sources=sources,
            agent="orchestrator",
            metadata={
                "strategy": planner_result.strategy,
                "chunks_retrieved": len(planner_result.chunks),
                "had_context": planner_result.has_context,
                "elapsed_seconds": elapsed,
                **kwargs,
            },
        )

        logger.info(
            "Orchestrator: pipeline complete in %.3fs — %d source(s).",
            elapsed, len(sources),
        )

        return result
