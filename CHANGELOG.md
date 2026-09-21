# Changelog

All notable changes to `clinical-skill-architecture` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-09-21

Revision release accompanying the revised npj Digital Medicine manuscript. No change to the
skill files, prompts or pipeline logic (prompt version stays 1.0.0); the release corrects the
documentation and adds the suite-independence tooling.

### Fixed

- `docs/reproduce_paper.md`, `README.md`, `MODEL_CARD.md`: the synthetic figures F1 0.840 /
  sensitivity 0.971 were attributed to Claude Sonnet 4.6; they were produced by Claude Opus 4.6
  (Sonnet 4.6: F1 0.824). Removed figures that correspond to no result file (decision accuracy
  0.94, weighted κ 0.92, Cohen's κ 0.68, Spearman ρ ≈ 0.41, an "Opus 4.7" run). Table numbers
  now match the revised manuscript's table titles rather than an earlier draft.
- `docs/reproduce_paper.md`: GLM-5 through `openai_compat` documented as the paper's primary
  configuration and primary reproduction route; the Claude runs are documented as CLI runs.
- `extras/paper_reproduction/README.md`: the scripts are adapted copies, not verbatim copies.
- `README.md` Step 5: the human-agreement guidance names the statistic and level of analysis
  (screening κ, subscale-presence κ, weighted-sum ICC) instead of an unqualified "κ ≥ 0.6".
- `DISCLAIMER.md`: aligned with the manuscript's classification (research software; not
  clinical decision support; not a medical device) and its seven preconditions for clinical use.
- `config/output_format.md` example: HOP coding weight 3 → 1 (HOP is a flat-weight subscale;
  no output was affected).
- Suite v1.0 figures for GLM-5 restated from the current evaluator (F1 0.629, precision 0.650,
  one false-positive coding fewer than the artefact archived in March 2026); Claude Opus 4.6 is
  unchanged.

### Added

- README: the "Adapting the framework to your own scale" recipe now warns that lifting examples
  into skill files and extrapolating from seed examples are where test-set independence is lost,
  and points at the gate; the citation block carries the revised article title.
- `synthetic/independence_gate.py`: skill-file independence gate (sequence ratio ≥ 0.7 or shared
  five-token phrase) and `synthetic/suite_v11.json`, the 90-instance de-overlapped suite v1.1;
  `generate_all.py --strict` refuses instances that fail the gate.
- `csa.eval.evaluate_run(..., instance_ids=...)` to evaluate on a subset such as v1.1.
- Expert-arm and construct-validity figures, with their reference standards and the
  calibration limit (weighted-sum ICC 0.21), in `MODEL_CARD.md` and `README.md`.

## [0.1.0] — 2026-04-23

Initial public release accompanying the npj Digital Medicine submission.

### Added

- `score()` and `score_async()` module-level functions and `GGAgent` class
- Anthropic backend with prompt caching enabled by default
- OpenAI-compatible backend (Requesty.ai, OpenRouter, vLLM, Ollama)
- 7 subscale skills (HOP, SAC, PMR, SOM, DAM, SEP, HOS) loaded via `importlib.resources`
- Two-stage screening + per-subscale detail pipeline
- `csa-score` console script
- `csa.eval` evaluation harness with hierarchical accuracy, Clopper-Pearson CIs, Cohen's and weighted kappa
- 3 demo synthetic instances bundled inside the wheel
- Full 150-instance synthetic suite generator at `synthetic/`
- Copy of the paper pipeline scripts at `extras/paper_reproduction/`
- 34-test suite covering fragmenter, scorer, validator, eval metrics, agent smoke
