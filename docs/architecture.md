# Architecture

A 1-page tour of how `clinical-skill-architecture` (with the bundled G-G depression scale) turns a transcript into 7 subscale scores.

## Overview

```
                         ┌─────────────────────────────┐
   transcript text  ───▶ │   fragmenter.fragment()     │ ──▶ list[Fragment]
   (multi-turn or        │   (auto-detect speakers,    │
    free-form)           │    bundle close_context)    │
                         └─────────────────────────────┘
                                     │
                                     ▼
                  ┌──────────────────────────────────────┐
                  │         GGAgent.score_async()         │
                  │                                       │
                  │   for each Fragment (concurrent):     │
                  │                                       │
                  │   ┌─────────────────────────────┐    │
                  │   │ Stage 1: SCREENING          │    │
                  │   │ system = ontology + rules   │    │
                  │   │ user   = excerpt + context  │    │
                  │   │ → {decision, flagged_subs}  │    │
                  │   └────────────┬────────────────┘    │
                  │                │                      │
                  │      decision == "needs_analysis"?    │
                  │                │ yes                  │
                  │                ▼                      │
                  │   ┌─────────────────────────────┐    │
                  │   │ Stage 2: DETAIL × N         │    │
                  │   │ (one call per flagged       │    │
                  │   │  subscale, concurrent)      │    │
                  │   │ system = SKILL.md + rules   │    │
                  │   │ user   = excerpt + screen.  │    │
                  │   │ → list[Coding]              │    │
                  │   └────────────┬────────────────┘    │
                  │                │                      │
                  │                ▼                      │
                  │           FragmentResult              │
                  └──────────────────┬────────────────────┘
                                     │
                                     ▼
                         ┌─────────────────────────────┐
                         │     scorer.aggregate()      │ ──▶ ScoringResult
                         │  (apply G-G formula per     │     (7 subscales +
                         │   subscale, sum total)      │      total)
                         └─────────────────────────────┘
```

## The two stages

**Stage 1 — Screening.** One LLM call per fragment. The system prompt contains the full G-G ontology (`config/depression_domains.md`) and a "liberal flagging mandate" — when in doubt, flag it. Output is a JSON object with `decision`, `flagged_subscales`, `screening_rationale`, and `word_count`.

**Stage 2 — Detail.** For every subscale flagged in Stage 1, a separate LLM call. The system prompt now contains that subscale's `SKILL.md` instead of the full ontology; the user prompt re-includes the excerpt plus the screening rationale. Output is a JSON object with a `codings` array (clause, sub-item, perspective, weight, rationale).

If Stage 1 returns `no_depressive_content`, Stage 2 is skipped entirely. Empirically ~30-50% of fragments take this fast path on real clinical transcripts.

## Why two stages

A single-prompt approach would have to stuff every subscale's `SKILL.md` into one system prompt — about 40 KB of text. That would (a) blow up context, (b) prevent the agent from doing focused per-subscale work, (c) lose the clean per-subscale rationales we need for human audit.

The two-stage design also lets us cache the Stage-1 system prompt (10 KB ontology) across every fragment of a session, turning the inner loop into a small per-call delta — a 5-10× cost reduction on the Anthropic backend.

## Concurrency

Within one transcript, `GGAgent` uses `asyncio.gather()` over all fragments and over all flagged subscales for each fragment. The `max_concurrent` semaphore (default 5) caps total in-flight calls to keep within provider rate limits.

For batches of transcripts, instantiate one `GGAgent` and call `score_async()` in your own outer `asyncio.gather()`.

## Schema

Every fragment's result is a `FragmentResult`:

```python
FragmentResult(
    fragment=Fragment(id, line_number, speaker, study_excerpt, close_context),
    screening=Screening(decision, flagged_subscales, rationale),
    codings=(Coding(clause, subscale, sub_item, perspective, weight, rationale), ...),
    word_count=int,
    analyzed_at=str,           # ISO 8601
    prompt_version=str,        # "1.0.0"
    input_tokens=int,
    output_tokens=int,
    cached_tokens=int,
)
```

Aggregating one or more `FragmentResult`s yields a `ScoringResult`:

```python
ScoringResult(
    fragments=(...),
    subscales={"HOP": SubscaleScore(...), "SAC": ..., ...},   # all 7 always present
    total_depression=float,                                    # sum of 7 scores
    word_count=int,
    model=str,
    prompt_version=str,
    estimated_cost_usd=float,
)
```

See [`docs/output_schema.md`](output_schema.md) for the JSON dump format.

## Backend protocol

```python
class Backend(Protocol):
    name: str
    async def complete(
        self, *, system: str, user: str, model: str, cache_system: bool = True
    ) -> BackendResponse: ...
```

`BackendResponse` returns `text`, `input_tokens`, `output_tokens`, `cached_tokens`. Backends decide internally how to enable JSON mode, retries, prompt caching. The agent expects valid JSON in `text` (with permissive extraction for fenced code blocks and mixed prose).

Implementing a new backend = implement `complete()` and register it in `backends/__init__.py:get_backend()`. See `backends/openai_compat.py` for a 60-line reference implementation.

## What we deliberately don't do

- **No fine-tuning.** The whole point is that a frontier instruction-following model with the right prompts is enough.
- **No embedding retrieval.** Each fragment is scored in isolation; the only "memory" is the close_context (preceding turns) bundled at fragmentation time.
- **No batch / cross-instance prompts.** Cross-instance batching was studied in the paper (synthetic only) and rejected: small accuracy drop, not worth the orchestration complexity.
- **No client-side de-identification.** That's the user's responsibility — see `DISCLAIMER.md`.
