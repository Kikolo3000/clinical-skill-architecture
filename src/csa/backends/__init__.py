"""LLM backends. Pick one with ``get_backend(name)`` or pass to ``ScaleAgent(backend=...)``."""

from __future__ import annotations

from typing import Literal

from csa.backends.base import Backend, BackendResponse

BackendName = Literal["anthropic", "openai_compat"]


def get_backend(name: BackendName | str = "anthropic", **kwargs) -> Backend:
    """
    Construct a backend by name.

    - `"anthropic"` → uses `anthropic.AsyncAnthropic`. Requires `ANTHROPIC_API_KEY`
      env var (or pass `api_key=...`). Prompt caching is enabled by default for
      the system block.
    - `"openai_compat"` → uses `openai.AsyncOpenAI` against any OpenAI-compatible
      endpoint (Requesty.ai, OpenRouter, vLLM, ...). Pass `base_url=...` and
      `api_key=...`.
    """
    if name == "anthropic":
        from csa.backends.anthropic import AnthropicBackend
        return AnthropicBackend(**kwargs)
    if name == "openai_compat":
        from csa.backends.openai_compat import OpenAICompatBackend
        return OpenAICompatBackend(**kwargs)
    raise ValueError(f"Unknown backend: {name!r}. Choose 'anthropic' or 'openai_compat'.")


__all__ = ["Backend", "BackendResponse", "get_backend"]
