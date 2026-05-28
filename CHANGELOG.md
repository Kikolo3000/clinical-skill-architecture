# Changelog

All notable changes to `clinical-skill-architecture` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Frozen verbatim copy of the paper pipeline at `extras/paper_reproduction/`
- 34-test suite covering fragmenter, scorer, validator, eval metrics, agent smoke
