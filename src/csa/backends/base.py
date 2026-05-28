"""Backend Protocol — every concrete backend must implement `complete(...)`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class BackendResponse:
    """Normalised response from any backend."""

    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0


class Backend(Protocol):
    """
    Minimal LLM-call surface. Backends decide internally how to enable JSON mode,
    prompt caching, retries, etc.
    """

    name: str

    async def complete(
        self,
        *,
        system: str,
        user: str,
        model: str,
        cache_system: bool = True,
    ) -> BackendResponse: ...
