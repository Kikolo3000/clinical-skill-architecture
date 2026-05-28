# Output Schema

JSON shape of `ScoringResult.to_dict()`. All fields are non-optional unless noted.

## Top-level

```json
{
  "model": "claude-sonnet-4-6",
  "prompt_version": "1.0.0",
  "word_count": 26,
  "total_depression": 5.42,
  "estimated_cost_usd": 0.0021,
  "subscales": { /* 7 entries — see below */ },
  "fragments": [ /* one entry per scored utterance — see below */ ]
}
```

## `subscales[<code>]`

```json
{
  "HOP": {
    "subscale": "HOP",
    "name": "Hopelessness",
    "score": 3.10,
    "count": 2,
    "weighted_sum": 2,
    "word_count": 26,
    "items_found": ["HOP.3b"]
  }
}
```

The `score` is `sqrt((weighted_sum + 0.5) * 100 / word_count)`. All 7 subscales are always present; un-flagged ones have `count=0` and the continuity-correction-only score `sqrt(0.5 * 100 / word_count)`.

## `fragments[i]`

```json
{
  "id": "frag_0001",
  "screening": {
    "decision": "needs_analysis",
    "flagged_subscales": ["HOP"],
    "screening_rationale": "Two clear hopelessness clauses."
  },
  "codings": [
    {
      "clause": "i just don't see the point anymore",
      "subscale": "HOP",
      "sub_item": "HOP.3b",
      "perspective": "self",
      "weight": 1,
      "rationale": "Direct expression of futility/hopelessness attributed to self"
    }
  ],
  "subscale_summaries": {
    "HOP": { "count": 1, "weighted_sum": 1, "items_found": ["HOP.3b"] },
    "SAC": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "PMR": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "SOM": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "DAM": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "SEP": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "HOS": { "count": 0, "weighted_sum": 0, "items_found": [] }
  },
  "word_count": 26,
  "analyzed_at": "2026-04-23T22:14:11+00:00",
  "prompt_version": "1.0.0",
  "tokens": {
    "input": 612,
    "output": 142,
    "cached": 580
  }
}
```

## Field reference

| Field                              | Type        | Notes                                                                           |
|-------------------------------------|-------------|---------------------------------------------------------------------------------|
| `screening.decision`                | enum        | `"no_depressive_content"` \| `"needs_analysis"`                                  |
| `screening.flagged_subscales`       | list[str]   | Subset of `["HOP","SAC","PMR","SOM","DAM","SEP","HOS"]`. Empty iff decision is `"no_depressive_content"`. |
| `screening.screening_rationale`     | str         | Short free-text explanation, model-generated.                                    |
| `codings[i].clause`                 | str         | Verbatim quote from `study_excerpt`.                                             |
| `codings[i].subscale`               | enum        | One of the 7 subscale codes.                                                     |
| `codings[i].sub_item`               | str         | E.g. `"HOP.3b"`, `"SAC.A.a"`. See `config/depression_domains.md` for full list.  |
| `codings[i].perspective`            | enum        | `"self"` \| `"others"` \| `"inanimate"` \| `"denial"`                            |
| `codings[i].weight`                 | int         | 1–4. HOP/PMR/SOM are flat 1; SAC.C suicide items can reach 4.                    |
| `codings[i].rationale`              | str         | Per-clause justification, model-generated.                                       |
| `subscale_summaries[<code>].count`  | int         | Number of codings under this subscale.                                           |
| `subscale_summaries[<code>].weighted_sum` | int   | Sum of `weight` over those codings.                                              |
| `subscale_summaries[<code>].items_found` | list[str] | Distinct sub-items observed.                                                     |
| `word_count`                        | int         | Word count of the `study_excerpt` (model-reported, falls back to `.split()`).    |
| `analyzed_at`                       | str         | ISO 8601 UTC timestamp.                                                          |
| `prompt_version`                    | str         | Bumped on any change to skills, prompts, or ontology. See `MODEL_CARD.md`.       |
| `tokens.input` / `output` / `cached`| int         | From the backend's usage report. Used for cost estimation.                        |

## Stable across versions?

The schema is **stable for the 0.x series**. Any field rename or removal will be a major-version bump (1.0.0+).
