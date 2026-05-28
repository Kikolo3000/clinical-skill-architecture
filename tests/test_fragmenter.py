"""Unit tests for the transcript fragmenter."""

from __future__ import annotations

import pytest

from csa.fragmenter import fragment


def test_basic_two_speaker_dialogue():
    text = "I: how are you\nS: not great today"
    frags = fragment(text)
    assert len(frags) == 1
    assert frags[0].speaker == "S"
    assert frags[0].study_excerpt == "not great today"
    assert "how are you" in frags[0].close_context


def test_auto_detects_p1_p2_format():
    text = "P1: hello\nP2: hi back\nP1: how are you\nP2: ok"
    frags = fragment(text)
    # Default: skip first speaker (P1), score the rest
    speakers = {f.speaker for f in frags}
    assert speakers == {"P2"}
    assert len(frags) == 2


def test_target_speakers_all():
    text = "I: q1\nS: a1\nI: q2\nS: a2"
    frags = fragment(text, target_speakers="all")
    assert len(frags) == 4


def test_multi_line_continuation_merges():
    text = "I: how are you\nS: fine\nthank you"
    frags = fragment(text)
    assert frags[0].study_excerpt == "fine thank you"


def test_context_turns_limit():
    text = "\n".join(f"I: q{i}\nS: a{i}" for i in range(10))
    frags = fragment(text, context_turns=2)
    last = frags[-1]
    # Context should contain at most 2 preceding turns
    assert last.close_context.count("\n") <= 1


def test_raises_on_no_speakers():
    with pytest.raises(ValueError, match="No speaker labels"):
        fragment("just some plain text with no labels")


def test_skip_metadata_lines():
    text = "Transcribed by: John\n@some-tag\n# title\nI: hi\nS: hi back"
    frags = fragment(text)
    assert len(frags) == 1
    assert frags[0].study_excerpt == "hi back"


def test_id_prefix_uses_argument():
    frags = fragment("I: q\nS: a", id_prefix="session_42")
    assert frags[0].id.startswith("session_42_")
