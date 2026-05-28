"""
Statistical helpers used by the evaluator.

`binomial_ci` returns an exact Clopper-Pearson interval when SciPy is
available; otherwise it falls back to a Wilson score interval — close enough
for almost any practical n. Both are 95% by default.
"""

from __future__ import annotations

import math
import re
from collections import Counter


def _normalise(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def clause_similarity(a: str, b: str) -> float:
    """Token-Jaccard similarity between two clauses (lowercased, punctuation stripped)."""
    ta = set(_normalise(a).split())
    tb = set(_normalise(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z = 1.96  # two-sided 95%
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def binomial_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """
    Clopper-Pearson exact 95% CI when SciPy is installed; Wilson otherwise.
    """
    if n == 0:
        return (0.0, 1.0)
    try:
        from scipy.stats import beta as beta_dist
    except ImportError:
        return _wilson_ci(k, n, alpha)

    lo = float(beta_dist.ppf(alpha / 2, k, n - k + 1)) if k > 0 else 0.0
    hi = float(beta_dist.ppf(1 - alpha / 2, k + 1, n - k)) if k < n else 1.0
    return (lo, hi)


def cohens_kappa(tp: int, fp: int, fn: int, tn: int) -> float:
    """Binary Cohen's kappa from a 2x2 confusion."""
    n = tp + fp + fn + tn
    if n == 0:
        return 0.0
    po = (tp + tn) / n
    pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / (n * n)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def weighted_kappa(confusion: dict[tuple[int, int], int], weights: list[int]) -> float:
    """Linear-weighted kappa for ordinal weight agreement."""
    categories = sorted(set(weights))
    if len(categories) < 2:
        return 1.0
    n = sum(confusion.values())
    if n == 0:
        return 0.0
    max_diff = max(categories) - min(categories)
    if max_diff == 0:
        return 1.0

    row_totals: Counter = Counter()
    col_totals: Counter = Counter()
    for (gt_w, pred_w), count in confusion.items():
        row_totals[gt_w] += count
        col_totals[pred_w] += count

    po_w = 0.0
    pe_w = 0.0
    for (gt_w, pred_w), count in confusion.items():
        w_ij = 1 - abs(gt_w - pred_w) / max_diff
        po_w += w_ij * count / n
        pe_w += w_ij * row_totals[gt_w] * col_totals[pred_w] / (n * n)

    if pe_w == 1.0:
        return 1.0
    return (po_w - pe_w) / (1 - pe_w)
