#!/usr/bin/env python3
"""
Gottschalk-Gleser Depression Scale — Analysis Orchestrator

Spawns isolated `claude -p` sessions for each patient utterance,
ensuring complete context isolation between evaluations.

Each `claude -p` invocation is a full Claude Code session with tool access
(Read, Write, Bash). The model reads reference files itself, evaluates the
utterance for depressive content, and writes the result to a partial JSON file.

Usage:
    python scripts/score_cli.py transcript_name
    python scripts/score_cli.py transcript_name --model sonnet --max-concurrent 5
    python scripts/score_cli.py transcript_name --output-suffix opus46 --model opus
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "config" / "subagent_template.md"
BATCH_TEMPLATE_PATH = PROJECT_ROOT / "config" / "subagent_template_batch.md"
DOMAINS_PATH = PROJECT_ROOT / "config" / "depression_domains.md"
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"

REQUIRED_SUBSCALES = {"HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS"}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("depression-orchestrator")


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

    # Try JSON array first
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Fall back to JSONL
    records = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def load_template(template_path: Path) -> str:
    """Load the prompt template, stripping the header comment block."""
    content = template_path.read_text(encoding="utf-8")
    # Strip the header comment block (everything before the first --- separator)
    parts = content.split("---", 1)
    if len(parts) >= 2:
        return parts[1].strip()
    return content.strip()


def construct_prompt(
    intervention: dict,
    template: str,
    transcript_filepath: str,
    domains_filepath: str,
    skills_dir: str,
    output_filepath: str,
) -> str:
    """Substitute variables into the prompt template."""
    prompt = template
    prompt = prompt.replace("{id}", intervention["id"])
    prompt = prompt.replace("{line_number}", str(intervention["line_number"]))
    prompt = prompt.replace("{close_context}", intervention["close_context"])
    prompt = prompt.replace("{study_excerpt}", intervention["study_excerpt"])
    prompt = prompt.replace("{output_filepath}", output_filepath)
    prompt = prompt.replace("{transcript_filepath}", transcript_filepath)
    prompt = prompt.replace("{domains_filepath}", domains_filepath)
    prompt = prompt.replace("{skills_dir}", skills_dir)
    return prompt


def construct_batch_prompt(
    interventions: list[dict],
    template: str,
    transcript_filepath: str,
    domains_filepath: str,
    skills_dir: str,
    partial_dir: str,
) -> str:
    """Build a single prompt containing multiple utterances for batch processing."""
    # Build per-utterance blocks
    blocks = []
    for idx, inv in enumerate(interventions, 1):
        output_filepath = str(Path(partial_dir) / f"{inv['id']}.json")
        block = (
            f"───────────────────────────────────────────────────────────────────────\n"
            f"UTTERANCE {idx} OF {len(interventions)}\n"
            f"───────────────────────────────────────────────────────────────────────\n"
            f"\n"
            f"ID: {inv['id']}\n"
            f"Line Number: {inv['line_number']}\n"
            f"Output File: `{output_filepath}`\n"
            f"\n"
            f"### Close Context\n"
            f"<close_context>\n"
            f"{inv['close_context']}\n"
            f"</close_context>\n"
            f"\n"
            f"### Study Excerpt\n"
            f"<study_excerpt>\n"
            f"{inv['study_excerpt']}\n"
            f"</study_excerpt>\n"
        )
        blocks.append(block)

    utterance_blocks = "\n".join(blocks)

    prompt = template
    prompt = prompt.replace("{utterance_blocks}", utterance_blocks)
    prompt = prompt.replace("{transcript_filepath}", transcript_filepath)
    prompt = prompt.replace("{domains_filepath}", domains_filepath)
    prompt = prompt.replace("{skills_dir}", skills_dir)
    prompt = prompt.replace("{batch_size}", str(len(interventions)))
    return prompt


def validate_partial(path: Path) -> bool:
    """Check if a partial result file exists and contains valid JSON with required fields."""
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Basic structural checks
        if not isinstance(data, dict):
            return False
        if "id" not in data or "screening" not in data:
            return False
        # Check subscale_summaries has all 7 subscales
        summaries = data.get("subscale_summaries", {})
        if not REQUIRED_SUBSCALES.issubset(summaries.keys()):
            return False
        # Check codings is a list
        if not isinstance(data.get("codings", None), list):
            return False
        # Check word_count exists
        if "word_count" not in data:
            return False
        return True
    except (json.JSONDecodeError, OSError):
        return False


# ---------------------------------------------------------------------------
# Core: run a single intervention via `claude -p`
# ---------------------------------------------------------------------------


async def run_intervention(
    semaphore: asyncio.Semaphore,
    intervention: dict,
    template: str,
    paths: dict,
    model: str,
    max_retries: int = 3,
    retry_delay: float = 10.0,
    timeout: float = 600.0,
) -> dict:
    """
    Run a single intervention evaluation via `claude -p`.

    Returns a result dict with keys: id, status, attempt, duration, decision, flagged.
    """
    intervention_id = intervention["id"]
    output_path = Path(paths["partial_dir"]) / f"{intervention_id}.json"

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

    prompt = construct_prompt(
        intervention,
        template,
        transcript_filepath=paths["transcript_filepath"],
        domains_filepath=paths["domains_filepath"],
        skills_dir=paths["skills_dir"],
        output_filepath=str(output_path),
    )
    prompt_bytes = prompt.encode("utf-8")

    last_reason = ""
    for attempt in range(1, max_retries + 1):
        t0 = time.monotonic()

        async with semaphore:
            try:
                cmd = [
                    "claude",
                    "-p",
                    "--model", model,
                    "--dangerously-skip-permissions",
                    "--no-session-persistence",
                    "--verbose",
                ]

                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(PROJECT_ROOT),
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(input=prompt_bytes),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
                    last_reason = f"timeout after {timeout}s"
                    log.warning(
                        "[%s] Attempt %d/%d timed out after %.0fs",
                        intervention_id, attempt, max_retries, timeout,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay * attempt)
                    continue

                elapsed = time.monotonic() - t0

                if proc.returncode != 0:
                    last_reason = f"exit code {proc.returncode}"
                    stderr_text = stderr.decode("utf-8", errors="replace")[:500]
                    log.warning(
                        "[%s] Attempt %d/%d failed (exit %d): %s",
                        intervention_id, attempt, max_retries,
                        proc.returncode, stderr_text,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay * attempt)
                    continue

            except FileNotFoundError:
                log.error(
                    "'claude' command not found. Ensure Claude Code CLI is installed and on PATH."
                )
                return {"id": intervention_id, "status": "failed", "reason": "claude not found"}
            except Exception as e:
                last_reason = str(e)
                log.warning(
                    "[%s] Attempt %d/%d exception: %s",
                    intervention_id, attempt, max_retries, e,
                )
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * attempt)
                continue

        # Validate result (outside semaphore)
        if validate_partial(output_path):
            try:
                with open(output_path) as f:
                    result_data = json.load(f)
                decision = result_data.get("screening", {}).get("decision", "?")
                flagged = result_data.get("screening", {}).get("flagged_subscales", [])
                summaries = result_data.get("subscale_summaries", {})
                active = {k: v for k, v in summaries.items() if v.get("count", 0) > 0}
            except Exception:
                decision, flagged, active = "?", [], {}

            return {
                "id": intervention_id,
                "status": "success",
                "attempt": attempt,
                "duration": round(elapsed, 1),
                "decision": decision,
                "flagged": flagged,
                "active_subscales": active,
            }

        last_reason = "output file missing or invalid JSON"
        log.warning(
            "[%s] Attempt %d/%d: output file not created or invalid",
            intervention_id, attempt, max_retries,
        )
        if attempt < max_retries:
            await asyncio.sleep(retry_delay * attempt)

    return {"id": intervention_id, "status": "failed", "reason": last_reason}


# ---------------------------------------------------------------------------
# Core: run a batch of interventions via a single `claude -p`
# ---------------------------------------------------------------------------


async def run_batch_group(
    semaphore: asyncio.Semaphore,
    interventions: list[dict],
    template: str,
    paths: dict,
    model: str,
    max_retries: int = 3,
    retry_delay: float = 10.0,
    timeout: float = 600.0,
) -> list[dict]:
    """
    Run a batch of interventions in a single `claude -p` call.

    Returns a list of result dicts (one per utterance).
    """
    partial_dir = Path(paths["partial_dir"])

    # Filter out already-completed utterances
    pending = []
    results = []
    for inv in interventions:
        output_path = partial_dir / f"{inv['id']}.json"
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
            results.append({
                "id": inv["id"],
                "status": "skipped",
                "decision": decision,
                "flagged": flagged,
                "active_subscales": active,
            })
        else:
            pending.append(inv)

    if not pending:
        return results

    prompt = construct_batch_prompt(
        pending,
        template,
        transcript_filepath=paths["transcript_filepath"],
        domains_filepath=paths["domains_filepath"],
        skills_dir=paths["skills_dir"],
        partial_dir=paths["partial_dir"],
    )
    prompt_bytes = prompt.encode("utf-8")

    # Scale timeout with batch size: base timeout per utterance
    batch_timeout = timeout * len(pending)

    last_reason = ""
    for attempt in range(1, max_retries + 1):
        t0 = time.monotonic()

        async with semaphore:
            try:
                cmd = [
                    "claude",
                    "-p",
                    "--model", model,
                    "--dangerously-skip-permissions",
                    "--no-session-persistence",
                    "--verbose",
                ]

                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(PROJECT_ROOT),
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(input=prompt_bytes),
                        timeout=batch_timeout,
                    )
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
                    last_reason = f"timeout after {batch_timeout}s"
                    ids_str = ", ".join(inv["id"] for inv in pending)
                    log.warning(
                        "[batch %s] Attempt %d/%d timed out after %.0fs",
                        ids_str, attempt, max_retries, batch_timeout,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay * attempt)
                    continue

                elapsed = time.monotonic() - t0

                if proc.returncode != 0:
                    last_reason = f"exit code {proc.returncode}"
                    stderr_text = stderr.decode("utf-8", errors="replace")[:500]
                    ids_str = ", ".join(inv["id"] for inv in pending)
                    log.warning(
                        "[batch %s] Attempt %d/%d failed (exit %d): %s",
                        ids_str, attempt, max_retries,
                        proc.returncode, stderr_text,
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay * attempt)
                    continue

            except FileNotFoundError:
                log.error(
                    "'claude' command not found. Ensure Claude Code CLI is installed and on PATH."
                )
                for inv in pending:
                    results.append({"id": inv["id"], "status": "failed", "reason": "claude not found"})
                return results
            except Exception as e:
                last_reason = str(e)
                ids_str = ", ".join(inv["id"] for inv in pending)
                log.warning(
                    "[batch %s] Attempt %d/%d exception: %s",
                    ids_str, attempt, max_retries, e,
                )
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * attempt)
                continue

        # Validate each expected partial (outside semaphore)
        all_valid = True
        for inv in pending:
            output_path = partial_dir / f"{inv['id']}.json"
            if validate_partial(output_path):
                try:
                    with open(output_path) as f:
                        result_data = json.load(f)
                    decision = result_data.get("screening", {}).get("decision", "?")
                    flagged = result_data.get("screening", {}).get("flagged_subscales", [])
                    summaries = result_data.get("subscale_summaries", {})
                    active = {k: v for k, v in summaries.items() if v.get("count", 0) > 0}
                except Exception:
                    decision, flagged, active = "?", [], {}

                results.append({
                    "id": inv["id"],
                    "status": "success",
                    "attempt": attempt,
                    "duration": round(elapsed / len(pending), 1),
                    "decision": decision,
                    "flagged": flagged,
                    "active_subscales": active,
                })
            else:
                all_valid = False

        if all_valid:
            return results

        # Some partials missing — retry only if we have attempts left
        # Remove successfully written ones from pending for next attempt
        succeeded_ids = {r["id"] for r in results if r["status"] == "success"}
        pending = [inv for inv in pending if inv["id"] not in succeeded_ids]

        if not pending:
            return results

        last_reason = f"partial files missing for: {', '.join(inv['id'] for inv in pending)}"
        log.warning(
            "[batch] Attempt %d/%d: %d of %d partials missing",
            attempt, max_retries, len(pending), len(interventions),
        )
        if attempt < max_retries:
            await asyncio.sleep(retry_delay * attempt)

    # All retries exhausted — mark remaining as failed
    succeeded_ids = {r["id"] for r in results}
    for inv in interventions:
        if inv["id"] not in succeeded_ids:
            results.append({"id": inv["id"], "status": "failed", "reason": last_reason})

    return results


# ---------------------------------------------------------------------------
# Orchestrator: run all interventions
# ---------------------------------------------------------------------------


async def run_all(
    interventions: list[dict],
    template: str,
    batch_template: str | None,
    paths: dict,
    model: str,
    max_concurrent: int,
    max_retries: int,
    retry_delay: float,
    timeout: float,
    batch_size: int = 1,
) -> list[dict]:
    """Run all interventions with concurrency control. Returns list of result dicts."""
    semaphore = asyncio.Semaphore(max_concurrent)
    total = len(interventions)

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

    if batch_size <= 1:
        # Single-utterance mode (original behavior)
        async def wrapped_single(intervention):
            result = await run_intervention(
                semaphore, intervention, template, paths, model,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=timeout,
            )
            log_result(result)
            results.append(result)

        tasks = [
            asyncio.create_task(wrapped_single(inv))
            for inv in interventions
        ]
        await asyncio.gather(*tasks)
    else:
        # Batch mode: group interventions into batches
        batches = [
            interventions[i:i + batch_size]
            for i in range(0, len(interventions), batch_size)
        ]
        log.info(
            "Batch mode: %d utterances → %d batches of up to %d",
            total, len(batches), batch_size,
        )

        async def wrapped_batch(batch):
            batch_results = await run_batch_group(
                semaphore, batch, batch_template, paths, model,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=timeout,
            )
            for result in batch_results:
                log_result(result)
                results.append(result)

        tasks = [
            asyncio.create_task(wrapped_batch(batch))
            for batch in batches
        ]
        await asyncio.gather(*tasks)

    if pbar:
        pbar.close()

    return results


# ---------------------------------------------------------------------------
# Post-processing: concatenate, sort, validate
# ---------------------------------------------------------------------------


def normalize_record(record: dict) -> dict:
    """Fix known model output inconsistencies.

    - If flagged_subscales is non-empty, decision must be 'needs_analysis'.
    """
    screening = record.get("screening", {})
    flagged = screening.get("flagged_subscales", [])
    decision = screening.get("decision", "")

    if flagged and decision == "no_depressive_content":
        screening = {**screening, "decision": "needs_analysis"}
        return {**record, "screening": screening}

    return record


def concatenate_results(partial_dir: Path, output_path: Path, expected_ids: list[str]) -> int:
    """
    Concatenate all partial JSON files into a single JSONL file, sorted by ID.
    Applies normalization to fix known model output inconsistencies.
    Returns the number of records written.
    """
    records = []
    for id_ in expected_ids:
        fpath = partial_dir / f"{id_}.json"
        if fpath.exists():
            with open(fpath, "r", encoding="utf-8") as f:
                records.append(normalize_record(json.loads(f.read())))

    # Sort by ID to match input order
    records.sort(key=lambda r: r["id"])

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    return len(records)


def run_validation(output_path: Path, input_path: Path | None) -> bool:
    """Run the validation script if available, otherwise do basic validation."""
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

    # Fallback: basic validation
    log.info("Validation script not found, running basic checks...")
    errors = []
    seen_ids = set()

    with open(output_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: invalid JSON - {e}")
                continue

            rid = record.get("id")
            if rid in seen_ids:
                errors.append(f"Duplicate ID: {rid}")
            seen_ids.add(rid)

            summaries = record.get("subscale_summaries", {})
            missing = REQUIRED_SUBSCALES - set(summaries.keys())
            if missing:
                errors.append(f"{rid}: missing subscales in summaries: {missing}")

    if errors:
        log.error("Validation FAILED with %d errors:", len(errors))
        for e in errors:
            log.error("  %s", e)
        return False

    log.info("Validation PASSED (%d records)", len(seen_ids))
    return True


def print_analysis_stats(results: list[dict], total: int):
    """Print detailed analysis statistics from all completed/skipped results."""
    all_active = []
    for r in results:
        if r["status"] in ("success", "skipped"):
            all_active.append(r.get("active_subscales", {}))

    if not all_active:
        return

    n = len(all_active)

    # Count how many interventions have each subscale with count > 0
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

    # Horizontal histogram
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
        description="Gottschalk-Gleser Depression Scale — spawns isolated claude -p sessions per utterance",
    )
    parser.add_argument(
        "transcript_name",
        help="Name of the transcript directory in results/ (e.g., call_001)",
    )
    parser.add_argument(
        "--model", default="sonnet",
        help="Claude model to use (default: sonnet)",
    )
    parser.add_argument(
        "--max-concurrent", type=int, default=5,
        help="Max concurrent claude -p subprocesses (default: 5)",
    )
    parser.add_argument(
        "--output-suffix", default=None,
        help="Suffix for output file name (default: same as --model)",
    )
    parser.add_argument(
        "--max-retries", type=int, default=3,
        help="Max retries per utterance on failure (default: 3)",
    )
    parser.add_argument(
        "--retry-delay", type=float, default=10.0,
        help="Base delay in seconds between retries (multiplied by attempt number) (default: 10)",
    )
    parser.add_argument(
        "--timeout", type=float, default=600.0,
        help="Timeout per subprocess in seconds (default: 600)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=1,
        help="Number of utterances per claude -p call (default: 1, isolated mode)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "--ids", nargs="*", default=None,
        help="Process only these intervention IDs (for testing). If not specified, process all.",
    )

    args = parser.parse_args()

    if args.output_suffix is None:
        args.output_suffix = args.model

    # -----------------------------------------------------------------------
    # Resolve paths
    # -----------------------------------------------------------------------

    transcript_dir = PROJECT_ROOT / "results" / args.transcript_name
    input_path = transcript_dir / "input.jsonl"
    partial_dir = transcript_dir / f"partial_{args.output_suffix}"
    output_path = transcript_dir / f"output_{args.output_suffix}.jsonl"
    transcript_filepath = transcript_dir / "transcript.md"

    # Validate paths exist
    required_paths = [
        ("Input file", input_path),
        ("Transcript", transcript_filepath),
        ("Template", TEMPLATE_PATH),
        ("Depression domains", DOMAINS_PATH),
        ("Skills dir", SKILLS_DIR),
    ]
    if args.batch_size > 1:
        required_paths.append(("Batch template", BATCH_TEMPLATE_PATH))
    for label, p in required_paths:
        if not p.exists():
            log.error("%s not found: %s", label, p)
            sys.exit(1)

    # Create partial directory
    partial_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Check for existing results
    # -----------------------------------------------------------------------

    existing_partials = list(partial_dir.glob("*.json"))
    existing_output = output_path.exists()

    if (existing_partials or existing_output) and not args.dry_run:
        n_existing = len(existing_partials)
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
            for ext_file in transcript_dir.glob(f"*{args.output_suffix}*"):
                if ext_file != output_path:
                    ext_file.unlink()
                    print(f"  Deleted {ext_file.name}.")
            print()
        elif choice == "c":
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

    template = load_template(TEMPLATE_PATH)
    batch_template = load_template(BATCH_TEMPLATE_PATH) if args.batch_size > 1 else None
    interventions = load_interventions(input_path)

    # Filter by IDs if specified
    if args.ids:
        id_set = set(args.ids)
        interventions = [i for i in interventions if i["id"] in id_set]
        if not interventions:
            log.error("No interventions matched the specified IDs")
            sys.exit(1)

    total = len(interventions)
    log.info("Transcript: %s", args.transcript_name)
    log.info("Model: %s", args.model)
    log.info("Utterances: %d", total)
    log.info("Batch size: %d", args.batch_size)
    log.info("Max concurrent: %d", args.max_concurrent)
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
        if args.batch_size > 1:
            n_batches = (remaining + args.batch_size - 1) // args.batch_size if remaining > 0 else 0
            log.info("Batch size: %d → %d subprocess calls", args.batch_size, n_batches)
        if interventions:
            if args.batch_size > 1 and batch_template:
                # Show batch prompt preview
                preview_batch = interventions[:min(args.batch_size, len(interventions))]
                preview = construct_batch_prompt(
                    preview_batch, batch_template,
                    transcript_filepath=str(transcript_filepath),
                    domains_filepath=str(DOMAINS_PATH),
                    skills_dir=str(SKILLS_DIR),
                    partial_dir=str(partial_dir),
                )
                log.info("First batch prompt preview (truncated to 800 chars):")
                print(preview[:800] + "\n... (truncated)")
            else:
                preview = construct_prompt(
                    interventions[0], template,
                    transcript_filepath=str(transcript_filepath),
                    domains_filepath=str(DOMAINS_PATH),
                    skills_dir=str(SKILLS_DIR),
                    output_filepath=str(partial_dir / f"{interventions[0]['id']}.json"),
                )
                log.info("First utterance prompt preview (truncated to 500 chars):")
                print(preview[:500] + "\n... (truncated)")
        return

    # -----------------------------------------------------------------------
    # Run all interventions
    # -----------------------------------------------------------------------

    paths = {
        "partial_dir": str(partial_dir),
        "transcript_filepath": str(transcript_filepath),
        "domains_filepath": str(DOMAINS_PATH),
        "skills_dir": str(SKILLS_DIR),
    }

    t_start = time.monotonic()

    results = asyncio.run(
        run_all(
            interventions, template, batch_template, paths, args.model,
            max_concurrent=args.max_concurrent,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay,
            timeout=args.timeout,
            batch_size=args.batch_size,
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
        else:
            log.warning("merge_to_csv.py not found, skipping CSV merge")

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
