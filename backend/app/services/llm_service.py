"""
KRISHNA — LLM service.

Production-grade wrapper around the OpenRouter API.

Responsibilities:
  • Build chat-completion requests against OpenRouter's v1 endpoint.
  • Handle retries (with exponential back-off) for transient failures.
  • Surface clear errors for bad keys, rate limits, or malformed responses.
  • Keep the interface simple:  generate_response(prompt) → str

Usage:
    from app.services.llm_service import LLMService

    llm = LLMService()
    answer = await llm.generate_response("Explain photosynthesis.")
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import requests

from app.config import settings

logger = logging.getLogger(__name__)

# ── OpenRouter constants ───────────────────────────────────────────────
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_MAX_RETRIES = 3
_RETRY_BACKOFF_BASE = 1.5          # seconds (1.5, 2.25, 3.375 …)
_DEFAULT_MAX_TOKENS = 1024
_DEFAULT_TEMPERATURE = 0.7


class LLMServiceError(Exception):
    """Raised when the LLM service encounters an unrecoverable error."""


class LLMService:
    """
    Wrapper around OpenRouter's chat-completion API.

    Configuration is pulled from ``settings.OPENROUTER_API_KEY`` and
    ``settings.OPENROUTER_MODEL`` (set via ``.env``).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        temperature: float = _DEFAULT_TEMPERATURE,
    ) -> None:
        self._api_key = api_key or settings.OPENROUTER_API_KEY
        self._model = model or settings.OPENROUTER_MODEL
        self._max_tokens = max_tokens
        self._temperature = temperature

        if not self._api_key:
            logger.warning(
                "OPENROUTER_API_KEY is empty — LLM calls will fail. "
                "Set it in .env or pass it to LLMService()."
            )

    # ── public API ──────────────────────────────────────────────────────

    async def generate_response(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """
        Send a prompt to OpenRouter and return the generated text.

        Parameters
        ----------
        prompt : str
            The user message / question.
        system_prompt : str | None
            Optional system instruction prepended to the conversation.
        max_tokens : int | None
            Override the default max output tokens for this call.
        temperature : float | None
            Override the default temperature for this call.

        Returns
        -------
        str
            The model's generated text content.

        Raises
        ------
        LLMServiceError
            If the API key is missing, the request fails after retries,
            or the response cannot be parsed.
        """
        if not self._api_key:
            raise LLMServiceError(
                "OPENROUTER_API_KEY is not configured. "
                "Set it in your .env file."
            )

        messages = self._build_messages(prompt, system_prompt)
        payload = self._build_payload(messages, max_tokens, temperature)

        # Run the blocking `requests.post` in a thread so we don't
        # block the async event loop.
        response_data = await asyncio.to_thread(
            self._post_with_retries, payload
        )

        return self._extract_text(response_data)

    # ── internals ───────────────────────────────────────────────────────

    @staticmethod
    def _build_messages(
        prompt: str,
        system_prompt: str | None,
    ) -> list[dict[str, str]]:
        """Assemble the messages array for the chat-completion request."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _build_payload(
        self,
        messages: list[dict[str, str]],
        max_tokens: int | None,
        temperature: float | None,
    ) -> dict[str, Any]:
        """Build the JSON body sent to OpenRouter."""
        return {
            "model": self._model,
            "messages": messages,
            "max_tokens": max_tokens or self._max_tokens,
            "temperature": temperature if temperature is not None else self._temperature,
        }

    def _post_with_retries(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Synchronous POST with exponential back-off.

        Retries on 429 (rate-limit) and 5xx (server errors).
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://krishna.app",
            "X-Title": "KRISHNA",
        }

        last_exc: Exception | None = None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    _OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=60,
                )

                # ── success ─────────────────────────────────────────────
                if resp.status_code == 200:
                    return resp.json()

                # ── retryable ───────────────────────────────────────────
                if resp.status_code in (429, 500, 502, 503, 504):
                    wait = _RETRY_BACKOFF_BASE ** attempt
                    logger.warning(
                        "OpenRouter %d on attempt %d/%d — retrying in %.1fs",
                        resp.status_code, attempt, _MAX_RETRIES, wait,
                    )
                    import time
                    time.sleep(wait)
                    last_exc = LLMServiceError(
                        f"OpenRouter returned {resp.status_code}: {resp.text[:300]}"
                    )
                    continue

                # ── non-retryable ───────────────────────────────────────
                raise LLMServiceError(
                    f"OpenRouter error {resp.status_code}: {resp.text[:500]}"
                )

            except requests.RequestException as exc:
                wait = _RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "Network error on attempt %d/%d — %s — retrying in %.1fs",
                    attempt, _MAX_RETRIES, exc, wait,
                )
                import time
                time.sleep(wait)
                last_exc = exc

        raise LLMServiceError(
            f"All {_MAX_RETRIES} attempts to OpenRouter failed."
        ) from last_exc

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        """Pull the assistant's message text from the API response."""
        try:
            choices = data["choices"]
            text = choices[0]["message"]["content"]
            if not text:
                raise ValueError("Empty content in response")
            return text.strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.error("Failed to parse OpenRouter response: %s", data)
            raise LLMServiceError(
                f"Could not extract text from OpenRouter response: {exc}"
            ) from exc
