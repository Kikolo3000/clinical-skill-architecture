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


def test_evaluate_run_instance_ids_filters_instances(tmp_path):
    """v0.2.0: `instance_ids` restricts evaluation to the named instance directories (suite v1.1)."""
    import json
    from csa.eval import evaluate_run

    def make(inst, clause):
        d = tmp_path / "gt" / inst
        d.mkdir(parents=True)
        rec = {"id": f"{inst}_0001", "screening": {"decision": "needs_analysis", "flagged_subscales": ["HOP"]},
               "codings": [{"clause": clause, "subscale": "HOP", "sub_item": "HOP.3b",
                            "perspective": "self", "weight": 1, "rationale": "x"}]}
        (d / "ground_truth.jsonl").write_text(json.dumps(rec) + "\n")
        p = tmp_path / "pred" / inst
        p.mkdir(parents=True)
        (p / "output.jsonl").write_text(json.dumps(rec) + "\n")

    make("SYN_A", "nothing is worth doing any more")
    make("SYN_B", "i cannot see a way forward")
    full = evaluate_run(tmp_path / "gt", tmp_path / "pred")
    sub = evaluate_run(tmp_path / "gt", tmp_path / "pred", instance_ids={"SYN_A"})
    assert full.detection_f1 == 1.0 and sub.detection_f1 == 1.0
    assert full.n_gt_codings == 2 and sub.n_gt_codings == 1
