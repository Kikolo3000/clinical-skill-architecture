# Model Card — clinical-skill-architecture v0.1.0 (G-G depression scale)

## At a glance

| Field                | Value                                          |
|----------------------|------------------------------------------------|
| Package              | `clinical-skill-architecture` (import as `csa`) |
| Bundled scale        | Gottschalk-Gleser depression (`csa.scales.gg_depression`) |
| Version              | 0.1.0                                          |
| Default model        | `claude-sonnet-4-6` (Anthropic)                 |
| Prompt version       | `1.0.0`                                        |
| Backends supported   | `anthropic`, `openai_compat`                    |
| Pipeline             | Two-stage: screening → per-flagged-subscale detail |
| Validation set       | 150 synthetic instances (own IP)                |
| Real-clinical tested | DAIC-WOZ subset (189 sessions, PHQ-8 ground truth) — see paper |

## Intended use

Score transcripts of speech samples against the 7 subscales of the Gottschalk-Gleser Depression Scale (Gottschalk & Gleser, 1969). Outputs are designed to be:

- **Aggregable** at the session, speaker, or corpus level
- **Auditable** — every clause-level coding ships with a free-text rationale
- **Comparable to human raters** — the output schema is identical to what a trained human annotator would produce

## Default model

The package defaults to `claude-sonnet-4-6` as a lower-cost Anthropic configuration for public use. The paper reports GLM-5 as the primary open-weights configuration and Claude Opus 4.6 as the proprietary upper-bound configuration. Switching models is supported but **invalidates the published metrics**.

| Model               | Backend       | Pipeline cost (per 1k words) | Validated? |
|---------------------|---------------|-------------------------------|------------|
| claude-sonnet-4-6   | anthropic     | ~$0.04 (with prompt caching) | Package default |
| claude-opus-4-6     | anthropic     | ~$0.20                        | Paper proprietary upper bound |
| claude-opus-4-7     | anthropic     | ~$0.20                        | Supported Anthropic configuration |
| claude-haiku-4-5    | anthropic     | ~$0.013                       | ✅ paper supp.    |
| GLM-5               | openai_compat | varies                        | Paper primary open-weights configuration |
| Qwen-3.5            | openai_compat | varies                        | Paper distillation / open-model configuration |
| GPT-5               | openai_compat | ~$0.13                        | ❌ not validated  |

## Validation metrics (from the paper)

Synthetic test suite, 150 instances, Claude Opus 4.6, prompt v1.0.0:

| Metric                                  | Value         |
|-----------------------------------------|----------------|
| Decision accuracy                       | 0.94          |
| Detection sensitivity (clause-level)    | 0.97 (95% CI 0.95–0.99) |
| Detection precision                     | 0.74          |
| Detection F1                            | 0.84          |
| Cohen's κ (binary coded?)               | 0.68          |
| Weighted κ (perspective weight)         | 0.92          |
| Hierarchical: subscale given detection  | 0.96          |
| Hierarchical: sub-item given subscale   | 0.93          |
| Hierarchical: perspective given sub-item| 0.98          |
| Hierarchical: weight given perspective  | 1.00          |

Per-subscale F1 ranges from 0.78 (DAM, lowest) to 0.96 (HOP, highest). See paper Table 2 for full breakdown including confidence intervals.

## Prompt set version

`PROMPT_VERSION = "1.0.0"` is logged in every `ScoringResult` and every per-fragment record. **Bump this constant on any change to:**

- `src/csa/scales/gg_depression/skills/*/SKILL.md`
- `src/csa/prompts/screening.md`
- `src/csa/prompts/detail.md`
- `src/csa/scales/gg_depression/config/depression_domains.md`

The validation table above is only valid for prompt v1.0.0. Any later version requires re-running the synthetic suite to be claimable.

## Out-of-distribution behaviour

- **Languages other than English.** The skills and prompts are English-only. Rough scoring of other languages will work but is unvalidated.
- **Non-clinical speech.** The G-G scale was developed for clinical interviews. Scoring lyrics, social-media posts, or fiction will return values, but interpretation is uncertain.
- **Very short utterances** (< 10 words). Scores become unstable due to the continuity-correction term in the G-G formula. Aggregate before interpreting.
- **Very long single fragments** (> 4000 tokens). The two-stage pipeline expects per-utterance fragments; chunk first.

## Known failure modes

- **HOS over-flagging.** The screening prompt biases toward catching anger; precision on HOS is the lowest of the 7 subscales (~0.65 in synthetic).
- **Denial misses (DENY instances).** When the speaker explicitly denies a symptom ("I don't feel guilty"), the agent occasionally still emits a `denial`-perspective coding instead of suppressing it entirely.
- **Word-count drift.** The agent's reported `word_count` is the model's count of the study excerpt. Falls back to a Python `.split()` count if the model returns garbage.
