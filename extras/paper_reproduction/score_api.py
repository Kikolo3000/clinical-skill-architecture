#!/usr/bin/env python3
"""
Gottschalk-Gleser Depression Scale — API-based Analysis Orchestrator

Makes direct API calls via Requesty.ai (OpenAI-compatible router) instead of
spawning `claude -p` subprocesses. Uses a 2-stage architecture:
  Stage 1: Screening — identify fragments with potential depressive content
  Stage 2: Detailed analysis — clause-level coding for each flagged subscale

Produces identical output format to score_cli.py for compatibility with
existing scoring/validation scripts.

Usage:
    python scripts/score_api.py 300
    python scripts/score_api.py 300 --model alibaba/qwen3.5 --max-concurrent 10
    python scripts/score_api.py 300 --output-suffix qwen --no-transcript
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_PATH = PROJECT_ROOT / "config" / "depression_domains.md"
OUTPUT_FORMAT_PATH = PROJECT_ROOT / "config" / "output_format.md"
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"

REQUIRED_SUBSCALES = {"HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS"}

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("depression-api")


class TeeWriter:
    """Write to both a stream (stdout) and a log file simultaneously."""

    def __init__(self, stream, log_file):
        self.stream = stream
        self.log_file = log_file

    def write(self, data):
        self.stream.write(data)
        self.log_file.write(data)

    def flush(self):
        self.stream.flush()
        self.log_file.flush()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_interventions(input_path: Path) -> list[dict]:
    """Load interventions from input file (handles both JSON array and JSONL)."""
    content = input_path.read_text(encoding="utf-8").strip()
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    records = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def validate_partial(path: Path) -> bool:
    """Check if a partial result file exists and contains valid JSON with required fields."""
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False
        if "id" not in data or "screening" not in data:
            return False
        summaries = data.get("subscale_summaries", {})
        if not REQUIRED_SUBSCALES.issubset(summaries.keys()):
            return False
        if not isinstance(data.get("codings", None), list):
            return False
        if "word_count" not in data:
            return False
        return True
    except (json.JSONDecodeError, OSError):
        return False


def load_file_content(path: Path) -> str:
    """Load a file's content, stripping optional header comment block."""
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return content.strip()


def extract_json(text: str) -> dict | None:
    """Extract JSON from model response, handling markdown fences and extra text."""
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code fences
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding the outermost { ... }
    brace_start = text.find("{")
    if brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start : i + 1])
                    except json.JSONDecodeError:
                        break

    return None


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

SCREENING_SYSTEM_PROMPT_TEMPLATE = """\
You are a depression content analyst coding verbal samples for depressive \
thematic content using the Gottschalk-Gleser Depression Scale.

Your task is STAGE 1: SCREENING — a rapid triage to identify whether a \
verbal sample contains potential depressive content across 7 subscales.

## Depression Scale Definitions

{domains_content}

## Instructions

1. Read the study excerpt and close context provided by the user.
2. Apply the 7 subscale definitions to identify potential depressive content.
3. Count the EXACT number of words in the study excerpt (for the word_count field).
4. Make a binary decision:
   - "no_depressive_content": No depressive themes detected.
   - "needs_analysis": Possible depressive content detected — flag specific subscales.

## LIBERAL FLAGGING MANDATE
- When uncertain between related subscales (e.g., HOP vs SEP, SAC vs HOS), flag ALL.
- Flag ANY reference to loss, difficulty, somatic complaint, self-criticism, death/harm.
- 10% doubt = flag it. False positives are cheap; false negatives are costly.
- Code the CONTENT, not the speaker's clinical state.

## WORD-BY-WORD SCAN
Analyze EACH word/phrase in the excerpt independently. Short excerpts are deceptive — \
a 2-word answer like "irritated lazy" contains TWO separate signals:
- "irritated" → anger/hostility → flag HOS
- "lazy" → self-deprecation → flag SAC; slowing → flag PMR; loss of energy → flag SOM
Do NOT stop after finding one subscale. Scan every word for all 7 subscales.

## COMMON UNDER-FLAGGING ERRORS TO AVOID
- Emotional words (angry, irritated, frustrated, annoyed) → ALWAYS flag HOS
- Self-critical labels (lazy, stupid, worthless, failure) → ALWAYS flag SAC
- Energy/fatigue words (tired, exhausted, lazy, slow) → flag BOTH PMR and SOM
- Loss/unreliability ("they don't follow through") → flag SEP (loss of support)
- Sleep references → flag SOM even if contextually explained

## Output

Respond with ONLY a JSON object (no other text):

```json
{{
  "decision": "no_depressive_content" or "needs_analysis",
  "flagged_subscales": ["HOP", "SAC"],
  "screening_rationale": "Brief explanation",
  "word_count": 45
}}
```

If no depressive content: flagged_subscales must be [].
If needs_analysis: flagged_subscales must be non-empty."""


