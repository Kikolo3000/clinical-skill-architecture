"""
OpenAI-compatible backend.

Works against any provider that speaks the OpenAI Chat Completions API:
Requesty.ai (router used in the npj DM paper for GLM-5), OpenRouter, vLLM,
Ollama with `--openai`, etc.
"""

from __future__ import annotations

import os

from csa.backends.base import Backend, BackendResponse


class OpenAICompatBackend:
    name = "openai_compat"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        json_mode: bool = True,
    ):
        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise ImportError(
                "The OpenAI-compatible backend requires the `openai` package. "
                "Install it with: pip install openai"
            ) from e

        self._client = AsyncOpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("REQUESTY_API_KEY"),
            base_url=base_url or os.environ.get("OPENAI_BASE_URL") or os.environ.get("REQUESTY_BASE_URL"),
        )
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._json_mode = json_mode

    async def complete(
        self,
        *,
        system: str,
        user: str,
        model: str,
        cache_system: bool = True,
    ) -> BackendResponse:
        # cache_system is ignored — provider-specific.
        kwargs: dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        if self._json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception as e:
            err = str(e)
            if self._json_mode and ("response_format" in err or "json_object" in err):
                kwargs.pop("response_format", None)
                response = await self._client.chat.completions.create(**kwargs)
            else:
                raise

        text = response.choices[0].message.content or ""
        usage = response.usage
        return BackendResponse(
            text=text,
            input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(usage, "completion_tokens", 0) or 0,
            cached_tokens=0,
        )


_: Backend = OpenAICompatBackend.__new__(OpenAICompatBackend)  # type: ignore[assignment]
