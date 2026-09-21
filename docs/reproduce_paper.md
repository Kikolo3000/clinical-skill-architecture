# Reproducing the npj Digital Medicine paper

This page maps every number reported in the paper to the model, backend, script and output
that produced it, and gives a reproduction route for each. The paper's primary configuration is
the open-weights **GLM-5** served through an OpenAI-compatible endpoint; the package supports it
directly through the `openai_compat` backend. Claude models were used for the synthetic-suite
model comparison and for two supplementary experiments, through the Claude Code command-line
interface. A complete provenance table (model requested, served identifier where logged,
backend, run date, skill-file commit, script, output file) is Supplementary Note "Result
provenance" of the paper.

> **Correction notice (v0.2.0).** Version 0.1.0 of this document attributed the synthetic
> figures F1 ≈ 0.84 / sensitivity ≈ 0.97 to Claude Sonnet 4.6 and quoted a decision accuracy of
> 0.94, a weighted κ of 0.92, a Cohen's κ of 0.68 and a Spearman ρ ≈ 0.41 that correspond to no
> result file. Those figures were produced by **Claude Opus 4.6** (F1 0.840, sensitivity 0.971,
> precision 0.740, decision accuracy 0.920); Sonnet 4.6 scored F1 0.824. The table numbers
> also referred to an earlier draft. Everything below has been checked against the archived
> outputs; the README and MODEL_CARD carry the same figures.

## Which model produced which number

| Result in the paper | Model (requested) | Backend | Script | Value |
|---|---|---|---|---|
| Construct validity vs PHQ-8, 189 DAIC-WOZ sessions (Results; ablation table) | `zai/GLM-5`, temperature 0 | Requesty router, OpenAI-compatible API | `extras/paper_reproduction/score_api.py` | Pearson r 0.492, Spearman ρ 0.475, AUC 0.702; sensitivity 0.554 / specificity 0.805 at the in-sample Youden cut-point |
| Zero-shot baseline, same 189 sessions | `zai/GLM-5` | same | research repository `baselines/score_api_zeroshot.py` | r 0.595, AUC 0.749; sensitivity 0.804 / specificity 0.594 |
| Expert arm, 48 fragments vs blind three-rater consensus | outputs of the two runs above | offline | research repository `annotation/` | full: sensitivity 0.920, specificity 0.739, F1 0.852, ICC(2,1) 0.211; zero-shot: 0.680 / 0.826 / 0.739, ICC(2,1) 0.533 |
| Synthetic suite, GLM-5 | `zai/GLM-5` | Requesty API | `score_api.py` (research: `synthetic/batch_api.py`) | v1.1: F1 **0.650**, sens 0.644, prec 0.655; v1.0: F1 0.628, sens 0.609, prec 0.648 |
| Synthetic suite, Claude Opus 4.6 | alias `opus` (recorded as Opus 4.6) | Claude Code CLI (`claude -p`) | `score_cli.py` (research: `synthetic/batch_cli.py`) | v1.1: F1 **0.811**, sens 0.960, prec 0.702; v1.0: F1 0.840, sens 0.971, prec 0.740 |
| Synthetic suite, Sonnet 4.6 / Haiku 4.5 (Supplementary Note on model capability) | aliases `sonnet`, `haiku` | Claude Code CLI | `score_cli.py` | v1.0 F1 0.824 / 0.832 |
| Context-window experiment (Supplementary Note) | alias `sonnet` (Sonnet 4.6) | Claude Code CLI | research repository `context_rot/` | 150/150 needles detected |

"v1.0" is the full 150-instance suite; "v1.1" is the de-overlapped 90-instance subset (see
below). The paper reports v1.1 as the headline synthetic result, with v1.0 alongside.

Model identifiers returned by the backends were not logged for these historical runs; the
identifiers above are the ones requested (API) or recorded by the operator in the output suffix
(CLI). Runs executed for the revised manuscript write a `run_manifest.json` next to their output
with the served identifier.

## Route 1 — GLM-5 (primary configuration) with the public package

Any OpenAI-compatible endpoint that serves GLM-5 works (Requesty, OpenRouter, a local vLLM
server). Set the two environment variables and pass the backend explicitly:

```bash
pip install -e ".[eval]"
export OPENAI_API_KEY=...                              # your provider key
export OPENAI_BASE_URL=https://router.requesty.ai/v1   # or your endpoint

python synthetic/generate_all.py                       # writes synthetic/instances/ (v1.0, 150)

mkdir -p runs/glm5
for d in synthetic/instances/*/; do
    id=$(basename "$d")
    mkdir -p "runs/glm5/$id"
    csa-score "$d/transcript.md" --model zai/GLM-5 --backend openai_compat \
        --json "runs/glm5/$id/output.jsonl"
done

python - <<'PY'
from csa.eval import evaluate_run
import json
full = evaluate_run("synthetic/instances", "runs/glm5")                 # v1.0
v11 = set(json.load(open("synthetic/suite_v11.json"))["instances"])
clean = evaluate_run("synthetic/instances", "runs/glm5", instance_ids=v11)  # v1.1
print(full.detection_f1, clean.detection_f1)
PY
```

