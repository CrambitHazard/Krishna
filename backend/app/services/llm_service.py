"""
KRISHNA — LLM service (placeholder).

Abstracts LLM provider calls (OpenAI, etc.) behind a unified interface.
"""

from __future__ import annotations

from app.config import settings


class LLMService:
    """Wrapper around the configured LLM provider."""

    def __init__(self) -> None:
        self.model = settings.LLM_MODEL

    async def generate(self, prompt: str) -> str:
        """Placeholder — returns a stub completion."""
        return f"[LLMService] stub response for model={self.model}"
