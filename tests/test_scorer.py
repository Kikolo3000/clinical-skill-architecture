"""Unit tests for the G-G formula and aggregation."""

from __future__ import annotations

import math

from csa.schemas import (
    Coding,
    Fragment,
    FragmentResult,
    Screening,
    gg_formula,
)
from csa.scorer import aggregate


def _make_fragment_result(codings: list[Coding], word_count: int) -> FragmentResult:
    return FragmentResult(
        fragment=Fragment(id="t1", line_number=1, speaker="S",
                          study_excerpt="x" * word_count, close_context=""),
        screening=Screening(decision="needs_analysis", flagged_subscales=("HOP",), rationale=""),
        codings=tuple(codings),
        word_count=word_count,
        analyzed_at="2026-04-23T00:00:00Z",
        prompt_version="1.0.0",
    )


def test_gg_formula_returns_canonical_value():
    # weighted_sum=2, word_count=26 → sqrt(2.5 * 100 / 26)
    assert gg_formula(2, 26) == math.sqrt(2.5 * 100 / 26)


def test_gg_formula_zero_word_count_returns_zero():
    assert gg_formula(5, 0) == 0.0


def test_gg_formula_with_zero_codings_uses_continuity_correction():
    # weighted_sum=0, word_count=100 → sqrt(0.5 * 100 / 100) = sqrt(0.5)
    assert gg_formula(0, 100) == math.sqrt(0.5)


def test_aggregate_seven_subscales_present():
    fr = _make_fragment_result([], word_count=10)
    scores, total, words = aggregate([fr])
    assert set(scores.keys()) == {"HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS"}
    assert words == 10


def test_aggregate_sums_across_fragments():
    fr1 = _make_fragment_result([
        Coding("I feel hopeless", "HOP", "HOP.3b", "self", 1, "x"),
    ], word_count=5)
    fr2 = _make_fragment_result([
        Coding("nothing matters", "HOP", "HOP.3b", "self", 1, "x"),
    ], word_count=5)
    scores, total, words = aggregate([fr1, fr2])
    assert words == 10
    assert scores["HOP"].weighted_sum == 2
    assert scores["HOP"].count == 2
    assert math.isclose(scores["HOP"].score, math.sqrt(2.5 * 100 / 10))


def test_total_depression_is_sum_of_subscale_scores():
    fr = _make_fragment_result([
        Coding("I feel hopeless", "HOP", "HOP.3b", "self", 1, "x"),
        Coding("I'm so guilty", "SAC", "SAC.A.a", "self", 3, "y"),
    ], word_count=10)
    scores, total, _ = aggregate([fr])
    assert math.isclose(total, sum(s.score for s in scores.values()))