Expected: detection F1 ≈ 0.63 on v1.0 and ≈ 0.65 on v1.1 for GLM-5. Run-to-run variation at
temperature 0 through a router is small but not zero (the paper's five-run repeat at
temperature 0.7 agreed with the deterministic run on 92% of fragment–subscale decisions).

The public package is a clean reimplementation with the same skill files and prompt templates
as the research pipeline; the `extras/paper_reproduction/` scripts are adapted copies of the
research scripts kept for reference. `pytest tests/test_snapshot.py` checks that the two agree
on the bundled demo instance.

## Route 2 — Claude models (synthetic model comparison)

The Opus 4.6, Sonnet 4.6 and Haiku 4.5 results were produced through the Claude Code CLI, which
resolves the alias passed on the command line to the current model of that tier at run time.
To reproduce with the package instead, use the `anthropic` backend with an explicit identifier:

```bash
export ANTHROPIC_API_KEY=...
csa-score synthetic/instances/SYN_001_PURE_EASY_HOP/transcript.md \
    --model claude-opus-4-6 --backend anthropic --json out.jsonl
```

Because the CLI harness and the API backend differ in tooling (the CLI writes output files
through tools; the API returns JSON), small differences from the published Opus figures are
expected; the paper's Supplementary Note on model capability discusses the size of such
differences across models and batching conditions.

## Route 3 — DAIC-WOZ construct validity

DAIC-WOZ (Gratch et al., 2014) is licensed by USC ICT and cannot be redistributed, including
transcripts and PHQ-8 scores. To reproduce the construct-validity results:

1. Obtain DAIC-WOZ at https://dcapswoz.ict.usc.edu/ and place `data/<id>_P/<id>_TRANSCRIPT.csv`.
2. Convert and fragment with the research repository's `scripts/convert_daic.py` and
   `scripts/fragment_transcript.py` (Ellie → `I`, participant → `S`; consecutive same-speaker
   turns merged; sessions 342, 394, 398, 460 excluded).
3. Score all 189 sessions with GLM-5 (Route 1 backend), or with
   `extras/paper_reproduction/score_api.py 300 --model zai/GLM-5`.
4. Aggregate with `extras/paper_reproduction/compute_scores.py` and correlate the total
   depression score with PHQ-8 across all three AVEC splits (189 sessions). Expected with
   GLM-5: Pearson r ≈ 0.49, Spearman ρ ≈ 0.48, AUC ≈ 0.70. The classification cut-point in the
   paper was selected by Youden's J on the same sample and is therefore in-sample; the paper
   also reports leave-one-out values.

No Claude model was run on DAIC-WOZ for the paper's main tables (a partial Sonnet run over 91
sessions and an Opus run over 32 sessions exist in the research repository and are not reported).

## Why the package defaults to a hosted Anthropic model

`csa.score()` defaults to `claude-sonnet-4-6` on the `anthropic` backend because it is the
simplest first run for most users (one key, prompt caching, no endpoint configuration). It is
**not** the configuration validated in the paper. The paper's primary configuration is GLM-5
through `openai_compat`, chosen because open weights can be served on institutional
infrastructure under clinical-data constraints; switching to it is one argument
(`--model zai/GLM-5 --backend openai_compat`). Any model other than those listed above is
unvalidated, and the published figures do not transfer to it.

## The de-overlapped suite (v1.1)

Sixty of the 150 v1.0 instances contain a ground-truth clause that reproduces an example
sentence quoted in a skill file (an audit is in the paper's Supplementary Note on suite
independence). `synthetic/independence_gate.py` implements the rule (sequence ratio ≥ 0.7 or a
shared five-token phrase with any skill-file example) and `synthetic/suite_v11.json` lists the
90 instances that pass it. Evaluate on v1.1 by passing that list as `instance_ids` (see Route 1).
New instances added to the suite must pass the gate.

## Cost estimate (synthetic suite, 150 instances, one run)

| Model | Backend | Approx. cost |
|---|---|---|
| GLM-5 via Requesty | `openai_compat` | $3–6 |
| Claude Haiku 4.5 | `anthropic` | $1–2 |
| Claude Sonnet 4.6 | `anthropic` (caching) | $5–8 |
| Claude Opus 4.6 | `anthropic` (caching) | $30–50 |
