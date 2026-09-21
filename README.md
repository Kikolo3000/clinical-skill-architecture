# clinical-skill-architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](pyproject.toml)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Kikolo3000/clinical-skill-architecture/blob/main/notebooks/01_quickstart.ipynb)
[![Tests](https://github.com/Kikolo3000/clinical-skill-architecture/actions/workflows/test.yml/badge.svg)](https://github.com/Kikolo3000/clinical-skill-architecture/actions/workflows/test.yml)
[![Prompt v1.0.0](https://img.shields.io/badge/prompt%20version-1.0.0-informational)](MODEL_CARD.md)

> **A framework for translating clinical rating-scale ontologies into LLM-driven coding agents.**
> Companion code for *npj Digital Medicine* (2026).

Most clinical rating scales are coded by hand. A trained rater reads a transcript and decides, clause by clause, which constructs are present and how strongly. The procedure is slow, expensive, and notoriously hard to reproduce across raters and across studies.

The **Clinical Skill Architecture** is a recipe for turning the operational definitions inside any such scale into an LLM-driven agent that performs the same coding automatically. Each construct is described in its own *skill file*; a generic two-stage orchestrator (screening → per-construct detail) reads those skill files at inference time and emits the scale's canonical hierarchical output. The agent is validated against a synthetic suite of instances with known-by-design ground truth, so accuracy can be reported per construct, per perspective, and per weight tier.

> **v0.2 ships with one fully-implemented scale — the Gottschalk-Gleser depression scale (G-G).** The framework itself is scale-agnostic; the recipe for porting it to your own ontology is in [Adapting the framework to your own scale](#adapting-the-framework-to-your-own-scale).

```python
from csa import score   # convenience entry — defaults to the G-G depression scale

result = score(
    "I just don't see the point anymore. Nothing's going to change. "
    "I went to work today though.",
    model="claude-sonnet-4-6",
)

print(f"Total depression: {result.total_depression:.2f}")
print(f"Hopelessness:     {result.subscales['HOP'].score:.2f}")
for c in result.codings:
    print(f"  [{c.subscale}/{c.sub_item}] \"{c.clause}\" — {c.rationale}")
```

## Table of contents

- [Paper](#paper)
- [Try it now](#try-it-now)
- [Install](#install)
- [Quickstart](#quickstart)
- [What does the output mean?](#what-does-the-output-mean)
- [Validation results](#validation-results)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Reproducing the paper](#reproducing-the-paper)
- [Adapting the framework to your own scale](#adapting-the-framework-to-your-own-scale)
- [Disclaimer](#disclaimer)
- [Citation](#citation)
- [License & acknowledgements](#license--acknowledgements)

## Paper

Gutiérrez E., Zhang Y., Navarro J.-B., Barajas A. (2026). *Translating clinical rating scale ontologies into auditable ambient LLM coding agents.* **npj Digital Medicine** *(under revision)*.

See [`CITATION.cff`](CITATION.cff) for a machine-readable citation block.

## Try it now

Click the Colab badge at the top of this README — it opens [`notebooks/01_quickstart.ipynb`](notebooks/01_quickstart.ipynb) in Google Colab. Paste your Anthropic API key into the first cell and run all cells (~3 minutes, ~$0.01 in API costs).

Three notebooks are bundled:

| Notebook                                                         | What it shows                                                                                  | Approx. cost |
|------------------------------------------------------------------|------------------------------------------------------------------------------------------------|--------------|
| [`01_quickstart.ipynb`](notebooks/01_quickstart.ipynb)           | The minimum 5 cells: install, set the key, score one short transcript, plot subscale scores.  | $0.01        |
| [`02_synthetic_validation.ipynb`](notebooks/02_synthetic_validation.ipynb) | The flagship demo: agent vs ground truth on 3 hand-crafted instances + hierarchical accuracy chart. | $0.05 |
| [`03_real_transcript.ipynb`](notebooks/03_real_transcript.ipynb) | A realistic 15-turn synthetic clinical-interview transcript scored end-to-end.                  | $0.10        |

## Install

```bash
# Basic — framework + the bundled G-G depression scale
pip install clinical-skill-architecture

# With evaluation harness (kappa, Clopper-Pearson CIs, hierarchical accuracy)
pip install "clinical-skill-architecture[eval]"

# Plus matplotlib + pandas for the notebooks
pip install "clinical-skill-architecture[eval,viz]"
```

The package installs as the import name **`csa`** (e.g. `from csa import score`).

Requires Python ≥ 3.11.

Set one of:

```bash
export ANTHROPIC_API_KEY=sk-ant-...        # default backend
# or, for OpenAI-compatible providers
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://router.requesty.ai/v1
```

## Quickstart

### Score a transcript

```python
from csa import score

# Free-form input — wrapped as a one-turn S: utterance
result = score("I feel hopeless. Nothing's going to change.")

# Multi-turn dialogue — labelled lines (I:/S:, P1:/P2:, "Speaker 1:" etc.)
transcript = """\
I: how have you been feeling about the future
S: i just don't see the point anymore
I: tell me more
S: i went to work today though
"""
result = score(transcript, model="claude-sonnet-4-6")
```

`score()` is a convenience entry point that defaults to the bundled G-G depression scale. The full form is `from csa.scales.gg_depression import score` (identical behaviour, different name).

### Inspect the result

```python
result.total_depression                # float — sum of 7 subscale scores
result.subscales["HOP"].score          # G-G score for Hopelessness
result.subscales["HOP"].weighted_sum   # raw weighted clause count
result.codings                         # tuple[Coding, ...] — every clause flagged
result.fragments                       # tuple[FragmentResult, ...] — per-utterance breakdown
result.estimated_cost_usd              # cost so far (uses backend-reported tokens)
result.to_dict()                       # everything, JSON-serialisable
```

### Score many transcripts

```python
import asyncio
from csa import ScaleAgent

agent = ScaleAgent(model="claude-sonnet-4-6", max_concurrent=10)
results = asyncio.run(asyncio.gather(*[agent.score_async(t) for t in transcripts]))
```

### Use the CLI

```bash
csa-score path/to/transcript.md
csa-score path/to/transcript.md --model claude-opus-4-7 --csv scores.csv
csa-score --demo                       # run on the bundled SYN_001 example
```

## What does the output mean?

The agent emits the canonical Gottschalk-Gleser output: a per-clause `Coding` plus aggregated subscale scores.

| Subscale | Name                       | What it captures                                            |
|----------|----------------------------|-------------------------------------------------------------|
| **HOP**  | Hopelessness               | Despair, futility, lack of confidence, loss of motivation   |
| **SAC**  | Self-accusation            | Guilt, shame, self-blame, suicidal ideation                 |
| **PMR**  | Psychomotor retardation    | Lack of energy, fatigue, slowness, passivity                |
| **SOM**  | Somatic concerns           | Bodily complaints, illness fears, pain, dysfunction          |
| **DAM**  | Death and mutilation       | References to death, harm, loss of body integrity           |
| **SEP**  | Separation depression      | Loss of relationships, abandonment, exclusion                |
| **HOS**  | Hostility outward          | Anger, resentment, irritability toward others                |

Each clause is also tagged with its **perspective** — `self` (weight 3), `others` (weight 2), `inanimate` (weight 1), or `denial` (weight 1). HOP / PMR / SOM use a flat weight of 1 regardless of perspective.

The score for each subscale is

```
score = sqrt((weighted_sum + 0.5) * 100 / word_count)
```

and the **total depression score** is the sum of the 7 subscale scores. Higher = more depressive content.

## Validation results

The paper validates the G-G agent in three arms with three different reference standards. The numbers below are from the paper (prompt v1.0.0); each applies only to the model named. The paper's **primary configuration is the open-weights GLM-5** (`--backend openai_compat`); Claude Opus 4.6 was run on the synthetic suite as a proprietary comparison. The package default (`claude-sonnet-4-6`) is a convenience for a first run, not a validated configuration.

| Arm / reference standard | Metric | GLM-5 | Claude Opus 4.6 |
|---|---|---|---|
| Synthetic suite v1.1 (90 de-overlapped instances, known ground truth) | clause detection F1 | **0.650** | **0.811** |
| Synthetic suite v1.0 (all 150 instances) | clause detection F1 | 0.629 | 0.840 |
| Expert arm (48 DAIC-WOZ fragments, blind 3-rater consensus) | fragment screening sensitivity / specificity | 0.92 / 0.74 | — |
| Expert arm | weighted-sum ICC(2,1) vs consensus | 0.21 | — |
| Construct validity (189 DAIC-WOZ sessions, PHQ-8 self-report) | Pearson r / AUC | 0.49 / 0.70 | — |

The agent detects consensus-positive fragments well but over-codes within flagged subscales, so its aggregate weighted scores are inflated relative to human coders (ICC 0.21); precision against expert consensus is low for HOP, SAC and SEP (0.13–0.19). Read the expert-arm and PHQ-8 rows as what they are: fragment-level agreement with raters and participant-level association with a self-report questionnaire, not diagnostic accuracy. Full tables, per-subscale values and the provenance of every number are in [`MODEL_CARD.md`](MODEL_CARD.md) and [`docs/reproduce_paper.md`](docs/reproduce_paper.md).

## Architecture

Two-stage pipeline:

1. **Screening** — one LLM call per fragment using the full G-G ontology. Liberal flagging mandate (false positives are cheap; false negatives are costly). Returns `decision`, `flagged_subscales`, `screening_rationale`.
2. **Detail** — for every flagged subscale, a separate LLM call with that subscale's `SKILL.md` loaded into the system prompt. Returns clause-level codings with sub-item, perspective, weight, and rationale.

Both stages re-use the same large system prompt, so **prompt caching** is enabled by default in the Anthropic backend (5–10× cost reduction). See [`docs/architecture.md`](docs/architecture.md) for diagrams and the prompt layout.

## Configuration

| Knob              | Where                        | Default              |
|-------------------|------------------------------|-----------------------|
| Model             | `score(model=...)`           | `claude-sonnet-4-6`  |
| Backend           | `score(backend=...)`         | `"anthropic"`        |
| Max concurrent    | `ScaleAgent(max_concurrent=...)`| 5                 |
| Target speakers   | `score(target_speakers=...)` | every non-first speaker |

Backends:
- `anthropic` — default. Reads `ANTHROPIC_API_KEY`. Prompt caching enabled.
- `openai_compat` — for any provider speaking the OpenAI Chat Completions API (Requesty.ai, OpenRouter, vLLM, Ollama). Reads `OPENAI_API_KEY` and `OPENAI_BASE_URL`.

## Reproducing the paper

[`docs/reproduce_paper.md`](docs/reproduce_paper.md) maps every reported number to its model, backend, script and output file and gives a reproduction route for each, with GLM-5 through `openai_compat` as the primary route. Adapted copies of the research-pipeline scripts are kept under [`extras/paper_reproduction/`](extras/paper_reproduction/) for reference.

## Adapting the framework to your own scale

The bundled G-G depression scale is a worked example of a more general recipe: **translate a clinical rating scale into an LLM-driven coding agent, then iterate against a synthetic ground-truth suite until it agrees with you.** The same five steps work for any content-analysis instrument — Hamilton Anxiety, PANSS positive/negative symptoms, the Linguistic Inquiry and Word Count categories, your own bespoke ontology — provided the construct can be defined in prose and recognised in language.

You do not have to fork this repository to follow the recipe; you can use the file layout below as a template and import only the pieces you need (the evaluation harness in `csa.eval` is scale-agnostic and reusable as-is).

### Step 1 — Write one *skill file* per phenomenon

A skill file is a single Markdown document that defines one construct your scale measures: what counts, what does not, edge cases, and a handful of canonical examples. It is the *operational definition* a human rater would internalise during training, written down as a prompt the LLM reads at inference time.

Start from the official scale documentation and the original validation studies — they are the source of truth. Extract each construct, write its definition, then add 5–15 hand-picked examples (positive, near-miss, distractor) with one-line rationales. This is your **v0.1**; expect it to evolve as you discover failure modes in Step 4.

LLMs are very useful drafting partners here: paste the relevant manual section into Claude or GPT and ask for a first-pass skill file in the format below, then edit it down by hand. The manual review is non-negotiable — the file is the prompt, and prompt quality dominates downstream performance.

📄 See [`src/csa/scales/gg_depression/skills/HOP/SKILL.md`](src/csa/scales/gg_depression/skills/HOP/SKILL.md) for a complete worked example (Hopelessness), and the full set in [`src/csa/scales/gg_depression/skills/`](src/csa/scales/gg_depression/skills/).

### Step 2 — Build a synthetic instance suite

Before you can iterate, you need a ground-truth dataset. Real annotated data is expensive and often unavailable; **synthetic instances with known-by-design codings** let you start immediately and stratify coverage exactly where you need it.

Each instance is a short transcript paired with the codings a perfect rater would produce. Aim for diversity along three axes: (a) *positives* covering every sub-item, perspective, and weight tier of your scale; (b) *distractors* that look superficially similar but should not be coded; (c) *difficulty* — easy textbook cases, moderate naturalistic cases, hard ambiguous cases.

Three sources, used together:
1. **Official documentation and validation papers** — verbatim examples from the scale manual are gold; lift them.
2. **Domain literature** — case reports, clinical interview excerpts, qualitative studies.
3. **LLM-generated synthetic dialogue** — once you have ~10 seed examples per construct, an LLM can extrapolate hundreds more. Always review by hand before committing them as ground truth.
4. **Your own clinical experience** — the most pedagogically valuable distractors usually come from cases that fooled you the first time.

> ⚠️ **Keep the test set independent of the skill files.** Sources 1 and 3 are exactly where independence is lost: an example you lifted into a skill file, or an LLM extrapolating from seed examples it was shown, can reappear as a test clause. Your agent then gets credit for recognising your own authored examples rather than for generalising. We hit this in the published G-G suite — a peer reviewer found that 73 of 345 ground-truth clauses reproduced a skill-file example — and it is the reason this package ships [`synthetic/independence_gate.py`](synthetic/independence_gate.py). Run it over your instance definitions before you evaluate anything:
>
> ```bash
> python synthetic/independence_gate.py --strict   # non-zero exit if any clause reproduces an example
> ```
>
> It rejects a clause that reaches a character sequence ratio of 0.7 with, or shares a five-token phrase with, any quoted example in your skill files. `generate_all.py --strict` enforces the same rule at generation time. Note what the gate does *not* do: it removes verbatim and near-verbatim reuse, not semantic proximity, so a suite authored alongside its own skill files is never fully independent of them. Treat a clean gate as a floor, not a guarantee.

📄 See [`synthetic/instance_defs.py`](synthetic/instance_defs.py) for the 150-instance G-G suite (each instance is a Python dict with `id`, `transcript`, and ground-truth `codings`), and [`synthetic/README.md`](synthetic/README.md) for the suite-design rationale.

### Step 3 — Choose an orchestrator

The orchestrator is whatever turns "skill file + transcript" into "LLM call + parsed output". You have three viable options, in increasing order of complexity:

- **A general-purpose agent harness** — Claude Code, OpenCode, Codex, Continue. Drop your skill files into the agent's tool directory and prompt it to score a transcript. Zero code, fastest to v0.1, but harder to evaluate at scale.
- **A simple Python script** — what this package does. One LLM call per construct, JSON output, deterministic parsing. ~300 lines. Good for production and for the evaluation loop.
- **A multi-stage pipeline** — what we ended up with: a *screening* stage flags candidate constructs cheaply, then a *detail* stage runs the full skill prompt only for flagged constructs. Cuts cost ~10× on long transcripts. Worth building once your v0.1 works.

The only hard requirement is that the orchestrator can load your skill files into the system prompt and return structured (e.g. JSON) output. Everything else is optimisation.

📄 See [`src/csa/agent.py`](src/csa/agent.py) for the two-stage orchestrator, [`src/csa/prompts/`](src/csa/prompts/) for the prompt templates that compose skills + ontology, and [`docs/architecture.md`](docs/architecture.md) for the design rationale.

### Step 4 — Iterate: evaluate → diagnose → revise

This is where the real work happens. Score your synthetic suite, compare predictions to ground truth, find the rows where the agent disagrees, and decide whether the *agent* is wrong (revise the skill file) or the *ground truth* is wrong (revise the instance). Both are common; both are progress.

The evaluation harness in this package is scale-agnostic — it computes hierarchical accuracy (detection → construct → sub-item → perspective → weight), Cohen's κ, weighted κ, Clopper-Pearson confidence intervals, and per-construct precision/recall/F1 against any ground-truth set with the same JSON schema as ours.

```python
from csa.eval import evaluate_run
report = evaluate_run(gt_dir="my_synthetic/", pred_dir="my_run_v0.1/")
print(report)                          # pretty table
report.per_subscale["MY_CONSTRUCT"].f1
```

Expect 5–20 iteration cycles between v0.1 and "good enough to publish" — each cycle adds examples to the skill files, fixes ambiguities in the operational definitions, and occasionally retires synthetic instances that were themselves miscoded. Track skill-file versions (we use `PROMPT_VERSION = "1.0.0"` in `_version.py`) so a published metric always points to a frozen prompt.

📄 See [`src/csa/eval/`](src/csa/eval/) for the metrics and matcher implementations, and [`notebooks/02_synthetic_validation.ipynb`](notebooks/02_synthetic_validation.ipynb) for an end-to-end iteration loop.

### Step 5 — Deploy on real data

Once your synthetic accuracy plateaus and you can articulate *why* the remaining errors happen, you are ready for real transcripts. We strongly recommend two safety nets before publishing clinical conclusions:

1. **Human agreement on a held-out sample** — sample 30–50 fragments from your real corpus, have ≥2 trained raters code them blind to the agent's output, and report agreement at two levels, naming the statistic each time: Cohen's κ between agent and rater consensus on the *screening decision* (does the fragment contain codable content?) and on *whether each subscale is coded in each fragment*, plus ICC(2,1) between the agent's and the consensus's per-fragment weighted sums. A screening κ ≥ 0.6 is a reasonable bar to publish detection claims; do not publish aggregate-score claims until the ICC is at a comparable level. For calibration, our own G-G agent reached κ = 0.66 on the screening decision, κ = 0.41 on subscale presence and ICC(2,1) = 0.21 on weighted sums against a blind three-rater consensus, which is why the paper claims detection and not calibrated scoring.
2. **A negative-control corpus** — run the agent on transcripts that should score zero (small-talk, weather reports, technical interviews). Non-zero scores reveal residual false-positive structure that synthetic distractors missed.

📄 See [`docs/reproduce_paper.md`](docs/reproduce_paper.md) for how we did this with DAIC-WOZ + PHQ-8, and the **Disclaimer** section below for the limits of what any current LLM-based coding agent should be used for.

---

If you build something using this recipe, we would love to hear about it — open an issue or email the corresponding author. We are keeping a list of community ports of the framework for future versions of the paper.

## Disclaimer

⚠️ **This is research software.** It is not a medical device, has not been approved by any regulator, and is not intended for clinical decision-making. See [`DISCLAIMER.md`](DISCLAIMER.md) for the full notice including data-handling and anonymisation guidance.

## Citation

```bibtex
@article{gutierrez2026gg,
  title  = {Translating clinical rating scale ontologies into auditable ambient {LLM} coding agents},
  author = {Guti{\'e}rrez, Enrique and Zhang, Yuhan and Navarro, Jos{\'e}-Blas and Barajas, Ana},
  journal= {npj Digital Medicine},
  year   = {2026},
  note   = {Under revision},
}

@software{csa_2026,
  title  = {{Clinical Skill Architecture}: a framework for translating rating-scale ontologies into {LLM} agents},
  author = {Guti{\'e}rrez, Enrique and Zhang, Yuhan and Navarro, Jos{\'e}-Blas and Barajas, Ana},
  year   = {2026},
  url    = {https://github.com/Kikolo3000/clinical-skill-architecture},
  version= {0.2.0},
  doi    = {10.5281/zenodo.20435438},
  note   = {Concept DOI; resolves to the latest archived version},
}
```

GitHub auto-renders [`CITATION.cff`](CITATION.cff) into a "Cite this repository" button on the sidebar.

## License & acknowledgements

MIT — see [`LICENSE`](LICENSE).

Funded by the authors' institutional allocations at Polytechnic University of Madrid, MIT Linq, and the Autonomous University of Barcelona.

We thank the original Gottschalk-Gleser scale developers (Gottschalk & Gleser, 1969) and our annotators E.L. for human-rater agreement data used in validation.
