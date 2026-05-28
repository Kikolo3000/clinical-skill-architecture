"""
Greedy bipartite matching of predicted codings to ground-truth codings via
clause similarity. Anything ground-truth that is unmatched becomes a false
negative; anything predicted that is unmatched becomes a false positive.
"""

from __future__ import annotations

from typing import Literal, TypedDict

from csa.eval.metrics import clause_similarity

MatchType = Literal["tp", "fn", "fp"]


class Match(TypedDict, total=False):
    gt_idx: int | None
    pred_idx: int | None
    gt_coding: dict | None
    pred_coding: dict | None
    similarity: float
    match_type: MatchType


def match_codings(
    gt_codings: list[dict],
    pred_codings: list[dict],
    *,
    threshold: float = 0.5,
) -> list[Match]:
    """
    Returns a list of `Match` records covering every ground-truth and predicted
    coding exactly once.

    `match_type` is one of:
    - `"tp"` — clause similarity ≥ threshold; pair is matched
    - `"fn"` — ground-truth clause not matched to any prediction
    - `"fp"` — predicted clause not matched to any ground truth
    """
    if not gt_codings and not pred_codings:
        return []

    similarities: dict[tuple[int, int], float] = {}
    for i, gt in enumerate(gt_codings):
        for j, pred in enumerate(pred_codings):
            sim = clause_similarity(gt.get("clause", ""), pred.get("clause", ""))
            if sim >= threshold:
                similarities[(i, j)] = sim

    matched_gt: set[int] = set()
    matched_pred: set[int] = set()
    matches: list[Match] = []

    for (i, j), sim in sorted(similarities.items(), key=lambda x: -x[1]):
        if i in matched_gt or j in matched_pred:
            continue
        matched_gt.add(i)
        matched_pred.add(j)
        matches.append({
            "gt_idx": i,
            "pred_idx": j,
            "gt_coding": gt_codings[i],
            "pred_coding": pred_codings[j],
            "similarity": sim,
            "match_type": "tp",
        })

    for i, gt in enumerate(gt_codings):
        if i not in matched_gt:
            matches.append({
                "gt_idx": i,
                "pred_idx": None,
                "gt_coding": gt,
                "pred_coding": None,
                "similarity": 0.0,
                "match_type": "fn",
            })

    for j, pred in enumerate(pred_codings):
        if j not in matched_pred:
            matches.append({
                "gt_idx": None,
                "pred_idx": j,
                "gt_coding": None,
                "pred_coding": pred,
                "similarity": 0.0,
                "match_type": "fp",
            })

    return matches
