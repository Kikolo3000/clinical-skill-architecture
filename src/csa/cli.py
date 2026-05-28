"""
Command-line entry point: ``csa-score``.

Usage:
    csa-score transcript.md
    csa-score transcript.md --model claude-opus-4-7 --backend anthropic
    csa-score transcript.md --csv scores.csv
    csa-score --demo                       # score the bundled SYN_001 demo
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from csa import ScaleAgent, ScoringResult, __version__
from csa.agent import DEFAULT_MODEL


def _print_result(result: ScoringResult) -> None:
    print()
    print(f"  Model:                    {result.model}")
    print(f"  Prompt version:           {result.prompt_version}")
    print(f"  Total word count:         {result.word_count}")
    print(f"  Estimated cost:           ${result.estimated_cost_usd:.4f}")
    print()
    print(f"  Total depression:         {result.total_depression:6.2f}")
    print()
    print("  Subscale scores:")
    for sub, score in result.subscales.items():
        print(
            f"    {sub} {score.name:24s}  score={score.score:6.2f}  "
            f"count={score.count}  weighted_sum={score.weighted_sum}"
        )
    print()
    if result.codings:
        print(f"  Codings ({len(result.codings)}):")
        for c in result.codings:
            print(f"    [{c.subscale}/{c.sub_item}/{c.perspective} w={c.weight}] "
                  f"\"{c.clause}\"")
            print(f"        → {c.rationale}")


def _write_csv(result: ScoringResult, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "fragment_id", "subscale", "sub_item", "perspective",
            "weight", "clause", "rationale",
        ])
        for fr in result.fragments:
            for c in fr.codings:
                w.writerow([
                    fr.fragment.id, c.subscale, c.sub_item, c.perspective,
                    c.weight, c.clause, c.rationale,
                ])


def _write_json(result: ScoringResult, path: Path) -> None:
    path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="csa-score",
        description=(
            "Score a transcript with a Clinical Skill Architecture agent. "
            "v0.1 ships with the Gottschalk-Gleser depression scale."
        ),
    )
    parser.add_argument("transcript", nargs="?", help="Path to a transcript file.")
    parser.add_argument("--demo", action="store_true",
                        help="Score the bundled SYN_001 demo instance instead.")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Model id (default: {DEFAULT_MODEL}).")
    parser.add_argument("--backend", default="anthropic",
                        choices=["anthropic", "openai_compat"])
    parser.add_argument("--max-concurrent", type=int, default=5)
    parser.add_argument("--csv", metavar="PATH", help="Write per-coding rows to CSV.")
    parser.add_argument("--json", metavar="PATH", help="Write the full result as JSON.")
    parser.add_argument("--version", action="version",
                        version=f"clinical-skill-architecture {__version__}")
    args = parser.parse_args(argv)

    if args.demo:
        from csa.eval.synthetic import get_demo_instance
        transcript = get_demo_instance("SYN_001_easy_hopelessness").transcript()
    elif args.transcript:
        transcript = Path(args.transcript).read_text(encoding="utf-8")
    else:
        parser.error("Provide a transcript path or pass --demo.")
        return 2

    agent = ScaleAgent(
        model=args.model,
        backend=args.backend,
        max_concurrent=args.max_concurrent,
    )
    result = agent.score(transcript)

    _print_result(result)
    if args.csv:
        _write_csv(result, Path(args.csv))
        print(f"\n  Wrote CSV → {args.csv}")
    if args.json:
        _write_json(result, Path(args.json))
        print(f"  Wrote JSON → {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
