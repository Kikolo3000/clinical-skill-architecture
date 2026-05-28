"""
Public dataclasses returned and consumed by the public API.

All result objects are frozen so callers cannot accidentally mutate scoring output.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Literal

Subscale = Literal["HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS"]
Perspective = Literal["self", "others", "inanimate", "denial"]
Decision = Literal["no_depressive_content", "needs_analysis"]

SUBSCALES: tuple[Subscale, ...] = ("HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS")
SUBSCALE_NAMES: dict[Subscale, str] = {
    "HOP": "Hopelessness",
    "SAC": "Self-accusation",
    "PMR": "Psychomotor retardation",
    "SOM": "Somatic concerns",
    "DAM": "Death and mutilation",
    "SEP": "Separation depression",
    "HOS": "Hostility outward",
}


@dataclass(frozen=True, slots=True)
class Fragment:
    """A single speaker utterance to evaluate, with surrounding context."""

    id: str
    line_number: int
    speaker: str
    study_excerpt: str
    close_context: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Coding:
    """One clause-level coding decision."""

    clause: str
    subscale: Subscale
    sub_item: str
    perspective: Perspective
    weight: int
    rationale: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Screening:
    decision: Decision
    flagged_subscales: tuple[Subscale, ...]
    rationale: str

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "flagged_subscales": list(self.flagged_subscales),
            "screening_rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class FragmentResult:
    """Per-utterance scoring result. The smallest reportable unit."""

    fragment: Fragment
    screening: Screening
    codings: tuple[Coding, ...]
    word_count: int
    analyzed_at: str
    prompt_version: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0

    def codings_for(self, subscale: Subscale) -> tuple[Coding, ...]:
        return tuple(c for c in self.codings if c.subscale == subscale)

    def weighted_sum(self, subscale: Subscale) -> int:
        return sum(c.weight for c in self.codings if c.subscale == subscale)

    def to_dict(self) -> dict:
        summaries = {
            sub: {
                "count": sum(1 for c in self.codings if c.subscale == sub),
                "weighted_sum": self.weighted_sum(sub),
                "items_found": sorted({c.sub_item for c in self.codings if c.subscale == sub}),
            }
            for sub in SUBSCALES
        }
        return {
            "id": self.fragment.id,
            "screening": self.screening.to_dict(),
            "codings": [c.to_dict() for c in self.codings],
            "subscale_summaries": summaries,
            "word_count": self.word_count,
            "analyzed_at": self.analyzed_at,
            "prompt_version": self.prompt_version,
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
                "cached": self.cached_tokens,
            },
        }


@dataclass(frozen=True, slots=True)
class SubscaleScore:
    """Aggregated G-G score for one subscale across one or more fragments."""

    subscale: Subscale
    score: float
    count: int
    weighted_sum: int
    word_count: int
    items_found: tuple[str, ...] = field(default_factory=tuple)

    @property
    def name(self) -> str:
        return SUBSCALE_NAMES[self.subscale]

    def to_dict(self) -> dict:
        return {
            "subscale": self.subscale,
            "name": self.name,
            "score": self.score,
            "count": self.count,
            "weighted_sum": self.weighted_sum,
            "word_count": self.word_count,
            "items_found": list(self.items_found),
        }


@dataclass(frozen=True, slots=True)
class ScoringResult:
    """
    Top-level result returned by ``score()`` and ``ScaleAgent.score()``.

    Aggregates per-fragment results into the 7 G-G subscale scores plus the total
    depression score, applying the canonical formula
    `sqrt((weighted_sum + 0.5) * 100 / word_count)` per subscale.
    """

    fragments: tuple[FragmentResult, ...]
    subscales: dict[Subscale, SubscaleScore]
    total_depression: float
    word_count: int
    model: str
    prompt_version: str
    estimated_cost_usd: float = 0.0

    @property
    def codings(self) -> tuple[Coding, ...]:
        return tuple(c for fr in self.fragments for c in fr.codings)

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "prompt_version": self.prompt_version,
            "word_count": self.word_count,
            "total_depression": self.total_depression,
            "subscales": {sub: score.to_dict() for sub, score in self.subscales.items()},
            "fragments": [fr.to_dict() for fr in self.fragments],
            "estimated_cost_usd": self.estimated_cost_usd,
        }


def gg_formula(weighted_sum: int, word_count: int) -> float:
    """
    Canonical Gottschalk-Gleser score for one subscale.

        score = sqrt((weighted_sum + 0.5) * 100 / word_count)

    Returns 0.0 if word_count <= 0.
    """
    if word_count <= 0:
        return 0.0
    return math.sqrt((weighted_sum + 0.5) * 100.0 / word_count)
