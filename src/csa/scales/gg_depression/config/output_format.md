# Output Format — Gottschalk-Gleser Depression Scale

Each intervention (clause/utterance) evaluation produces one JSON object with the
following structure. The subagent MUST write this JSON to the specified output file.

## JSON Structure

```json
{
  "id": "call_001_P1_0023",
  "screening": {
    "decision": "needs_analysis",
    "flagged_subscales": ["HOP", "SAC"],
    "screening_rationale": "Speaker expresses hopelessness about their situation and self-blame for past decisions."
  },
  "codings": [
    {
      "clause": "I just feel like nothing matters anymore",
      "subscale": "HOP",
      "sub_item": "HOP.3b",
      "perspective": "self",
      "weight": 1,
      "rationale": "Direct expression of hopelessness/despair attributed to self"
    },
    {
      "clause": "I'm such a failure",
      "subscale": "SAC",
      "sub_item": "SAC.B.a",
      "perspective": "self",
      "weight": 3,
      "rationale": "Self-depreciation and shame, attributed to self"
    }
  ],
  "subscale_summaries": {
    "HOP": { "count": 1, "weighted_sum": 1, "items_found": ["HOP.3b"] },
    "SAC": { "count": 1, "weighted_sum": 3, "items_found": ["SAC.B.a"] },
    "PMR": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "SOM": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "DAM": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "SEP": { "count": 0, "weighted_sum": 0, "items_found": [] },
    "HOS": { "count": 0, "weighted_sum": 0, "items_found": [] }
  },
  "word_count": 45,
  "scratchpad": {
    "HOP": {
      "sp1": "answer to scratchpad question 1",
      "sp2": "answer to scratchpad question 2"
    },
    "SAC": {
      "sp1": "...",
      "sp2": "..."
    }
  },
  "exclusion_checklist": {
    "HOP": {
      "ec1": "answer to exclusion question 1",
      "ec2": "answer to exclusion question 2"
    },
    "SAC": {
      "ec1": "...",
      "ec2": "..."
    }
  },
  "analyzed_at": "2026-02-19T14:30:00"
}
```

## Field Definitions

### Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique intervention identifier from input.jsonl |
| `screening` | object | yes | Stage 1 screening result |
| `codings` | array | yes | Array of clause-level codings (may be empty) |
| `subscale_summaries` | object | yes | Summary per subscale (all 7 must be present) |
| `word_count` | integer | yes | Total words in the study excerpt |
| `scratchpad` | object | yes | Scratchpad notes for flagged subscales |
| `exclusion_checklist` | object | yes | Exclusion checklist for flagged subscales |
| `analyzed_at` | string | yes | ISO 8601 timestamp |

### `screening` object

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `decision` | string | `"needs_analysis"` or `"no_depressive_content"` | Binary screening outcome |
| `flagged_subscales` | array[string] | Subset of `["HOP","SAC","PMR","SOM","DAM","SEP","HOS"]` | Subscales flagged for Stage 2 |
| `screening_rationale` | string | — | Brief explanation of screening decision |

**Consistency rules:**
- If `decision` = `"no_depressive_content"`, then `flagged_subscales` must be `[]` and `codings` must be `[]`
- If `decision` = `"needs_analysis"`, then `flagged_subscales` must be non-empty

### Each `codings[]` entry

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `clause` | string | — | The exact clause text being coded |
| `subscale` | string | `HOP`, `SAC`, `PMR`, `SOM`, `DAM`, `SEP`, `HOS` | Which subscale this coding belongs to |
| `sub_item` | string | e.g. `HOP.3b`, `SAC.A.a`, `DAM.B.c` | Specific sub-item from the scale |
| `perspective` | string | `"self"`, `"others"`, `"inanimate"`, `"denial"` | Whose experience is described |
| `weight` | integer | 1-4 | Absolute weight (3=self, 2=others, 1=inanimate/denial; 4 for SAC.C suicide items only) |
| `rationale` | string | — | Why this clause was coded under this subscale |

### `subscale_summaries` object

All 7 subscale codes must be present. Each contains:

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Number of clauses coded under this subscale |
| `weighted_sum` | integer | Sum of all weights for this subscale |
| `items_found` | array[string] | List of unique sub-items found |

### `scratchpad` and `exclusion_checklist`

- Keys = subscale codes (only for flagged subscales)
- Values = objects with `sp1`, `sp2`, ... or `ec1`, `ec2`, ... entries
- Empty `{}` when `decision` = `"no_depressive_content"`

## Weight Reference

| Perspective | Weight | When to use |
|-------------|--------|-------------|
| self | 3 | Content about the speaker's own experience |
| others | 2 | Content about other people or animate beings |
| inanimate | 1 | Content about objects, impersonal entities, nature |
| denial | 1 | Denial of depressive content (e.g., "I'm not hopeless") |

**Exception**: SAC.C (Hostility Inward) has items weighted 4 (suicide attempts/wishes).
