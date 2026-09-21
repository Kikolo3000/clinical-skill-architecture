# Model Card — clinical-skill-architecture v0.2.0 (G-G depression scale)

## At a glance

| Field                | Value                                          |
|----------------------|------------------------------------------------|
| Package              | `clinical-skill-architecture` (import as `csa`) |
| Bundled scale        | Gottschalk-Gleser depression (`csa.scales.gg_depression`) |
| Version              | 0.2.0                                          |
| Package default model | `claude-sonnet-4-6` (Anthropic) — convenience default, **not** the validated configuration |
| Paper primary configuration | `zai/GLM-5` via `openai_compat` (open weights) |
| Paper proprietary comparison | Claude Opus 4.6 (synthetic suite only) |
| Prompt version       | `1.0.0`                                        |
| Backends supported   | `anthropic`, `openai_compat`                    |
| Pipeline             | Two-stage: screening → per-flagged-subscale detail |
| Validation           | Three arms: synthetic suite (150 instances; 90 after de-overlap), blind expert annotation (48 DAIC-WOZ fragments, 3 raters), construct validity vs PHQ-8 (189 DAIC-WOZ sessions) |

## Intended use

Research software for retrospective coding of speech transcripts against the seven subscales of
the Gottschalk-Gleser Depression Scale (Gottschalk & Gleser, 1969). Outputs are clause-level
codings with sub-item, perspective, weight and a free-text rationale, aggregable to fragment,
session or corpus level. The output schema is the one a trained human annotator would produce,
so it can be compared with human coding directly.

It is **not** clinical decision support and has not been evaluated as a medical device. See
`DISCLAIMER.md` for the preconditions the paper states for any clinical use.

## Models

The package defaults to `claude-sonnet-4-6` because it is the simplest first run (one key, prompt
caching). The paper's primary configuration is the open-weights GLM-5, chosen so that clinical
speech can be processed on institutional infrastructure. Switching models changes the output
distribution; the figures below apply only to the model named in each row.

| Model               | Backend        | Status |
|---------------------|----------------|--------|
| `zai/GLM-5`         | `openai_compat`| **Paper primary configuration** (all DAIC-WOZ results; synthetic suite) |
| `claude-opus-4-6`   | `anthropic` / CLI | Paper proprietary comparison on the synthetic suite |
| `claude-sonnet-4-6` | `anthropic` / CLI | Synthetic suite and context-window experiment (supplementary); package default |
| `claude-haiku-4-5`  | `anthropic` / CLI | Synthetic suite (supplementary) |
| Qwen3.5-2B, Nanbeige4.1-3B (fine-tuned students) | local | Distillation experiment (supplementary); not recommended for use |
| anything else       | either         | Not validated |

## Validation figures (from the paper; prompt v1.0.0)

**Synthetic suite** (clause-level detection against known ground truth; v1.1 = the 90
instances that pass the skill-file independence gate, v1.0 = all 150):

| Metric                              | GLM-5 v1.1 | GLM-5 v1.0 | Opus 4.6 v1.1 | Opus 4.6 v1.0 |
|-------------------------------------|-----------:|-----------:|--------------:|--------------:|
| Detection sensitivity               | 0.644      | 0.609      | 0.960         | 0.971         |
| Detection precision                 | 0.655      | 0.648      | 0.702         | 0.740         |
| Detection F1                        | **0.650**  | 0.628      | **0.811**     | 0.840         |
| Subscale correct, given detection   | 72.8%      | 76.7%      | 94.1%         | 96.4%         |
| Sub-item correct, given subscale    | 90.4%      | 93.2%      | 90.0%         | 92.9%         |
| Perspective correct, given sub-item | 98.7%      | 97.3%      | 98.6%         | 98.3%         |
| Weight correct, given perspective   | 100%       | 100%       | 100%          | 100%          |
| Overall decision accuracy (150)     | —          | 95.3%      | —             | 92.0%         |

Per-subscale F1 (v1.0, Opus 4.6) ranges from 0.733 (DAM) to 0.923 (PMR); for GLM-5 from 0.456
(SEP) to 0.687 (SOM). Sonnet 4.6 and Haiku 4.5 reach F1 0.824 and 0.832 on v1.0.

**Expert arm** (GLM-5; 48 DAIC-WOZ fragments; blind three-rater majority consensus;
fragment-level screening):

| Metric | Full architecture | Zero-shot baseline (same model) |
|---|---|---|
| Sensitivity | 0.920 | 0.680 |
| Specificity | 0.739 | 0.826 |
| F1 | 0.852 | 0.739 |
| Weighted-sum ICC(2,1) vs consensus | 0.211 | 0.533 |
| Cohen's κ, subscale coded in fragment (336 items) | 0.41 | 0.41 |
| Cohen's κ, screening decision | 0.66 | 0.50 |

The full architecture detects more consensus-positive fragments than the baseline (2 vs 8 of 25
missed; a directional result, McNemar p = 0.29 at n = 48) but over-codes within flagged
subscales, which inflates its weighted sums (bias +5.1 points per fragment). Per-subscale
precision against the consensus is low for HOP (0.16), SAC (0.19) and SEP (0.13); for HOP and
SEP this is system error, not rater instability.

**Construct validity** (GLM-5; 189 sessions; PHQ-8 self-report): Pearson r = 0.492, Spearman
ρ = 0.475, AUC = 0.702; at the in-sample Youden cut-point sensitivity 0.554 and specificity
0.805 (leave-one-out: 0.536 / 0.805). Sex-stratified: r = 0.55 (women, n = 87) vs 0.44 (men,
n = 102), AUC 0.69 vs 0.72; the difference is not significant.

## Prompt set version

`PROMPT_VERSION = "1.0.0"` is logged in every `ScoringResult` and per-fragment record. Bump it
on any change to the skill files, `screening.md`, `detail.md` or `depression_domains.md`. The
figures above are valid for prompt v1.0.0 with the model named in each row only.

## Out-of-distribution behaviour

- **Languages other than English.** Skills and prompts are English-only; other languages are unvalidated.
- **Non-clinical speech.** The G-G scale was developed for clinical interviews; scores on other text are of uncertain meaning.
- **Very short utterances** (< 10 words). Scores are unstable because of the continuity-correction term; aggregate before interpreting.
- **Very long single fragments** (> 4,000 tokens). The pipeline expects per-utterance fragments; chunk first.
- **Populations and settings beyond DAIC-WOZ.** Validation used one English corpus of semi-structured interviews with a virtual interviewer; local validation is required elsewhere.

## Known failure modes

- **Over-coding within flagged subscales.** Stage 2 rarely prunes what Stage 1 flags and often emits several codings per subscale; aggregate weighted sums are therefore inflated relative to human coders (see Expert arm). Capping to one coding per fragment–subscale halves the bias.
- **HOP, SAC, SEP false positives.** Precision against expert consensus is 0.13–0.19 on these subscales. A Hopelessness flag is a prompt for review, not a risk indicator.
- **Denial handling.** When a symptom is explicitly denied, the agent occasionally emits a `denial`-perspective coding instead of none.
- **Word-count drift.** The reported `word_count` is the model's; the package falls back to a Python count when it is malformed.
