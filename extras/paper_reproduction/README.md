# Paper Reproduction (frozen)

The exact scripts used to produce Tables 2-4 in:

> Gutiérrez E., Zhang Y., Navarro J.-B., Barajas A. (2026). _Translating rating-scale ontologies into LLM agents: a general framework for ambient clinical phenotyping._ **npj Digital Medicine** *(submitted)*.

These files are **frozen verbatim copies** of the research-grade pipeline at the time of submission. They are intentionally _not_ refactored, _not_ kept in sync with the public `clinical-skill-architecture` package, and _not_ a recommended starting point for new work. Use the public package instead.

## What's here

| File                     | Purpose                                                                                |
|--------------------------|-----------------------------------------------------------------------------------------|
| `score_api.py`           | Two-stage screening + detail orchestrator using OpenAI-compatible APIs (Requesty.ai)   |
| `score_cli.py`           | Same pipeline implemented via `claude -p` subprocess calls (Claude Code CLI)            |
| `fragment_transcript.py` | Markdown transcript → per-utterance JSONL                                               |
| `compute_scores.py`      | Apply the G-G formula to one session's output                                           |
| `validate_output.py`     | Schema + perspective/weight consistency validator                                       |
| `pinned_requirements.txt`| Exact dependency versions at submission                                                 |

## Reproducing a published number

```bash
# 1. Clone the repo and enter this directory
cd extras/paper_reproduction
pip install -r pinned_requirements.txt

# 2. Generate the synthetic suite (see ../../synthetic/README.md)
python ../../synthetic/generate_all.py

# 3. Score each instance using the legacy script (mirrors paper experiments)
for d in ../../synthetic/instances/*/; do
    python score_api.py "$(basename $d)" \
        --model claude-sonnet-4-6 --output-suffix sonnet46_run1 \
        --max-concurrent 3
done

# 4. Evaluate against ground truth
python -m csa.eval --gt-dir ../../synthetic/instances --pred-dir runs/sonnet46_run1
```

The Tables 2-4 numbers correspond to the configurations listed in `MODEL_CARD.md`. Differences greater than ±0.5 percentage points should be reported as an issue.

## Why we keep these here instead of in the package

- The public `clinical-skill-architecture` package (import as `csa`) is intentionally simpler than the paper pipeline (single async backend, sensible defaults, fewer flags). That simplicity is good for users but creates a tiny risk of subtle behavioural drift from the paper.
- These frozen scripts let reviewers and downstream researchers reproduce the **exact** numbers without trusting that we kept the public package bug-for-bug compatible.
- They depend on the Claude Code CLI (`score_cli.py`) or a Requesty.ai API key (`score_api.py`), which are not appropriate dependencies for a public Python package.