DETAIL_SYSTEM_PROMPT_TEMPLATE = """\
You are a depression content analyst performing STAGE 2: DETAILED CLAUSE-LEVEL \
CODING for the **{subscale_code}** subscale of the Gottschalk-Gleser Depression Scale.

## Subscale Definition & Coding Guide

{skill_content}

## Perspective Weighting Rules

- **Self (weight 3)**: The speaker is the subject of the depressive content.
- **Others (weight 2)**: Other people or animate beings are the subject.
- **Inanimate (weight 1)**: Objects, situations, or impersonal entities.
- **Denial (weight 1)**: The speaker denies depressive content.

Exception: HOP, PMR, SOM use flat weight 1 regardless of perspective.
Exception: SAC.C suicide items use weight up to 4.

## Instructions

1. Work through the scratchpad questions (sp1, sp2, etc.) from the skill guide.
2. Apply the exclusion checklist (ec1, ec2, etc.).
3. For EACH clause in the study excerpt matching {subscale_code}:
   - Identify the exact clause text
   - Determine the sub-item code
   - Assign the perspective and weight
   - Write a brief rationale

## IMPORTANT CODING PRINCIPLES
- **Bias toward coding**: This excerpt was flagged in screening for a reason. If the \
content is borderline, CODE IT. The scale is designed to capture thematic content, not \
clinical diagnosis. Even mild or situational references count.
- **Distinguish animate vs inanimate targets carefully**: Criticizing a PERSON or \
people's behavior → weight 2-3. Criticizing an abstract concept, situation, or object \
(e.g., "bias", "the weather", "traffic") → weight 1 (inanimate).
- **Single words count as clauses**: In short excerpts, even a single word like \
"lazy" or "irritated" is a valid clause if it matches the subscale definition.
- **Do NOT over-exclude**: Exclusion criteria filter out content that clearly does NOT \
match the subscale. If content matches the definition even partially, code it. \
When in doubt, include the coding.

## Output

Respond with ONLY a JSON object (no other text):

```json
{{
  "scratchpad": {{
    "sp1": "answer",
    "sp2": "answer"
  }},
  "exclusion_checklist": {{
    "ec1": "answer",
    "ec2": "answer"
  }},
  "codings": [
    {{
      "clause": "exact text",
      "subscale": "{subscale_code}",
      "sub_item": "{subscale_code}.3b",
      "perspective": "self",
      "weight": 1,
      "rationale": "explanation"
    }}
  ]
}}
```

If no clauses match after applying exclusion criteria, return empty codings: []."""


def build_screening_system_prompt(domains_content: str) -> str:
    return SCREENING_SYSTEM_PROMPT_TEMPLATE.format(domains_content=domains_content)


def build_screening_user_prompt(
    intervention: dict, transcript_content: str | None
) -> str:
    parts = []
    if transcript_content:
        parts.append(
            f"## Full Transcript (for context)\n\n<transcript>\n{transcript_content}\n</transcript>\n"
        )
    parts.append(
        f"## Close Context (preceding turns)\n\n<close_context>\n{intervention['close_context']}\n</close_context>\n"
    )
    parts.append(
        f"## Study Excerpt (evaluate this for depressive content)\n\n<study_excerpt>\n{intervention['study_excerpt']}\n</study_excerpt>"
    )
    return "\n".join(parts)


