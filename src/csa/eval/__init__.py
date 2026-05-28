"""
Scale-agnostic evaluation harness.

Importable as ``csa.eval``. Requires the ``[eval]`` extra
(``pip install "clinical-skill-architecture[eval]"``) for SciPy-backed exact
binomial CIs; the module falls back to Wilson intervals if SciPy is unavailable.
"""

from csa.eval.evaluator import (
    MetricsReport,
    PerSubscale,
    compare_runs,
    evaluate_instance,
    evaluate_run,
)
from csa.eval.matcher import match_codings
from csa.eval.metrics import (
    binomial_ci,
    clause_similarity,
    cohens_kappa,
    weighted_kappa,
)

__all__ = [
    "MetricsReport",
    "PerSubscale",
    "evaluate_run",
    "evaluate_instance",
    "compare_runs",
    "match_codings",
    "binomial_ci",
    "cohens_kappa",
    "weighted_kappa",
    "clause_similarity",
]
