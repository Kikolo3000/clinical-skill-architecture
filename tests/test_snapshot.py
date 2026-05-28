"""
Reproducibility canary.

Locks in the canonical scoring of the bundled SYN_001_easy_hopelessness demo
under a stub backend whose responses match the published ground truth. If the
scoring formula, aggregation, schema, or resource layout drifts in a future
refactor, this test catches it before reviewers notice the published numbers
no longer match.

Uses a stub backend so the test runs offline and stays deterministic.
"""

from __future__ import annotations

import asyncio
import json
import math
from importlib import resources

import pytest

from csa import GGAgent, PROMPT_VERSION
from csa.backends.base import BackendResponse
from csa.schemas import SUBSCALES


SNAPSHOT_TRANSCRIPT = (
    resources.files("csa")
    .joinpath("scales/gg_depression/data/demo/SYN_001_easy_hopelessness/transcript.md")
    .read_text()
)

# Mirrors src/csa/scales/gg_depression/data/demo/SYN_001_easy_hopelessness/ground_truth.jsonl
GROUND_TRUTH_HOP_CODINGS = [
    {
        "clause": "i just don't see the point anymore",
        "subscale": "HOP",
        "sub_item": "HOP.3b",
        "perspective": "self",
        "weight": 1,
        "rationale": "Direct expression of futility/hopelessness attributed to self",
    },
    {
        "clause": "nothing is going to change no matter what i do",
        "subscale": "HOP",
        "sub_item": "HOP.3b",
        "perspective": "self",
        "weight": 1,
        "rationale": "Pessimism about future despite effort - classic hopelessness",
    },
]

EXPECTED_WORD_COUNT = 26


class GroundTruthBackend:
    """Returns canned responses that mirror the SYN_001 ground truth."""

    name = "ground-truth-stub"

    async def complete(self, *, system: str, user: str, model: str, cache_system: bool = True):
        if "STAGE 1: SCREENING" in system:
            payload = {
                "decision": "needs_analysis",
                "flagged_subscales": ["HOP"],
                "screening_rationale": "Two clear HOP.3b clauses.",
                "word_count": EXPECTED_WORD_COUNT,
            }
        elif "STAGE 2" in system:
            payload = {
                "scratchpad": {"sp1": "stub"},
                "exclusion_checklist": {"ec1": "stub"},
                "codings": GROUND_TRUTH_HOP_CODINGS,
            }
        else:
            payload = {}
        return BackendResponse(
            text=json.dumps(payload), input_tokens=0, output_tokens=0, cached_tokens=0
        )


def _score_demo():
    agent = GGAgent(backend=GroundTruthBackend(), model="snapshot-stub", max_concurrent=1)
    return asyncio.run(agent.score_async(SNAPSHOT_TRANSCRIPT))


def test_snapshot_seven_subscales_always_present():
    """All 7 subscales must appear in the result, even when only HOP is scored."""
    result = _score_demo()
    assert set(result.subscales.keys()) == set(SUBSCALES)
    assert len(SUBSCALES) == 7


def test_snapshot_word_count_matches_published():
    """SYN_001 is published as a 26-word transcript; word counter must match."""
    result = _score_demo()
    assert result.word_count == EXPECTED_WORD_COUNT


def test_snapshot_hop_score_locked():
    """HOP score = sqrt((2 + 0.5) * 100 / 26). Locks the G-G formula and aggregation."""
    result = _score_demo()
    expected_hop = math.sqrt((2 + 0.5) * 100.0 / EXPECTED_WORD_COUNT)
    hop = result.subscales["HOP"]
    assert hop.weighted_sum == 2
    assert hop.count == 2
    assert hop.items_found == ("HOP.3b",)
    assert hop.score == pytest.approx(expected_hop, rel=1e-9)


def test_snapshot_silent_subscales_use_continuity_correction():
    """Subscales with no codings still produce sqrt(0.5 * 100 / 26), not zero."""
    result = _score_demo()
    expected_silent = math.sqrt(0.5 * 100.0 / EXPECTED_WORD_COUNT)
    for sub in SUBSCALES:
        if sub == "HOP":
            continue
        score = result.subscales[sub]
        assert score.weighted_sum == 0
        assert score.count == 0
        assert score.score == pytest.approx(expected_silent, rel=1e-9)


def test_snapshot_total_depression_locked():
    """Total = HOP score + 6 * silent score. Locks the aggregation."""
    result = _score_demo()
    expected_hop = math.sqrt(2.5 * 100.0 / EXPECTED_WORD_COUNT)
    expected_silent = math.sqrt(0.5 * 100.0 / EXPECTED_WORD_COUNT)
    expected_total = expected_hop + 6 * expected_silent
    assert result.total_depression == pytest.approx(expected_total, rel=1e-9)


def test_snapshot_prompt_version_recorded():
    """Every result records the PROMPT_VERSION so published numbers stay tied to prompts."""
    result = _score_demo()
    assert result.prompt_version == PROMPT_VERSION
    assert PROMPT_VERSION == "1.0.0"
