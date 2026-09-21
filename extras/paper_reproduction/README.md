# Paper Reproduction (frozen)

Adapted copies of the scripts used to produce the results in:

> Gutiérrez E., Zhang Y., Navarro J.-B., Barajas A. (2026). _Translating clinical rating scale ontologies into auditable ambient LLM coding agents._ **npj Digital Medicine** *(under revision)*.

These files are **adapted copies** of the research-pipeline scripts (paths and defaults edited for this package; the research repository holds the exact scripts and their commit history, which the paper's provenance table cites by hash). They are intentionally _not_ refactored, _not_ kept in sync with the public `clinical-skill-architecture` package, and _not_ a recommended starting point for new work. Use the public package instead; `docs/reproduce_paper.md` gives the reproduction routes and the model behind every reported number.

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

# 3. Score each instance with the paper's primary model (GLM-5 through an OpenAI-compatible
#    endpoint; the Claude runs in the paper used score_cli.py through the Claude Code CLI)
export REQUESTY_API_KEY=... REQUESTY_BASE_URL=https://router.requesty.ai/v1
for d in ../../synthetic/instances/*/; do
    python score_api.py "$(basename $d)" \
        --model zai/GLM-5 --output-suffix glm5_run1 \
        --max-concurrent 3
done

# 4. Evaluate against ground truth
python -m csa.eval --gt-dir ../../synthetic/instances --pred-dir runs/sonnet46_run1
```

Expected values per model and suite version are in `docs/reproduce_paper.md`. Differences greater than a few percentage points on the same model should be reported as an issue, together with the served model identifier.

## Why we keep these here instead of in the package

- The public `clinical-skill-architecture` package (import as `csa`) is intentionally simpler than the paper pipeline (single async backend, sensible defaults, fewer flags). That simplicity is good for users but creates a tiny risk of subtle behavioural drift from the paper.
- These scripts let reviewers and downstream researchers follow the research pipeline's control flow without trusting that we kept the public package bug-for-bug compatible; the exact numbers are tied to the research repository commits listed in the paper's provenance table.
- They depend on the Claude Code CLI (`score_cli.py`) or a Requesty.ai API key (`score_api.py`), which are not appropriate dependencies for a public Python package.
