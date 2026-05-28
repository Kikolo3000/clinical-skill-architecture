# Synthetic Test Suite

The 150 instances used to validate the agent in the npj Digital Medicine paper. Each instance is a short, hand-crafted clinical-interview-style dialogue with **known-by-design** ground truth: every clause that should be coded, every distractor that should be ignored.

## Stratification

| Type    | Description                                          | Count |
|---------|------------------------------------------------------|-------|
| `PURE`  | Single subscale, clear pathology                     | 54    |
| `MULTI` | Multiple subscales in one fragment                   | 25    |
| `MCODE` | Multiple codings per fragment, same/related subscale | 15    |
| `DIST`  | High distractor density — tests false-positive avoidance | 15 |
| `DENY`  | Explicit denial / minimisation of symptoms           | 10    |
| `NEG`   | True negatives (no depression content)               | 31    |

Difficulty levels: `EASY`, `MOD`, `HARD`, `ADV`. See `suite_manifest.json` for the per-instance breakdown.

## Files

| File                  | What it is                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `instance_defs.py`    | Pure data — every instance as a Python dict (turns + ground-truth codings) |
| `generate_all.py`     | Reads `instance_defs.py` and writes one directory per instance to disk     |
| `suite_manifest.json` | Per-instance metadata: type, difficulty, primary subscale, codings count   |
| `instances/`          | Generated on demand. Gitignored.                                           |

## Regenerating the suite

```bash
# All 150
python synthetic/generate_all.py

# One subset
python synthetic/generate_all.py --type DIST

# One instance
python synthetic/generate_all.py --ids SYN_001_PURE_EASY_HOP
```

Each `instances/<id>/` directory will contain three files:

- `transcript.md` — the dialogue in `I:`/`S:` format
- `input.jsonl` — fragments ready to score with `csa-score`
- `ground_truth.jsonl` — expected agent output (one record per `S:` turn)

## Running the agent on it

```bash
mkdir -p runs/sonnet_46
for d in synthetic/instances/*/; do
    id=$(basename "$d")
    mkdir -p "runs/sonnet_46/$id"
    csa-score "$d/transcript.md" --json "runs/sonnet_46/$id/output.jsonl"
done
```

## Evaluating results

```python
from csa.eval import evaluate_run

report = evaluate_run("synthetic/instances", "runs/sonnet_46")
print(report)                  # pretty text table
report.detection_f1            # 0.84
report.per_subscale["HOP"].f1  # 0.90
```

Three of the 150 instances ship inside the wheel (in `csa.data.demo`) so you can try the evaluator without regenerating anything — see `notebooks/02_synthetic_validation.ipynb`.

## Reproducing paper Tables 2-4

The numbers in the npj DM paper come from running `extras/paper_reproduction/score_api.py` with pinned dependencies. See `docs/reproduce_paper.md`.
