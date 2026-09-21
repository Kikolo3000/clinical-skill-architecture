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

## Suite v1.0 and v1.1

The 150 instances above are **suite v1.0**. An audit for the paper's revision found that 60 of them contain a ground-truth clause that reproduces an example sentence quoted in one of the skill files (the generator had reused examples it was shown). `independence_gate.py` implements the independence rule (no clause may reach a character sequence ratio ≥ 0.7 with, or share a five-token phrase with, any skill-file example) and `suite_v11.json` lists the 90 instances that pass it (**suite v1.1**; 177 ground-truth codings). The paper reports v1.1 as the headline synthetic result and v1.0 alongside; stratifying the published runs showed no detection advantage on the overlapping clauses. New instances must pass the gate:

```bash
python synthetic/independence_gate.py            # audit and rewrite suite_v11.json
python synthetic/generate_all.py --strict        # refuse to generate if any instance fails
```

## Files

| File                  | What it is                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `instance_defs.py`    | Pure data — every instance as a Python dict (turns + ground-truth codings) |
| `generate_all.py`     | Reads `instance_defs.py` and writes one directory per instance to disk     |
| `suite_manifest.json` | Per-instance metadata: type, difficulty, primary subscale, codings count   |
| `independence_gate.py`| Skill-file independence gate; defines suite v1.1                           |
| `suite_v11.json`      | The 90 instance IDs of suite v1.1 with coverage by type and difficulty     |
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
export OPENAI_API_KEY=... OPENAI_BASE_URL=https://router.requesty.ai/v1   # any GLM-5 endpoint
mkdir -p runs/glm5
for d in synthetic/instances/*/; do
    id=$(basename "$d")
    mkdir -p "runs/glm5/$id"
    csa-score "$d/transcript.md" --model zai/GLM-5 --backend openai_compat \
        --json "runs/glm5/$id/output.jsonl"
done
```

## Evaluating results

```python
from csa.eval import evaluate_run

import json
report = evaluate_run("synthetic/instances", "runs/glm5")            # v1.0
print(report)                  # pretty text table
report.detection_f1            # ≈ 0.63 for GLM-5 (0.84 for Claude Opus 4.6)
v11 = json.load(open("synthetic/suite_v11.json"))["instances"]
evaluate_run("synthetic/instances", "runs/glm5", instance_ids=v11).detection_f1   # ≈ 0.65 (v1.1)
```

Three of the 150 instances ship inside the wheel (in `csa.data.demo`) so you can try the evaluator without regenerating anything — see `notebooks/02_synthetic_validation.ipynb`.

## Reproducing the paper's synthetic results

`docs/reproduce_paper.md` lists, per model, which script and backend produced each published number and the expected values on v1.0 and v1.1.