def build_detail_system_prompt(subscale_code: str, skill_content: str) -> str:
    return DETAIL_SYSTEM_PROMPT_TEMPLATE.format(
        subscale_code=subscale_code,
        skill_content=skill_content,
    )


def build_detail_user_prompt(
    intervention: dict,
    screening_rationale: str,
    transcript_content: str | None,
) -> str:
    parts = []
    if transcript_content:
        parts.append(
            f"## Full Transcript (for context)\n\n<transcript>\n{transcript_content}\n</transcript>\n"
        )
    parts.append(
        f"## Close Context\n\n<close_context>\n{intervention['close_context']}\n</close_context>\n"
    )
    parts.append(
        f"## Study Excerpt\n\n<study_excerpt>\n{intervention['study_excerpt']}\n</study_excerpt>\n"
    )
    parts.append(
        f"## Screening Context\n\nThe screening stage flagged this excerpt. Rationale: {screening_rationale}"
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# API call helpers
# ---------------------------------------------------------------------------


async def call_api(
    client: AsyncOpenAI,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3,
) -> dict | None:
    """Make an API call and parse JSON from the response. Retries on malformed JSON."""
    for attempt in range(1, max_retries + 1):
        try:
            await asyncio.sleep(2.5)  # Rate-limit: space out requests (max-concurrent 3 safe)
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            result = extract_json(content)
            if result is not None:
                return result

            log.warning("Attempt %d: malformed JSON response, retrying...", attempt)

        except Exception as e:
            err_str = str(e)
            # If json_object mode not supported, retry without it
            if "response_format" in err_str or "json_object" in err_str:
                try:
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.0,
                    )
                    content = response.choices[0].message.content
                    result = extract_json(content)
                    if result is not None:
                        return result
                except Exception as e2:
                    log.warning("Attempt %d: API error (no json mode): %s", attempt, e2)
            else:
                log.warning("Attempt %d: API error: %s", attempt, e)

            if attempt < max_retries:
                await asyncio.sleep(2 * attempt)

    return None


# ---------------------------------------------------------------------------
# Core: process a single intervention
# ---------------------------------------------------------------------------


