"""Unit tests for evaluation metrics and clause matching."""

from __future__ import annotations

import math

from csa.eval.matcher import match_codings
from csa.eval.metrics import (
    binomial_ci,
    clause_similarity,
    cohens_kappa,
    weighted_kappa,
)


def test_clause_similarity_identical_is_one():
    assert clause_similarity("I feel hopeless", "I feel hopeless") == 1.0


def test_clause_similarity_disjoint_is_zero():
    assert clause_similarity("happy birthday", "fast cars") == 0.0


def test_clause_similarity_punctuation_insensitive():
    assert clause_similarity("Hi, friend.", "hi friend") == 1.0


def test_binomial_ci_zero_n_full_range():
    lo, hi = binomial_ci(0, 0)
    assert (lo, hi) == (0.0, 1.0)


def test_binomial_ci_full_success_upper_one():
    _lo, hi = binomial_ci(10, 10)
    assert math.isclose(hi, 1.0)


def test_binomial_ci_contains_observed_proportion():
    lo, hi = binomial_ci(20, 100)
    assert lo <= 0.20 <= hi


def test_cohens_kappa_perfect_agreement_is_one():
    assert cohens_kappa(tp=10, fp=0, fn=0, tn=10) == 1.0


def test_cohens_kappa_chance_agreement_near_zero():
    k = cohens_kappa(tp=5, fp=5, fn=5, tn=5)
    assert -0.1 < k < 0.1


def test_weighted_kappa_perfect_agreement_is_one():
    confusion = {(1, 1): 5, (2, 2): 5, (3, 3): 5}
    assert weighted_kappa(confusion, [1, 2, 3, 1, 2, 3]) == 1.0


def test_match_codings_perfect_pair_is_tp():
    gt = [{"clause": "I feel hopeless", "subscale": "HOP"}]
    pred = [{"clause": "I feel hopeless", "subscale": "HOP"}]
    matches = match_codings(gt, pred)
    assert len(matches) == 1
    assert matches[0]["match_type"] == "tp"


def test_match_codings_unmatched_pred_is_fp():
    gt: list = []
    pred = [{"clause": "I feel happy", "subscale": "HOP"}]
    matches = match_codings(gt, pred)
    assert len(matches) == 1
    assert matches[0]["match_type"] == "fp"


def test_match_codings_unmatched_gt_is_fn():
    gt = [{"clause": "I feel hopeless", "subscale": "HOP"}]
    pred: list = []
    matches = match_codings(gt, pred)
    assert len(matches) == 1
    assert matches[0]["match_type"] == "fn"
