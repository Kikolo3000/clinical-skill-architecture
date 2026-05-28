# Reproducing the npj Digital Medicine Paper

The numbers in Tables 2-4 of the paper come from running the **frozen** pipeline at `extras/paper_reproduction/`, not from the simplified public package. This document shows how to reproduce them.

## TL;DR

```bash
git clone https://github.com/Kikolo3000/clinical-skill-architecture
cd clinical-skill-architecture
pip install -e ".[eval]"
pip install -r extras/paper_reproduction/pinned_requirements.txt

# 1. Generate the synthetic suite (one-time)
python synthetic/generate_all.py

# 2. Score it with the legacy pipeline (~1-2 hours, ~$15 in API costs)
export REQUESTY_API_KEY=...
export REQUESTY_BASE_URL=https://router.requesty.ai/v1
mkdir -p runs/sonnet46_paper
for d in synthetic/instances/*/; do
    id=$(basename "$d")
    python extras/paper_reproduction/score_api.py "$id" \
        --model claude-sonnet-4-6 \
        --output-suffix sonnet46_paper \
        --max-concurrent 3
done

# 3. Evaluate
python -c "
from csa.eval import evaluate_run
print(evaluate_run('synthetic/instances', 'runs/sonnet46_paper'))
"
```

Expected (Table 2 of the paper, Sonnet 4.6 column): clause-level F1 ≈ 0.84, sensitivity ≈ 0.97, decision accuracy ≈ 0.94, weighted kappa ≈ 0.92. Run-to-run variation is < 1 pp on the same model with `temperature=0`.

## Per-table mapping

| Paper artifact                       | Script / config                                                |
|--------------------------------------|----------------------------------------------------------------|
| Table 2 (synthetic, by model)         | `extras/paper_reproduction/score_api.py` × {sonnet46, opus47, haiku45, glm5} |
| Table 3 (per-subscale F1 + κ)         | `evaluate_run().per_subscale` from the same runs               |
| Table 4 (DAIC-WOZ PHQ-8 correlation)  | DAIC-WOZ is licensed and **cannot be redistributed**. See "Replicating Table 4" below. |
| Figure 2 (hierarchical accuracy bar)  | `evaluate_run().hierarchical` rendered as a stacked bar         |
| Figure 3 (confusion matrix)           | `evaluate_run().subscale_confusion`                             |
| Supplement S6/S7 (rater agreement)    | `compare_runs(rater_a, rater_b)` from the public package        |

## Why two pipelines?

The public `clinical-skill-architecture` package (import as `csa`) is a clean reimplementation: smaller surface, sane defaults, fewer flags. The frozen `extras/paper_reproduction/score_api.py` is a verbatim copy of what we ran for the paper. Reviewers can use it to verify that the reported numbers are *exactly* reproducible; downstream users should prefer the public package.

Differences between the two:
- Public package uses Anthropic prompt caching by default; legacy script does not (it goes through Requesty.ai). This affects cost, not output.
- Public package retries on schema violations; legacy script also retries.
- Both use the same `screening.md` and `detail.md` templates and the same 7 `SKILL.md` files.

Run the snapshot test (`pytest tests/test_snapshot.py`) to catch divergence between the two pipelines on the bundled demo instance.

## Replicating Table 4 (DAIC-WOZ)

The DAIC-WOZ corpus (Gratch et al., 2014) requires signing a license agreement with USC ICT. We cannot redistribute the audio, transcripts, or PHQ-8 ground truth. Steps:

1. Apply for DAIC-WOZ access at https://dcapswoz.ict.usc.edu/
2. Place the per-session TSV transcripts under `data/<id>_P/<id>_TRANSCRIPT.csv`
3. Convert with the original conversion script (kept in the research repo, not the public package): `scripts/convert_daic.py` and `scripts/fragment_transcript.py`
4. Score with `extras/paper_reproduction/score_api.py`
5. Correlate against `train_split_Depression_AVEC2017.csv` PHQ-8 totals; expected Spearman ρ ≈ 0.41 for total depression score.

If you cannot obtain DAIC-WOZ, the synthetic Table 2 is the primary validation result.

## Cost estimate

| Validation set                       | Model            | Approx. cost (with caching) |
|--------------------------------------|------------------|------------------------------|
| Synthetic (150 instances, 1 run)      | Claude Sonnet 4.6| $5–8                         |
| Synthetic (150 instances, 1 run)      | Claude Opus 4.7  | $30–50                       |
| Synthetic (150 instances, 1 run)      | Claude Haiku 4.5 | $1–2                         |
| DAIC-WOZ (189 sessions × ~50 frags)   | Claude Sonnet 4.6| $40–60                       |