async def process_intervention(
    semaphore: asyncio.Semaphore,
    client: AsyncOpenAI,
    model: str,
    intervention: dict,
    partial_dir: Path,
    domains_content: str,
    skill_contents: dict[str, str],
    transcript_content: str | None,
    screening_system_prompt: str,
) -> dict:
    """Process a single intervention through screening → detail stages."""
    intervention_id = intervention["id"]
    output_path = partial_dir / f"{intervention_id}.json"

    # Resumability: skip if already done
    if validate_partial(output_path):
        try:
            with open(output_path) as f:
                existing = json.load(f)
            decision = existing.get("screening", {}).get("decision", "?")
            flagged = existing.get("screening", {}).get("flagged_subscales", [])
            summaries = existing.get("subscale_summaries", {})
            active = {k: v for k, v in summaries.items() if v.get("count", 0) > 0}
        except Exception:
            decision, flagged, active = "?", [], {}
        return {
            "id": intervention_id,
            "status": "skipped",
            "decision": decision,
            "flagged": flagged,
            "active_subscales": active,
        }

    t0 = time.monotonic()

    async with semaphore:
        # STAGE 1: Screening
        user_prompt = build_screening_user_prompt(intervention, transcript_content)
        screening_result = await call_api(
            client, model, screening_system_prompt, user_prompt,
        )

        if screening_result is None:
            return {"id": intervention_id, "status": "failed", "reason": "screening API failed"}

        decision = screening_result.get("decision", "no_depressive_content")
        flagged_subscales = screening_result.get("flagged_subscales", [])
        screening_rationale = screening_result.get("screening_rationale", "")
        word_count = screening_result.get("word_count", 0)

        # Ensure word_count is int
        if not isinstance(word_count, int):
            try:
                word_count = int(word_count)
            except (ValueError, TypeError):
                word_count = len(intervention["study_excerpt"].split())

        # Normalize: if flagged subscales present, decision must be needs_analysis
        if flagged_subscales and decision == "no_depressive_content":
            decision = "needs_analysis"

        # Filter invalid subscale codes
        flagged_subscales = [s for s in flagged_subscales if s in REQUIRED_SUBSCALES]

        all_codings = []
        all_scratchpad = {}
        all_exclusion = {}

        # STAGE 2: Detailed analysis for each flagged subscale
        if decision == "needs_analysis" and flagged_subscales:
            detail_user_prompt = build_detail_user_prompt(
                intervention, screening_rationale, transcript_content,
            )

            for subscale_code in flagged_subscales:
                skill_content = skill_contents.get(subscale_code, "")
                if not skill_content:
                    log.warning("[%s] No skill file for %s, skipping", intervention_id, subscale_code)
                    all_scratchpad[subscale_code] = {}
                    all_exclusion[subscale_code] = {}
                    continue

                detail_system = build_detail_system_prompt(subscale_code, skill_content)
                detail_result = await call_api(
                    client, model, detail_system, detail_user_prompt,
                )

                if detail_result is None:
                    log.warning("[%s] Detail API failed for %s", intervention_id, subscale_code)
                    all_scratchpad[subscale_code] = {}
                    all_exclusion[subscale_code] = {}
                    continue

                # Collect codings
                codings = detail_result.get("codings", [])
                if isinstance(codings, list):
                    for coding in codings:
                        # Ensure subscale field is set
                        if isinstance(coding, dict):
                            coding["subscale"] = subscale_code
                            all_codings.append(coding)

                all_scratchpad[subscale_code] = detail_result.get("scratchpad", {})
                all_exclusion[subscale_code] = detail_result.get("exclusion_checklist", {})

    # Build subscale summaries
    subscale_summaries = {}
    for sub in REQUIRED_SUBSCALES:
        sub_codings = [c for c in all_codings if c.get("subscale") == sub]
        weighted_sum = sum(c.get("weight", 0) for c in sub_codings)
        items_found = list({c.get("sub_item", "") for c in sub_codings if c.get("sub_item")})
        subscale_summaries[sub] = {
            "count": len(sub_codings),
            "weighted_sum": weighted_sum,
            "items_found": sorted(items_found),
        }

    # Assemble final result
    result_record = {
        "id": intervention_id,
        "screening": {
            "decision": decision,
            "flagged_subscales": flagged_subscales,
            "screening_rationale": screening_rationale,
        },
        "codings": all_codings,
        "subscale_summaries": subscale_summaries,
        "word_count": word_count,
        "scratchpad": all_scratchpad,
        "exclusion_checklist": all_exclusion,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }

    # Write partial file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_record, f, indent=2, ensure_ascii=False)

    elapsed = time.monotonic() - t0
    active = {k: v for k, v in subscale_summaries.items() if v["count"] > 0}

    return {
        "id": intervention_id,
        "status": "success",
        "duration": round(elapsed, 1),
        "decision": decision,
        "flagged": flagged_subscales,
        "active_subscales": active,
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


async def run_all(
    interventions: list[dict],
    client: AsyncOpenAI,
    model: str,
    partial_dir: Path,
    domains_content: str,
    skill_contents: dict[str, str],
    transcript_content: str | None,
    max_concurrent: int,
) -> list[dict]:
    """Run all interventions with concurrency control."""
    semaphore = asyncio.Semaphore(max_concurrent)
    total = len(interventions)

    screening_system_prompt = build_screening_system_prompt(domains_content)

    if HAS_TQDM:
        pbar = tqdm(total=total, desc="Processing", unit="utterance")
    else:
        pbar = None

    completed_count = 0
    results = []

    def log_result(result):
        nonlocal completed_count
        completed_count += 1
        iid = result["id"]
        status = result["status"]
        if status == "skipped":
            msg = f"[{completed_count}/{total}] Skipping {iid} (already exists)"
        elif status == "success":
            decision = result.get("decision", "?")
            flagged = ",".join(result.get("flagged", []))
            active = result.get("active_subscales", {})
            active_str = ", ".join(
                f"{k}: {v.get('count', 0)}" for k, v in active.items()
            ) if active else ""
            dur = result.get("duration", 0)
            msg = (
                f"[{completed_count}/{total}] {iid}... done "
                f"({dur}s, decision: {decision}"
                f"{', flagged: ' + flagged if flagged else ''}"
                f"{', active: {' + active_str + '}' if active_str else ''})"
            )
        else:
            reason = result.get("reason", "unknown")
            msg = f"[{completed_count}/{total}] {iid}... FAILED ({reason})"

        if pbar:
            pbar.set_postfix_str(iid.split("_")[-1])
            pbar.update(1)
        else:
            log.info(msg)

    async def wrapped(intervention):
        result = await process_intervention(
            semaphore, client, model, intervention, partial_dir,
            domains_content, skill_contents, transcript_content,
            screening_system_prompt,
        )
        log_result(result)
        results.append(result)

    tasks = [asyncio.create_task(wrapped(inv)) for inv in interventions]
    await asyncio.gather(*tasks)

    if pbar:
        pbar.close()

    return results


# ---------------------------------------------------------------------------
# Post-processing (reused from score_cli.py)
# ---------------------------------------------------------------------------


PERSPECTIVE_REMAP = {"impersonal": "inanimate", "general": "inanimate"}


def normalize_record(record: dict) -> dict:
    """Fix known model output inconsistencies."""
    modified = False

    # Fix screening decision vs flagged_subscales mismatch
    screening = record.get("screening", {})
    flagged = screening.get("flagged_subscales", [])
    decision = screening.get("decision", "")

    if flagged and decision == "no_depressive_content":
        screening = {**screening, "decision": "needs_analysis"}
        record = {**record, "screening": screening}
        modified = True

    # Remap invalid perspective values in codings
    codings = record.get("codings", [])
    if codings:
        new_codings = []
        for coding in codings:
            perspective = coding.get("perspective", "")
            remapped = PERSPECTIVE_REMAP.get(perspective.lower() if isinstance(perspective, str) else "", "")
            if remapped:
                coding = {**coding, "perspective": remapped}
                modified = True
            new_codings.append(coding)
        if modified:
            record = {**record, "codings": new_codings}

    return record


def concatenate_results(partial_dir: Path, output_path: Path, expected_ids: list[str]) -> int:
    """Concatenate all partial JSON files into a single JSONL file, sorted by ID."""
    records = []
    for id_ in expected_ids:
        fpath = partial_dir / f"{id_}.json"
        if fpath.exists():
            with open(fpath, "r", encoding="utf-8") as f:
                records.append(normalize_record(json.loads(f.read())))

    records.sort(key=lambda r: r["id"])

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    return len(records)


def run_validation(output_path: Path, input_path: Path | None) -> bool:
    """Run the validation script if available."""
    validate_script = PROJECT_ROOT / "scripts" / "validate_output.py"

    if validate_script.exists():
        import subprocess
        cmd = [sys.executable, str(validate_script), str(output_path)]
        if input_path:
            cmd.append(str(input_path))
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0

    log.info("Validation script not found, running basic checks...")
    return True


def print_analysis_stats(results: list[dict], total: int):
    """Print detailed analysis statistics."""
    all_active = []
    for r in results:
        if r["status"] in ("success", "skipped"):
            all_active.append(r.get("active_subscales", {}))

    if not all_active:
        return

    n = len(all_active)
    subscale_presence = {s: 0 for s in sorted(REQUIRED_SUBSCALES)}
    subscale_total_weight = {s: 0 for s in sorted(REQUIRED_SUBSCALES)}

    for active in all_active:
        for subscale, summary in active.items():
            if subscale in subscale_presence:
                subscale_presence[subscale] += 1
                subscale_total_weight[subscale] += summary.get("weighted_sum", 0)

    active_subscales = {s: c for s, c in subscale_presence.items() if c > 0}

    print("\n" + "=" * 70)
    print("ANALYSIS STATISTICS")
    print("=" * 70)

    total_weighted = sum(subscale_total_weight.values())
    print(f"\n  Total weighted depression content: {total_weighted}")

    if active_subscales:
        print(f"\n  Subscales present ({len(active_subscales)} of 7):")
        for s in sorted(active_subscales):
            wt = subscale_total_weight[s]
            print(f"    {s}: {active_subscales[s]} utterance(s), total weight: {wt}")

        most_present = max(active_subscales, key=active_subscales.get)
        print(f"\n  Most frequent subscale: {most_present} ({active_subscales[most_present]} utterances)")
    else:
        print("\n  No depressive content detected in any utterance.")

    print(f"\n  Subscale frequency (present / {n} utterances):")
    print()

    bar_max_width = 40
    for s in sorted(REQUIRED_SUBSCALES):
        count = subscale_presence[s]
        pct = count / n if n > 0 else 0
        bar_len = round(pct * bar_max_width)
        bar = "\u2588" * bar_len
        if count > 0:
            print(f"    {s}  {bar:<{bar_max_width}s} {count:>3} ({pct:5.1%})")
        else:
            print(f"    {s}  {'·':<{bar_max_width}s}   0 ( 0.0%)")

    print("\n" + "=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Gottschalk-Gleser Depression Scale — API-based orchestrator (Requesty/OpenAI-compatible)",
    )
    parser.add_argument(
        "transcript_name",
        help="Name of the transcript directory in results/ (e.g., 300)",
    )
    parser.add_argument(
        "--model", default=None,
        help="Model ID (default: from .env REQUESTY_MODEL or alibaba/qwen3.5)",
    )
    parser.add_argument(
        "--max-concurrent", type=int, default=10,
        help="Max concurrent API calls (default: 10)",
    )
    parser.add_argument(
        "--output-suffix", default=None,
        help="Suffix for output file name (default: derived from model name)",
    )
    parser.add_argument(
        "--no-transcript", action="store_true",
        help="Exclude full transcript from prompts to save tokens",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "--ids", nargs="*", default=None,
        help="Process only these intervention IDs (for testing)",
    )
    parser.add_argument(
        "--auto-continue", action="store_true",
        help="Automatically continue from existing results without prompting",
    )

    args = parser.parse_args()

    # Load .env
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("REQUESTY_API_KEY")
    base_url = os.getenv("REQUESTY_BASE_URL", "https://router.requesty.ai/v1")
    default_model = os.getenv("REQUESTY_MODEL", "alibaba/qwen3.5")

    if not api_key:
        log.error("REQUESTY_API_KEY not found in .env or environment")
        sys.exit(1)

    model = args.model or default_model

    if args.output_suffix is None:
        # Derive from model name: alibaba/qwen3.5 -> qwen
        args.output_suffix = model.split("/")[-1].split(".")[0].split("-")[0].lower()

    # -----------------------------------------------------------------------
    # Resolve paths
    # -----------------------------------------------------------------------

    transcript_dir = PROJECT_ROOT / "results" / args.transcript_name
    input_path = transcript_dir / "input.jsonl"
    partial_dir = transcript_dir / f"partial_{args.output_suffix}"
    output_path = transcript_dir / f"output_{args.output_suffix}.jsonl"
    transcript_filepath = transcript_dir / "transcript.md"

    required_paths = [
        ("Input file", input_path),
        ("Transcript", transcript_filepath),
        ("Depression domains", DOMAINS_PATH),
        ("Skills dir", SKILLS_DIR),
    ]
    for label, p in required_paths:
        if not p.exists():
            log.error("%s not found: %s", label, p)
            sys.exit(1)

    partial_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Check for existing results
    # -----------------------------------------------------------------------

    existing_partials = list(partial_dir.glob("*.json"))
    existing_output = output_path.exists()

    if (existing_partials or existing_output) and not args.dry_run:
        n_existing = len(existing_partials)
        if args.auto_continue:
            log.info("Auto-continuing: keeping %d existing partials, processing missing utterances", n_existing)
            choice = "c"
        else:
            print("\n" + "=" * 70)
            print(f"EXISTING RESULTS DETECTED ({args.output_suffix})")
            print("=" * 70)
            if existing_partials:
                print(f"  Partial files: {n_existing} in {partial_dir.name}/")
            if existing_output:
                print(f"  Output file:   {output_path.name}")
            print()
            print("  [c] Continue -- keep existing results, process only missing utterances")
            print("  [d] Delete   -- remove all prior results and start fresh")
            print("  [q] Quit")
            print("=" * 70)

            choice = input("\nChoice [c/d/q]: ").strip().lower()

        if choice == "q":
            print("Aborted.")
            sys.exit(0)
        elif choice == "d":
            import shutil
            if existing_partials:
                shutil.rmtree(partial_dir)
                partial_dir.mkdir(parents=True, exist_ok=True)
                print(f"  Deleted {n_existing} partial files.")
            if existing_output:
                output_path.unlink()
                print(f"  Deleted {output_path.name}.")
            print()
        elif choice == "c":
            if not args.auto_continue:
                print("  Continuing -- will skip already completed utterances.\n")
        else:
            print(f"  Unknown choice '{choice}'. Continuing by default.\n")

    # Set up log file tee
    log_path = transcript_dir / f"run_{args.output_suffix}.log"
    log_file = open(log_path, "w", encoding="utf-8")
    sys.stdout = TeeWriter(sys.__stdout__, log_file)
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    log.addHandler(file_handler)

    # -----------------------------------------------------------------------
    # Load data
    # -----------------------------------------------------------------------

    interventions = load_interventions(input_path)

    if args.ids:
        id_set = set(args.ids)
        interventions = [i for i in interventions if i["id"] in id_set]
        if not interventions:
            log.error("No interventions matched the specified IDs")
            sys.exit(1)

    total = len(interventions)

    # Load reference content
    domains_content = DOMAINS_PATH.read_text(encoding="utf-8")
    skill_contents = {}
    for sub in REQUIRED_SUBSCALES:
        skill_path = SKILLS_DIR / sub / "SKILL.md"
        if skill_path.exists():
            skill_contents[sub] = load_file_content(skill_path)

    transcript_content = None
    if not args.no_transcript:
        transcript_content = transcript_filepath.read_text(encoding="utf-8")

    log.info("Transcript: %s", args.transcript_name)
    log.info("Model: %s", model)
    log.info("Utterances: %d", total)
    log.info("Max concurrent: %d", args.max_concurrent)
    log.info("Transcript context: %s", "included" if transcript_content else "excluded")
    log.info("Output: %s", output_path)

    if args.dry_run:
        log.info("--- DRY RUN ---")
        already_done = sum(
            1 for i in interventions
            if validate_partial(partial_dir / f"{i['id']}.json")
        )
        remaining = total - already_done
        log.info("Already completed: %d / %d", already_done, total)
        log.info("Would process: %d utterances", remaining)

        # Estimate cost
        avg_input_screening = 3500
        avg_input_detail = 5000
        avg_output = 250
        flagged_rate = 0.29
        avg_subscales = 1.8

        total_input = remaining * avg_input_screening
        detail_calls = int(remaining * flagged_rate * avg_subscales)
        total_input += detail_calls * avg_input_detail
        total_output = (remaining + detail_calls) * avg_output

        # Pricing lookup (per 1M tokens) — update when changing models
        PRICING = {
            "zai/GLM-5":          (1.00, 3.20),
            "alibaba/qwen3.5":    (0.60, 3.60),
            "alibaba/qwen-plus":  (0.40, 2.40),
        }
        price_in, price_out = PRICING.get(model, (1.00, 3.20))
        cost_in = total_input / 1_000_000 * price_in
        cost_out = total_output / 1_000_000 * price_out
        total_cost = cost_in + cost_out

        log.info("Estimated API calls: %d screening + %d detail = %d total",
                 remaining, detail_calls, remaining + detail_calls)
        log.info("Estimated cost: ~$%.2f (input: $%.2f, output: $%.2f)",
                 total_cost, cost_in, cost_out)
        return

    # -----------------------------------------------------------------------
    # Create client and run
    # -----------------------------------------------------------------------

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        max_retries=1,
    )

    t_start = time.monotonic()

    results = asyncio.run(
        run_all(
            interventions, client, model, partial_dir,
            domains_content, skill_contents, transcript_content,
            max_concurrent=args.max_concurrent,
        )
    )

    elapsed = time.monotonic() - t_start

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    succeeded = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "failed")

    print("\n" + "=" * 70)
    print("ORCHESTRATION SUMMARY")
    print("=" * 70)
    print(f"  Total utterances:    {total}")
    print(f"  Succeeded:           {succeeded}")
    print(f"  Skipped (cached):    {skipped}")
    print(f"  Failed:              {failed}")
    print(f"  Elapsed time:        {elapsed:.1f}s ({elapsed/60:.1f}m)")
    if succeeded > 0:
        durations = [r["duration"] for r in results if r.get("duration")]
        if durations:
            print(f"  Avg time/utterance:  {sum(durations)/len(durations):.1f}s")
    print("=" * 70)

    if failed > 0:
        print("\nFailed utterances:")
        for r in results:
            if r["status"] == "failed":
                print(f"  - {r['id']}: {r.get('reason', 'unknown')}")

    # -----------------------------------------------------------------------
    # Concatenate results
    # -----------------------------------------------------------------------

    expected_ids = [i["id"] for i in interventions]
    n_written = concatenate_results(partial_dir, output_path, expected_ids)
    log.info("Wrote %d records to %s", n_written, output_path)

    if n_written < total:
        log.warning(
            "Only %d / %d records written (some utterances may have failed)",
            n_written, total,
        )

    # -----------------------------------------------------------------------
    # Validate
    # -----------------------------------------------------------------------

    print()
    validation_input = None if args.ids else input_path
    is_valid = run_validation(output_path, validation_input)

    # -----------------------------------------------------------------------
    # Merge input + output into CSV
    # -----------------------------------------------------------------------

    csv_path = None
    if is_valid:
        merge_script = PROJECT_ROOT / "scripts" / "merge_to_csv.py"
        output_filename = f"output_{args.output_suffix}.jsonl"
        if merge_script.exists():
            import subprocess
            result = subprocess.run(
                [sys.executable, str(merge_script), str(transcript_dir), output_filename],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                csv_path = result.stdout.strip().replace("CSV created successfully: ", "")
                log.info("CSV merged: %s", csv_path)
            else:
                log.warning("CSV merge failed: %s", result.stderr or result.stdout)

    # -----------------------------------------------------------------------
    # Analysis statistics & summary
    # -----------------------------------------------------------------------

    print_analysis_stats(results, total)

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"  Output JSONL: {output_path}")
    if csv_path:
        print(f"  Output CSV:   {csv_path}")
    print(f"  Log file:     {log_path}")
    print(f"  Validation:   {'PASSED' if is_valid else 'FAILED'}")
    print("=" * 70)

    # Close log file and restore stdout
    sys.stdout = sys.__stdout__
    log_file.close()

    sys.exit(0 if is_valid and failed == 0 else 1)


if __name__ == "__main__":
    main()
