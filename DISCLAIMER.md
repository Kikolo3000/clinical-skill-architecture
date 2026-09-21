# Disclaimer

## Not for clinical use

`clinical-skill-architecture` (and the bundled `gg_depression` scale) is **research software** for retrospective coding of transcripts, distributed under the MIT license. It is **not clinical decision support**, it is **not a medical device**, and it has **not** been reviewed by the FDA, EMA, MHRA, or any other regulator. It **must not** be used for:

- Primary diagnostic decisions
- Patient triage or treatment planning without professional oversight
- Deployment in clinical settings without local validation and appropriate regulatory review
- Any task where an incorrect output could harm a patient

It is intended for:

- Academic and methodological research
- Reproducing the validation reported in the npj Digital Medicine paper
- Teaching and training purposes
- Clinician-assisted secondary scoring only under the preconditions below

## Preconditions for any clinical use

The paper states these as conditions, not recommendations. Any use in patient care presupposes:

1. **Clinician review of every flag** before it informs any decision. The agent attaches clinical names to patient speech; that is an interpretive act that a professional must own.
2. **An abstention pathway.** Low-confidence codings are withheld or marked as uncertain rather than shown as findings. Agreement across repeated runs (vote fraction) is one implementable signal; in the paper it removed a quarter of the codings at no sensitivity cost.
3. **Uncertainty display.** Every coding is shown with its confidence, the clause it rests on, the surrounding utterances and its rationale, so that it can be contested.
4. **Informed patient consent** to the analysis of their speech, with a plain statement of what the system does and does not do.
5. **Local validation** on the deploying site's own population, language and interview format before use, with results reported by sex.
6. **An override and correction trail** that propagates to every downstream summary, so that a corrected coding never survives in an aggregate score.
7. **Regulatory assessment** appropriate to the jurisdiction and the intended use.

**Hopelessness (HOP) flags must never enter a suicide-risk workflow without human review.** Against expert consensus the agent's HOP precision was 0.16 and its false positives were not explained by rater disagreement.

## Performance caveats

The validation figures in the paper and `MODEL_CARD.md` come from three arms: a synthetic suite of 150 hand-crafted instances (90 after removing instances that reproduce skill-file examples), a blind three-rater annotation of 48 DAIC-WOZ fragments, and PHQ-8 self-report on 189 DAIC-WOZ sessions. They show good fragment-level detection and **poor calibration of aggregate weighted scores** (ICC 0.21 against expert consensus). Performance on any other corpus, language or population **must be re-validated** before drawing conclusions.

The figures apply only to the configurations named in `MODEL_CARD.md`:

- The **paper's primary model is GLM-5** via `openai_compat`; the **package default** (`claude-sonnet-4-6`) is a convenience for a first run and carries no validated figures of its own. Switching models changes the output distribution.
- The **default prompt set version** (`PROMPT_VERSION = "1.0.0"`). Editing prompts, skills, or the ontology invalidates the validation numbers.
- The default **two-stage screening + detail** pipeline. Single-stage variants will produce different distributions.

## Data handling and anonymisation

Calling the Anthropic API or any third-party LLM provider sends your transcript text to that provider's servers. You are responsible for:

- Stripping or pseudonymising direct identifiers (names, dates, locations) **before** scoring
- Confirming with your IRB / DPA that LLM-based scoring is permitted for your data
- Reading your provider's data retention and training-data policies; configure zero-data-retention agreements where required

This package does **not** automatically de-identify input. Treat scoring like sending the same text to any external API.

## Limitations specific to LLM-based scoring

- **Hallucinated codings.** The agent may invent clauses or assign weights that look plausible but were not in the input. The hierarchical accuracy decomposition (`evaluate_run().hierarchical`) is designed to surface this; spot-check rationales for any clinically consequential decision.
- **Drift.** Frontier model versions change without notice. Re-run `tests/test_snapshot.py` after any model upgrade to detect behavioural drift.
- **Bias.** LLMs encode biases from their training data. The G-G scale itself was developed in a primarily English-speaking, North American clinical population. Validation outside that distribution is the user's responsibility.

## No warranty

This software is provided "as is", without warranty of any kind, express or implied. See `LICENSE` for the full text.
