"""
Transcript fragmentation: split a multi-turn transcript into per-utterance Fragments
ready for scoring.

Supports any "LABEL: text" format — `I:`/`S:` (clinical interview), `P1:`/`P2:`
(phone), `Speaker 1:` (ASR), or any custom prefix. The first speaker label seen
is treated as the interviewer by default, so only subsequent speakers are
extracted unless you pass `target_speakers="all"`.
"""

from __future__ import annotations

import re
from pathlib import Path

from csa.schemas import Fragment

_LABEL_PATTERN = re.compile(r"^((?:Speaker\s+)?\w+):\s")
_SKIP_PATTERNS = (
    re.compile(r"^Transcribed by:"),
    re.compile(r"^@"),
    re.compile(r"^#"),
)


def _detect_speaker_labels(lines: list[str], scan_limit: int = 50) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()
    for i, line in enumerate(lines):
        if i > scan_limit and len(labels) >= 2:
            break
        m = _LABEL_PATTERN.match(line)
        if m:
            label = m.group(1)
            if label not in seen:
                labels.append(label)
                seen.add(label)
    return labels


def _parse_turns(lines: list[str], labels: list[str]) -> list[dict]:
    """Parse continuous turns; merge multi-line continuations into one turn."""
    pattern = re.compile(r"^(" + "|".join(re.escape(label) for label in labels) + r"):\s*(.*)")
    turns: list[dict] = []
    current_speaker: str | None = None
    current_text: list[str] = []
    current_line_start: int | None = None

    for line_num, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if any(p.match(line) for p in _SKIP_PATTERNS):
            continue
        m = pattern.match(line)
        if m:
            if current_speaker is not None and current_text:
                turns.append({
                    "line_number": current_line_start,
                    "speaker": current_speaker,
                    "text": " ".join(current_text).strip(),
                })
            current_speaker = m.group(1)
            current_line_start = line_num
            tail = m.group(2).strip()
            current_text = [tail] if tail else []
        elif current_speaker is not None and line.strip():
            current_text.append(line.strip())

    if current_speaker is not None and current_text:
        turns.append({
            "line_number": current_line_start,
            "speaker": current_speaker,
            "text": " ".join(current_text).strip(),
        })
    return turns


def fragment(
    transcript: str,
    *,
    target_speakers: str | list[str] | None = None,
    context_turns: int = 5,
    id_prefix: str = "frag",
) -> list[Fragment]:
    """
    Split a transcript string into a list of `Fragment`s ready to score.

    Args:
        transcript: The transcript text. Lines must follow a "LABEL: text" format
            (e.g., `I: how are you`, `S: not great`).
        target_speakers: Which speakers to score. Default: every speaker except
            the first one detected (the interviewer convention). Pass `"all"` to
            score every speaker, or a list of explicit labels (`["S", "P1"]`).
        context_turns: Number of preceding turns to bundle as `close_context`.
        id_prefix: String prefix used in the generated fragment IDs.

    Returns:
        A list of immutable `Fragment` instances.

    Raises:
        ValueError: if no speaker labels are detected.
    """
    lines = transcript.splitlines(keepends=False)
    labels = _detect_speaker_labels(lines)
    if not labels:
        raise ValueError(
            "No speaker labels detected. Transcript lines must start with "
            "'LABEL: text' (e.g., 'S: I feel hopeless')."
        )

    turns = _parse_turns(lines, labels)

    if target_speakers is None:
        targets: set[str] = set(labels[1:]) if len(labels) > 1 else set(labels)
    elif isinstance(target_speakers, str) and target_speakers.lower() in ("all", "both"):
        targets = set(labels)
    elif isinstance(target_speakers, str):
        targets = {target_speakers}
    else:
        targets = set(target_speakers)

    fragments: list[Fragment] = []
    counter = 1
    for i, turn in enumerate(turns):
        if turn["speaker"] not in targets:
            continue
        ctx_start = max(0, i - context_turns)
        ctx_lines = [
            f"{turns[j]['speaker']}: {turns[j]['text']}" for j in range(ctx_start, i)
        ]
        speaker_tag = f"{turn['speaker']}_" if len(targets) > 1 else ""
        fragments.append(
            Fragment(
                id=f"{id_prefix}_{speaker_tag}{counter:04d}",
                line_number=turn["line_number"],
                speaker=turn["speaker"],
                study_excerpt=turn["text"],
                close_context="\n".join(ctx_lines),
            )
        )
        counter += 1
    return fragments


def fragment_file(path: str | Path, **kwargs) -> list[Fragment]:
    """Convenience wrapper: read a transcript file from disk and fragment it."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    kwargs.setdefault("id_prefix", p.parent.name or p.stem)
    return fragment(text, **kwargs)
