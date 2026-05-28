"""
Lightweight schema and consistency validator for raw model output records.

Used inside the agent (right after the LLM returns JSON) and exposed publicly
for users who want to re-validate output files.
"""

from __future__ import annotations

from typing import Any

from csa.schemas import SUBSCALES

VALID_PERSPECTIVES: frozenset[str] = frozenset({"self", "others", "inanimate", "denial"})
VALID_DECISIONS: frozenset[str] = frozenset({"no_depressive_content", "needs_analysis"})

# Subscales whose weight is always 1 regardless of perspective.
FLAT_WEIGHT_SUBSCALES: frozenset[str] = frozenset({"HOP", "PMR", "SOM"})

# Default weight by perspective for the 4 perspective-sensitive subscales.
PERSPECTIVE_WEIGHT: dict[str, int] = {
    "self": 3,
    "others": 2,
    "inanimate": 1,
    "denial": 1,
}


class ValidationError(ValueError):
    """Raised when a record violates the output schema."""


def validate_record(record: dict[str, Any], *, strict: bool = True) -> list[str]:
    """
    Validate a single output record. Returns a list of error strings (empty if valid).

    If `strict=True`, raises `ValidationError` on the first issue. Otherwise
    accumulates all issues and returns the list.
    """
    errors: list[str] = []

    def fail(msg: str) -> None:
        if strict:
            raise ValidationError(msg)
        errors.append(msg)

    if not isinstance(record, dict):
        fail("record is not a dict")
        return errors

    if "id" not in record:
        fail("missing 'id'")
    if "screening" not in record or not isinstance(record["screening"], dict):
        fail("missing or invalid 'screening' object")
    else:
        decision = record["screening"].get("decision")
        if decision not in VALID_DECISIONS:
            fail(f"invalid screening.decision: {decision!r}")
        flagged = record["screening"].get("flagged_subscales", [])
        if not isinstance(flagged, list):
            fail("screening.flagged_subscales must be a list")
        else:
            for sub in flagged:
                if sub not in SUBSCALES:
                    fail(f"unknown flagged subscale: {sub!r}")

    codings = record.get("codings", [])
    if not isinstance(codings, list):
        fail("'codings' must be a list")
        codings = []

    for i, coding in enumerate(codings):
        if not isinstance(coding, dict):
            fail(f"codings[{i}] not a dict")
            continue
        sub = coding.get("subscale")
        persp = coding.get("perspective")
        weight = coding.get("weight")
        if sub not in SUBSCALES:
            fail(f"codings[{i}].subscale invalid: {sub!r}")
        if persp not in VALID_PERSPECTIVES:
            fail(f"codings[{i}].perspective invalid: {persp!r}")
        if not isinstance(weight, int) or weight < 1 or weight > 4:
            fail(f"codings[{i}].weight must be int in [1,4], got {weight!r}")
        # Perspective/weight consistency check
        if isinstance(weight, int) and sub in SUBSCALES and persp in VALID_PERSPECTIVES:
            if sub in FLAT_WEIGHT_SUBSCALES and weight != 1:
                fail(f"codings[{i}] {sub} must have weight 1 (flat weight); got {weight}")
            elif sub not in FLAT_WEIGHT_SUBSCALES and sub != "SAC":
                expected = PERSPECTIVE_WEIGHT[persp]
                if weight != expected:
                    fail(
                        f"codings[{i}] {sub} perspective={persp} expected weight {expected}, "
                        f"got {weight}"
                    )

    summaries = record.get("subscale_summaries", {})
    if not isinstance(summaries, dict):
        fail("'subscale_summaries' must be a dict")
    else:
        for sub in SUBSCALES:
            if sub not in summaries:
                fail(f"subscale_summaries missing {sub!r}")

    if "word_count" not in record or not isinstance(record["word_count"], int):
        fail("'word_count' missing or not int")

    return errors
