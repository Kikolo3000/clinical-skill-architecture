#!/usr/bin/env python3
"""
Compute Gottschalk-Gleser Depression Scale scores from analysis output.

Formula per subscale:
    score = sqrt((weighted_sum + 0.5) * 100 / word_count)

Total depression = sum of all 7 subscale scores.

Usage:
    python scripts/compute_scores.py results/call_001/output_sonnet.jsonl
    python scripts/compute_scores.py results/call_001/  # finds output_*.jsonl automatically
"""

import csv
import json
import math
import sys
from pathlib import Path

SUBSCALES = ["HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS"]


def gg_score(weighted_sum: int | float, word_count: int) -> float:
    """Compute a single Gottschalk-Gleser subscale score.

    Formula: sqrt((weighted_sum + 0.5) * 100 / word_count)

    The +0.5 correction avoids discontinuity when no items are scored.
    Multiplying by 100 gives a rate per 100 words.
    Square root normalizes the skewed distribution.
    """
    if word_count <= 0:
        return 0.0
    return math.sqrt((weighted_sum + 0.5) * 100 / word_count)


def compute_utterance_scores(record: dict) -> dict:
    """Compute G-G scores for a single utterance record.

    Returns dict with per-subscale scores and total depression score.
    """
    word_count = record.get("word_count", 0)
    summaries = record.get("subscale_summaries", {})

    scores = {}
    for sub in SUBSCALES:
        summary = summaries.get(sub, {})
        weighted_sum = summary.get("weighted_sum", 0)
        scores[sub] = round(gg_score(weighted_sum, word_count), 4)

    scores["total_depression"] = round(sum(scores[s] for s in SUBSCALES), 4)
    scores["word_count"] = word_count

    return scores


def compute_transcript_scores(output_path: Path) -> dict:
    """Compute aggregate G-G scores for an entire transcript.

    Aggregates across all utterances by summing weighted frequencies
    and total word counts, then applying the formula once.
    """
    total_weights = {s: 0 for s in SUBSCALES}
    total_words = 0
    utterance_scores = []

    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            word_count = record.get("word_count", 0)
            summaries = record.get("subscale_summaries", {})

            total_words += word_count
            for sub in SUBSCALES:
                total_weights[sub] += summaries.get(sub, {}).get("weighted_sum", 0)

            # Also compute per-utterance scores
            scores = compute_utterance_scores(record)
            scores["id"] = record.get("id", "")
            scores["decision"] = record.get("screening", {}).get("decision", "")
            utterance_scores.append(scores)

    # Aggregate scores
    aggregate = {}
    for sub in SUBSCALES:
        aggregate[sub] = round(gg_score(total_weights[sub], total_words), 4)
    aggregate["total_depression"] = round(sum(aggregate[s] for s in SUBSCALES), 4)
    aggregate["total_words"] = total_words
    aggregate["n_utterances"] = len(utterance_scores)

    return {
        "aggregate": aggregate,
        "per_utterance": utterance_scores,
    }


def print_scores(result: dict):
    """Print formatted score report."""
    agg = result["aggregate"]
    per_utt = result["per_utterance"]

    print("\n" + "=" * 70)
    print("GOTTSCHALK-GLESER DEPRESSION SCALE SCORES")
    print("=" * 70)

    print(f"\n  Utterances analyzed: {agg['n_utterances']}")
    print(f"  Total words:         {agg['total_words']}")

    print(f"\n  AGGREGATE SCORES (across full transcript):")
    print(f"  {'Subscale':<12} {'Score':>8}")
    print(f"  {'-'*12} {'-'*8}")
    for sub in SUBSCALES:
        score = agg[sub]
        bar = "=" * int(score * 5) if score > 0 else ""
        print(f"  {sub:<12} {score:>8.4f}  {bar}")
    print(f"  {'-'*12} {'-'*8}")
    print(f"  {'TOTAL':<12} {agg['total_depression']:>8.4f}")

    # Per-utterance summary (only non-zero)
    active_utterances = [u for u in per_utt if u["total_depression"] > min(
        gg_score(0, u["word_count"]) * 7 + 0.01, 999
    )]

    if active_utterances:
        print(f"\n  UTTERANCES WITH DEPRESSIVE CONTENT:")
        print(f"  {'ID':<30} {'Total':>8} {'Subscales with content'}")
        print(f"  {'-'*30} {'-'*8} {'-'*30}")
        for u in active_utterances:
            active_subs = [s for s in SUBSCALES if u.get(s, 0) > gg_score(0, u["word_count"]) + 0.01]
            if active_subs:
                sub_str = ", ".join(f"{s}={u[s]:.2f}" for s in active_subs)
                print(f"  {u['id']:<30} {u['total_depression']:>8.4f} {sub_str}")

    print("\n" + "=" * 70)


def save_scores_csv(result: dict, output_path: Path):
    """Save per-utterance scores to CSV."""
    per_utt = result["per_utterance"]
    if not per_utt:
        return

    csv_path = output_path.parent / f"scores_{output_path.stem}.csv"

    fieldnames = ["id", "decision", "word_count"] + SUBSCALES + ["total_depression"]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in per_utt:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"Scores CSV saved: {csv_path}")

    # Also save aggregate as a single-row CSV
    agg_path = output_path.parent / f"aggregate_scores_{output_path.stem}.csv"
    agg = result["aggregate"]
    with open(agg_path, "w", newline="", encoding="utf-8") as f:
        fieldnames_agg = ["n_utterances", "total_words"] + SUBSCALES + ["total_depression"]
        writer = csv.DictWriter(f, fieldnames=fieldnames_agg)
        writer.writeheader()
        writer.writerow({k: agg.get(k, "") for k in fieldnames_agg})

    print(f"Aggregate CSV saved: {agg_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python compute_scores.py <output.jsonl or results_dir>")
        sys.exit(1)

    path = Path(sys.argv[1])

    # If directory, find output_*.jsonl
    if path.is_dir():
        jsonl_files = list(path.glob("output_*.jsonl"))
        if not jsonl_files:
            print(f"Error: No output_*.jsonl files found in {path}")
            sys.exit(1)
        # Use the most recently modified one
        output_path = max(jsonl_files, key=lambda p: p.stat().st_mtime)
        print(f"Using: {output_path}")
    else:
        output_path = path

    if not output_path.exists():
        print(f"Error: File not found: {output_path}")
        sys.exit(1)

    result = compute_transcript_scores(output_path)
    print_scores(result)
    save_scores_csv(result, output_path)


if __name__ == "__main__":
    main()
