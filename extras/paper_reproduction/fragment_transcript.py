#!/usr/bin/env python3
"""
Fragment a transcript into individual speaker utterances with context.

Supports flexible speaker label formats:
    - I:/S: (clinical interview format)
    - P1:/P2: (phone conversation format)
    - Speaker 1:/Speaker 2: (ASR output format)
    - Any "LABEL:" prefix format (auto-detected)

Usage:
    python scripts/fragment_transcript.py data/transcript.md
    python scripts/fragment_transcript.py data/transcript.md --speaker S
    python scripts/fragment_transcript.py data/transcript.md --speaker P1
    python scripts/fragment_transcript.py data/transcript.md --speaker both
    python scripts/fragment_transcript.py data/transcript.md --output results/call_001/input.jsonl
"""

import argparse
import json
import re
import sys
from pathlib import Path


def detect_speaker_format(lines: list[str]) -> list[str]:
    """Auto-detect speaker labels from the first lines of the transcript.

    Returns a list of unique speaker labels found (e.g., ['I', 'S'] or ['P1', 'P2']).
    """
    # Pattern: start of line, one or more word chars (possibly with spaces for "Speaker 1"),
    # followed by a colon
    label_pattern = re.compile(r"^((?:Speaker\s+)?\w+):\s")
    labels = []
    seen = set()

    for line in lines:
        m = label_pattern.match(line)
        if m:
            label = m.group(1)
            if label not in seen:
                labels.append(label)
                seen.add(label)
        # Stop after finding at least 2 distinct labels or scanning 50 lines
        if len(labels) >= 2 or len(seen) > 0 and lines.index(line) > 50:
            break

    return labels


def parse_interventions(lines: list[str], labels: list[str]) -> list[dict]:
    """Parse all speaker interventions from transcript lines.

    Returns list of dicts: {line_number, speaker, text}.
    """
    # Build pattern to match any known label
    escaped_labels = [re.escape(label) for label in labels]
    pattern = re.compile(r"^(" + "|".join(escaped_labels) + r"):\s*(.*)")

    interventions = []
    current_speaker = None
    current_text = []
    current_line_start = None

    # Lines to skip (headers, metadata)
    skip_patterns = [
        re.compile(r"^Transcribed by:"),
        re.compile(r"^@"),
        re.compile(r"^#"),  # markdown headers
    ]

    for line_num, line in enumerate(lines, start=1):
        line = line.rstrip("\n")

        # Skip header/metadata lines
        if any(p.match(line) for p in skip_patterns):
            continue

        # Check for speaker change
        m = pattern.match(line)
        if m:
            # Save previous intervention
            if current_speaker is not None and current_text:
                interventions.append({
                    "line_number": current_line_start,
                    "speaker": current_speaker,
                    "text": " ".join(current_text).strip(),
                })

            current_speaker = m.group(1)
            current_line_start = line_num
            current_text = [m.group(2).strip()] if m.group(2).strip() else []

        elif current_speaker is not None and line.strip():
            # Continuation of current intervention (multi-line)
            current_text.append(line.strip())

    # Last intervention
    if current_speaker is not None and current_text:
        interventions.append({
            "line_number": current_line_start,
            "speaker": current_speaker,
            "text": " ".join(current_text).strip(),
        })

    return interventions


def fragment_transcript(
    transcript_path: str,
    speaker: str | None = None,
    output_path: str | None = None,
    context_turns: int = 5,
) -> list[dict]:
    """Fragment a transcript into individual utterances with context.

    Args:
        transcript_path: Path to the transcript file.
        speaker: Speaker label to evaluate (e.g., 'S', 'P1', 'both', or None for auto).
        output_path: Optional path to save the JSONL output.
        context_turns: Number of preceding turns to include as context.

    Returns:
        List of fragment dicts with id, line_number, close_context, study_excerpt.
    """
    transcript_path = Path(transcript_path)

    with open(transcript_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Use parent directory name for fragment IDs
    base_name = transcript_path.parent.name or transcript_path.stem

    # Detect speaker format
    labels = detect_speaker_format(lines)
    if not labels:
        print(f"Error: No speaker labels detected in {transcript_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Detected speakers: {', '.join(labels)}")

    # Parse all interventions
    interventions = parse_interventions(lines, labels)
    print(f"Total interventions parsed: {len(interventions)}")

    # Determine which speaker(s) to evaluate
    if speaker is None or speaker == "":
        # Default: evaluate all non-first speakers (assume first speaker is interviewer)
        target_speakers = set(labels[1:]) if len(labels) > 1 else set(labels)
    elif speaker.lower() == "both" or speaker.lower() == "all":
        target_speakers = set(labels)
    else:
        # Validate the specified speaker exists
        if speaker not in labels:
            print(f"Error: Speaker '{speaker}' not found. Available: {labels}", file=sys.stderr)
            sys.exit(1)
        target_speakers = {speaker}

    print(f"Evaluating speaker(s): {', '.join(sorted(target_speakers))}")

    # Extract target speaker utterances with context
    fragments = []
    counter = 1

    for i, intervention in enumerate(interventions):
        if intervention["speaker"] not in target_speakers:
            continue

        # Build context: up to N prior interventions
        context_parts = []
        context_start = max(0, i - context_turns)
        for j in range(context_start, i):
            ctx = interventions[j]
            context_parts.append(f"{ctx['speaker']}: {ctx['text']}")

        # Build speaker prefix for multi-speaker evaluation
        speaker_prefix = f"{intervention['speaker']}_" if len(target_speakers) > 1 else ""

        fragment = {
            "id": f"{base_name}_{speaker_prefix}{counter:04d}",
            "line_number": intervention["line_number"],
            "close_context": "\n".join(context_parts) if context_parts else "",
            "study_excerpt": intervention["text"],
        }

        fragments.append(fragment)
        counter += 1

    print(f"Extracted {len(fragments)} utterances for evaluation")

    # Save to file
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(fragments, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(fragments)} fragments to {output_path}")

    return fragments


def main():
    parser = argparse.ArgumentParser(
        description="Fragment a transcript into speaker utterances with context",
    )
    parser.add_argument(
        "transcript",
        help="Path to transcript file",
    )
    parser.add_argument(
        "--speaker",
        default=None,
        help="Speaker label to evaluate (e.g., 'S', 'P1', 'both'). "
             "Default: evaluate non-interviewer speakers.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for JSONL file. Default: results/<dirname>/input.jsonl",
    )
    parser.add_argument(
        "--context-turns",
        type=int,
        default=5,
        help="Number of preceding turns to include as context (default: 5)",
    )

    args = parser.parse_args()

    # Default output path
    transcript_path = Path(args.transcript)
    if args.output is None:
        project_root = Path(__file__).resolve().parent.parent
        dirname = transcript_path.parent.name or transcript_path.stem
        output_path = project_root / "results" / dirname / "input.jsonl"
    else:
        output_path = args.output

    fragments = fragment_transcript(
        args.transcript,
        speaker=args.speaker,
        output_path=output_path,
        context_turns=args.context_turns,
    )

    if fragments:
        print(f"\nFirst fragment preview:")
        print(json.dumps(fragments[0], indent=2))


if __name__ == "__main__":
    main()
