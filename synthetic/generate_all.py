#!/usr/bin/env python3
"""
Generate the full 150-instance synthetic test suite.

Reads `instance_defs.py` (a pure data file) and writes one directory per
instance under `synthetic/instances/<id>/` with three files:

    transcript.md      — the dialogue in I:/S: format
    input.jsonl        — fragments ready for `csa-score`
    ground_truth.jsonl — expected agent output (decision, codings, summaries)

Run once after cloning the repo, then evaluate with:

    from csa.eval import evaluate_run
    report = evaluate_run("synthetic/instances", "your_pred_dir")

Usage:
    python synthetic/generate_all.py
    python synthetic/generate_all.py --type PURE
    python synthetic/generate_all.py --ids SYN_001_PURE_EASY_HOP SYN_002_PURE_EASY_HOP
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUBSCALES = ("HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS")


def _build_transcript(instance: dict) -> str:
    return "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in instance["turns"])


def _build_input(instance: dict) -> str:
    fragments = []
    counter = 1
    for i, turn in enumerate(instance["turns"]):
        if turn["speaker"] != "S":
            continue
        ctx_start = max(0, i - 5)
        ctx_lines = [
            f"{instance['turns'][j]['speaker']}: {instance['turns'][j]['text']}"
            for j in range(ctx_start, i)
        ]
        fragments.append({
            "id": f"{instance['id']}_{counter:04d}",
            "line_number": i + 1,
            "close_context": "\n".join(ctx_lines),
            "study_excerpt": turn["text"],
        })
        counter += 1
    return json.dumps(fragments, indent=2, ensure_ascii=False)


def _build_ground_truth(instance: dict) -> str:
    gt_by_fragment: dict[int, dict] = {gt["fragment"]: gt for gt in instance.get("ground_truth", [])}
    lines: list[str] = []
    counter = 1
    for turn in instance["turns"]:
        if turn["speaker"] != "S":
            continue
        gt = gt_by_fragment.get(counter, {})
        codings = gt.get("codings", [])
        word_count = len(turn["text"].split())

        if codings:
            decision = "needs_analysis"
            flagged = sorted({c["subscale"] for c in codings})
            summaries = {
                sub: {
                    "count": sum(1 for c in codings if c["subscale"] == sub),
                    "weighted_sum": sum(c["weight"] for c in codings if c["subscale"] == sub),
                    "items_found": sorted({c["sub_item"] for c in codings if c["subscale"] == sub}),
                }
                for sub in SUBSCALES
            }
        else:
            decision = "no_depressive_content"
            flagged = []
            summaries = {sub: {"count": 0, "weighted_sum": 0, "items_found": []} for sub in SUBSCALES}

        lines.append(json.dumps({
            "id": f"{instance['id']}_{counter:04d}",
            "screening": {
                "decision": decision,
                "flagged_subscales": flagged,
                "screening_rationale": gt.get("rationale", "Synthetic ground truth."),
            },
            "codings": codings,
            "subscale_summaries": summaries,
            "word_count": word_count,
            "analyzed_at": "2026-03-14T00:00:00Z",
        }, ensure_ascii=False))
        counter += 1
    return "\n".join(lines)


def write_instance(instance: dict, root: Path) -> None:
    inst_dir = root / instance["id"]
    inst_dir.mkdir(parents=True, exist_ok=True)
    (inst_dir / "transcript.md").write_text(_build_transcript(instance), encoding="utf-8")
    (inst_dir / "input.jsonl").write_text(_build_input(instance), encoding="utf-8")
    (inst_dir / "ground_truth.jsonl").write_text(_build_ground_truth(instance), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--output", default="synthetic/instances",
                        help="Where to write generated instances (default: synthetic/instances)")
    parser.add_argument("--type", default=None,
                        choices=["PURE", "MULTI", "MCODE", "DIST", "DENY", "NEG"])
    parser.add_argument("--ids", nargs="+", default=None)
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).parent))
    from instance_defs import ALL_INSTANCES  # type: ignore
    # v0.2.0: report ground-truth clauses that reproduce a skill-file example. Suite v1.0 is
    # published as is (60 instances fail the gate; see suite_v11.json for the clean subset);
    # NEW instances must pass it. Pass --strict to refuse generation on any violation.
    try:
        from independence_gate import audit_instances  # type: ignore
        _viol = audit_instances(ALL_INSTANCES)
        if _viol:
            print(f"independence gate: {sum(len(v) for v in _viol.values())} clause(s) in "
                  f"{len(_viol)} instance(s) reproduce a skill-file example; the clean subset is "
                  f"synthetic/suite_v11.json", file=sys.stderr)
            if "--strict" in sys.argv:
                return 1
    except ImportError:
        pass

    instances = ALL_INSTANCES
    if args.type:
        instances = [i for i in instances if i["type"] == args.type]
    if args.ids:
        wanted = set(args.ids)
        instances = [i for i in instances if i["id"] in wanted]

    if not instances:
        print("No instances matched the filters.", file=sys.stderr)
        return 1

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    for inst in instances:
        write_instance(inst, out)
    print(f"Wrote {len(instances)} instances to {out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
