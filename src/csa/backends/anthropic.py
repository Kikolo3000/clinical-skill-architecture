"""
Anthropic SDK backend (default).

Uses `anthropic.AsyncAnthropic` with prompt caching on the system block. The
G-G pipeline reuses the same multi-kilobyte system prompt (skill + ontology)
across many fragment calls, so caching cuts cost and latency by 5–10x.
"""

from __future__ import annotations

import os

from csa.backends.base import Backend, BackendResponse


class AnthropicBackend:
    name = "anthropic"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ):
        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:
            raise ImportError(
                "The Anthropic backend requires the `anthropic` package. "
                "Install it with: pip install anthropic"
            ) from e

        self._client = AsyncAnthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self._max_tokens = max_tokens
        self._temperature = temperature

    async def complete(
        self,
        *,
        system: str,
        user: str,
        model: str,
        cache_system: bool = True,
    ) -> BackendResponse:
        if cache_system:
            system_blocks = [{
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }]
        else:
            system_blocks = [{"type": "text", "text": system}]

        response = await self._client.messages.create(
            model=model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            system=system_blocks,
            messages=[{"role": "user", "content": user}],
        )

        text_parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
        text = "".join(text_parts)

        usage = response.usage
        cached = (
            getattr(usage, "cache_read_input_tokens", 0) or 0
        ) + (
            getattr(usage, "cache_creation_input_tokens", 0) or 0
        )
        return BackendResponse(
            text=text,
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
            cached_tokens=cached,
        )


_: Backend = AnthropicBackend.__new__(AnthropicBackend)  # type: ignore[assignment]  # protocol check
