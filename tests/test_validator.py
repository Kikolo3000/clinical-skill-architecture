"""Unit tests for the output validator."""

from __future__ import annotations

import pytest

from csa.validator import ValidationError, validate_record


def _good_record() -> dict:
    return {
        "id": "x",
        "screening": {
            "decision": "needs_analysis",
            "flagged_subscales": ["HOP"],
            "screening_rationale": "ok",
        },
        "codings": [
            {"clause": "x", "subscale": "HOP", "sub_item": "HOP.3b",
             "perspective": "self", "weight": 1, "rationale": "y"},
        ],
        "subscale_summaries": {
            sub: {"count": 0, "weighted_sum": 0, "items_found": []}
            for sub in ("HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS")
        },
        "word_count": 10,
    }


def test_good_record_validates():
    assert validate_record(_good_record()) == []


def test_invalid_decision_raises_in_strict_mode():
    rec = _good_record()
    rec["screening"]["decision"] = "ambiguous"
    with pytest.raises(ValidationError):
        validate_record(rec, strict=True)


def test_invalid_perspective_collected_in_lax_mode():
    rec = _good_record()
    rec["codings"][0]["perspective"] = "robot"
    errors = validate_record(rec, strict=False)
    assert any("perspective" in e for e in errors)


def test_missing_subscale_summary_caught():
    rec = _good_record()
    del rec["subscale_summaries"]["HOP"]
    errors = validate_record(rec, strict=False)
    assert any("HOP" in e for e in errors)


def test_flat_weight_subscale_must_be_one():
    rec = _good_record()
    rec["codings"][0]["weight"] = 3   # invalid for HOP
    errors = validate_record(rec, strict=False)
    assert any("weight" in e for e in errors)


def test_perspective_weight_consistency():
    rec = _good_record()
    # Switch to a perspective-sensitive subscale
    rec["codings"][0]["subscale"] = "HOS"
    rec["codings"][0]["perspective"] = "self"
    rec["codings"][0]["weight"] = 1   # should be 3 for self
    errors = validate_record(rec, strict=False)
    assert any("weight" in e for e in errors)
