# Disclaimer

## Not for clinical use

`clinical-skill-architecture` (and the bundled `gg_depression` scale) is **research software** distributed under the MIT license. It is **not a medical device**, has **not** been reviewed by the FDA, EMA, MHRA, or any other regulator, and **must not** be used for:

- Primary diagnostic decisions
- Patient triage or treatment planning without professional oversight
- Deployment in clinical settings without appropriate regulatory review
- Any task where an incorrect output could harm a patient

It is intended for:

- Academic and methodological research
- Clinician-assisted secondary scoring (with a human always in the loop)
- Reproducing the validation reported in the npj Digital Medicine paper
- Teaching and training purposes

## Performance caveats

The validation metrics reported in the paper and `MODEL_CARD.md` were measured on a synthetic test suite of 150 hand-crafted instances. Performance on real clinical interviews varies and **should be re-validated for any new corpus or population** before drawing conclusions.

The agent's calibration depends on:

- The **default model** (`claude-sonnet-4-6`). Switching models invalidates the validation numbers.
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
