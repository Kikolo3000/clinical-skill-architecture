"""
clinical-skill-architecture (csa) — a framework for translating clinical
rating-scale ontologies into LLM-driven coding agents.

The framework is scale-agnostic; v0.1 ships with one fully-implemented scale,
the Gottschalk-Gleser depression scale, under :mod:`csa.scales.gg_depression`.
The convenience entrypoints below default to that scale.

Public API
----------

>>> from csa import score
>>> result = score("I just don't see the point anymore. Nothing's going to change.")
>>> print(result.total_depression)
>>> print(result.subscales["HOP"].score)

For framework-flavoured code:

>>> from csa import ScaleAgent
>>> agent = ScaleAgent(model="claude-sonnet-4-6", max_concurrent=10)
"""

from csa._version import PROMPT_VERSION, __version__
from csa.agent import GGAgent, ScaleAgent, score, score_async
from csa.schemas import (
    Coding,
    Fragment,
    FragmentResult,
    ScoringResult,
    SubscaleScore,
)

__all__ = [
    "__version__",
    "PROMPT_VERSION",
    "score",
    "score_async",
    "ScaleAgent",
    "GGAgent",
    "ScoringResult",
    "SubscaleScore",
    "Fragment",
    "FragmentResult",
    "Coding",
]
