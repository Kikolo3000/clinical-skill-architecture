"""End-to-end smoke test of the agent with a stubbed backend (no network)."""

from __future__ import annotations

import asyncio
import json

from csa import GGAgent
from csa.backends.base import BackendResponse


class StubBackend:
    """A scripted backend: returns canned JSON strings depending on the system prompt."""

    name = "stub"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def complete(self, *, system: str, user: str, model: str, cache_system: bool = True):
        self.calls.append((system[:80], user[:80]))
        if "STAGE 1: SCREENING" in system:
            payload = {
                "decision": "needs_analysis",
                "flagged_subscales": ["HOP"],
                "screening_rationale": "Hopelessness phrasing detected.",
                "word_count": len(user.split()),
            }
            return BackendResponse(text=json.dumps(payload), input_tokens=200,
                                   output_tokens=40, cached_tokens=180)
        if "STAGE 2" in system:
            payload = {
                "scratchpad": {"sp1": "y"},
                "exclusion_checklist": {"ec1": "n"},
                "codings": [{
                    "clause": "i just don't see the point anymore",
                    "subscale": "HOP",
                    "sub_item": "HOP.3b",
                    "perspective": "self",
                    "weight": 1,
                    "rationale": "Direct hopelessness.",
                }],
            }
            return BackendResponse(text=json.dumps(payload), input_tokens=400,
                                   output_tokens=120, cached_tokens=380)
        return BackendResponse(text="{}", input_tokens=0, output_tokens=0, cached_tokens=0)


def test_agent_end_to_end_with_stub_backend():
    agent = GGAgent(backend=StubBackend(), model="stub-model", max_concurrent=2)
    transcript = (
        "I: how have you been feeling about the future\n"
        "S: i just don't see the point anymore"
    )
    result = asyncio.run(agent.score_async(transcript))

    # One fragment, one HOP coding, weighted sum = 1
    assert len(result.fragments) == 1
    assert len(result.codings) == 1
    assert result.codings[0].subscale == "HOP"
    assert result.subscales["HOP"].weighted_sum == 1
    assert result.total_depression > 0
    assert result.estimated_cost_usd >= 0
    assert result.prompt_version


def test_sync_score_wraps_async():
    """The `GGAgent.score()` sync wrapper runs end-to-end without a live API."""
    agent = GGAgent(backend=StubBackend(), model="stub-model", max_concurrent=2)
    result = agent.score("I: q\nS: i just don't see the point anymore")
    assert result.total_depression >= 0
