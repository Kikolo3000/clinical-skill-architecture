#!/usr/bin/env python3
"""Independence gate: no synthetic ground-truth clause may reproduce a skill-file example.

Added in v0.2.0 (paper revision). The gate is enforced by generate_all.py at generation time and can be run standalone to define the de-overlapped
suite (v1.1) as the subset of instances with no violating clause.

A clause violates the gate when, after normalisation (lower-case, straight apostrophes,
punctuation removed), it either
  * reaches a character sequence ratio >= RATIO_THRESHOLD with any quoted skill-file phrase of
    three or more tokens, or
  * shares a contiguous phrase of NGRAM tokens or more with any such skill-file phrase.

Usage (standalone):
  python synthetic/independence_gate.py             # audit instance_defs.py, write suite_v11.json
  python synthetic/independence_gate.py --strict    # exit 1 if any violation
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "src" / "csa" / "scales" / "gg_depression" / "skills"
SUBSCALES = ["HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS"]
RATIO_THRESHOLD = 0.7
NGRAM = 5
MIN_PHRASE_TOKENS = 3
_JSON_KEY = re.compile(r'^\s*"(clause|subscale|sub_item|perspective|weight|rationale)"')


def normalize(text: str) -> str:
    text = text.lower().replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"').replace("—", " ").replace("–", " ")
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_skill_phrases(skills_dir: Path = SKILLS_DIR) -> list[dict]:
    """Every quoted phrase of >= MIN_PHRASE_TOKENS tokens in the seven coding skills."""
    phrases = []
    for sub in SUBSCALES:
        path = skills_dir / sub / "SKILL.md"
        if not path.exists():
            continue
        for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _JSON_KEY.match(line):
                continue
            for q in re.findall(r'"([^"]+)"', line):
                if len(q.split()) >= MIN_PHRASE_TOKENS and "answered" not in q:
                    phrases.append({"skill": sub, "line": ln, "text": q, "norm": normalize(q)})
    return phrases


def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def clause_violations(clause: str, phrases: list[dict]) -> list[dict]:
    """Skill phrases that the clause reproduces, with the reason."""
    nc = normalize(clause)
    toks = nc.split()
    grams = _ngrams(toks, NGRAM)
    out = []
    for p in phrases:
        ratio = SequenceMatcher(None, nc, p["norm"]).ratio()
        shared = bool(grams & _ngrams(p["norm"].split(), NGRAM)) if grams else False
        if ratio >= RATIO_THRESHOLD or shared:
            out.append({"skill": p["skill"], "line": p["line"], "phrase": p["text"],
                        "ratio": round(ratio, 3), "shared_ngram": shared})
    return out


def audit_instances(instances: list[dict], phrases: list[dict] | None = None) -> dict:
    """Return {instance_id: [violations]} for every ground-truth clause; empty dict = clean."""
    phrases = phrases or load_skill_phrases()
    result = {}
    for inst in instances:
        hits = []
        for gt in inst.get("ground_truth", []):
            for c in gt.get("codings", []):
                v = clause_violations(c["clause"], phrases)
                if v:
                    hits.append({"clause": c["clause"], "sub_item": c.get("sub_item"), "violations": v})
        if hits:
            result[inst["id"]] = hits
    return result


def load_instance_defs(path: Path = ROOT / "synthetic" / "instance_defs.py") -> list[dict]:
    spec = importlib.util.spec_from_file_location("instance_defs", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ALL_INSTANCES


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="exit 1 if any violation is found")
    ap.add_argument("--output", default=str(ROOT / "synthetic" / "suite_v11.json"),
                    help="where to write the de-overlapped suite definition")
    args = ap.parse_args()

    instances = load_instance_defs()
    violations = audit_instances(instances)
    clean = [i["id"] for i in instances if i["id"] not in violations]
    by_type = Counter(i["type"] for i in instances)
    by_diff = Counter(i["difficulty"] for i in instances)
    kept_type = Counter(i["type"] for i in instances if i["id"] in clean)
    kept_diff = Counter(i["difficulty"] for i in instances if i["id"] in clean)
    n_clauses = sum(len(c) for i in instances for g in i.get("ground_truth", []) for c in [g.get("codings", [])])
    n_clauses_kept = sum(len(g.get("codings", [])) for i in instances if i["id"] in clean for g in i.get("ground_truth", []))
    n_viol_clauses = sum(len(h) for h in violations.values())
    out = {
        "version": "1.1",
        "definition": ("Instances of suite v1.0 with no ground-truth clause reaching sequence ratio "
                       f">= {RATIO_THRESHOLD} with, or sharing a {NGRAM}-token phrase with, any quoted "
                       "skill-file example (independence_gate.py)."),
        "n_instances_v10": len(instances), "n_instances_v11": len(clean),
        "n_gt_clauses_v10": n_clauses, "n_gt_clauses_v11": n_clauses_kept,
        "n_violating_clauses": n_viol_clauses, "n_excluded_instances": len(violations),
        "coverage_by_type": {t: {"v10": by_type[t], "v11": kept_type[t]} for t in by_type},
        "coverage_by_difficulty": {d: {"v10": by_diff[d], "v11": kept_diff[d]} for d in by_diff},
        "instances": clean,
        "excluded": {k: [{"clause": h["clause"], "sub_item": h["sub_item"],
                          "best": max(h["violations"], key=lambda v: v["ratio"])} for h in hs]
                     for k, hs in violations.items()},
    }
    Path(args.output).write_text(json.dumps(out, indent=1))
    print(f"instances: {len(instances)} -> {len(clean)} clean ({len(violations)} excluded, "
          f"{n_viol_clauses} violating clauses of {n_clauses})")
    print("by type:", {t: f"{kept_type[t]}/{by_type[t]}" for t in by_type})
    print("by difficulty:", {d: f"{kept_diff[d]}/{by_diff[d]}" for d in by_diff})
    print("wrote", args.output)
    if args.strict and violations:
        sys.exit(1)


if __name__ == "__main__":
    main()
