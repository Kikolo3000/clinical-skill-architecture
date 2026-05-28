#!/usr/bin/env python3
"""
Validate Gottschalk-Gleser Depression Scale analysis output.

Validates the output.jsonl file against the expected schema:
- codings array with clause-level entries
- subscale_summaries for all 7 subscales
- proper perspective/weight assignments
- consistency between codings and summaries
"""

import json
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_SUBSCALES = {"HOP", "SAC", "PMR", "SOM", "DAM", "SEP", "HOS"}
VALID_DECISIONS = {"no_depressive_content", "needs_analysis"}
VALID_PERSPECTIVES = {"self", "others", "inanimate", "denial"}
MAX_WEIGHT = 4  # SAC.C suicide items can be weight 4


def validate_output_file(output_path: str, input_path: str = None) -> tuple[bool, list[str]]:
    """Validate depression analysis output file.

    Returns (is_valid, list_of_errors).
    """
    errors = []
    output_path = Path(output_path)

    if not output_path.exists():
        return False, [f"Output file not found: {output_path}"]

    records = []
    seen_ids = set()

    try:
        with open(output_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append((line_num, record))

                    record_id = record.get("id")
                    if record_id in seen_ids:
                        errors.append(f"Line {line_num}: Duplicate ID '{record_id}'")
                    seen_ids.add(record_id)

                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")

    except Exception as e:
        return False, [f"Error reading file: {e}"]

    if not records:
        return False, ["Output file is empty"]

    for line_num, record in records:
        errors.extend(validate_record(record, line_num))

    # Check completeness against input if provided
    if input_path:
        input_ids = load_input_ids(input_path)
        if input_ids:
            missing_ids = input_ids - seen_ids
            extra_ids = seen_ids - input_ids
            if missing_ids:
                errors.append(f"Missing output for input IDs: {sorted(missing_ids)}")
            if extra_ids:
                errors.append(f"Extra output IDs not in input: {sorted(extra_ids)}")

    return len(errors) == 0, errors


def validate_record(record: dict, line_num: int) -> list[str]:
    """Validate a single output record."""
    errors = []
    prefix = f"Line {line_num}"

    # Required top-level fields
    required_fields = ["id", "screening", "codings", "subscale_summaries",
                       "word_count", "analyzed_at"]
    for field in required_fields:
        if field not in record:
            errors.append(f"{prefix}: Missing required field '{field}'")

    # Validate ID
    if "id" in record:
        if not isinstance(record["id"], str) or not record["id"]:
            errors.append(f"{prefix}: ID must be non-empty string")

    # Validate screening
    if "screening" in record:
        errors.extend(validate_screening(record["screening"], prefix))

    # Validate codings array
    if "codings" in record:
        if not isinstance(record["codings"], list):
            errors.append(f"{prefix}: 'codings' must be an array")
        else:
            for i, coding in enumerate(record["codings"]):
                errors.extend(validate_coding(coding, f"{prefix}, coding[{i}]"))

    # Validate subscale_summaries
    if "subscale_summaries" in record:
        errors.extend(validate_summaries(record, prefix))

    # Validate word_count
    if "word_count" in record:
        wc = record["word_count"]
        if not isinstance(wc, int) or wc < 0:
            errors.append(f"{prefix}: word_count must be a non-negative integer, got {wc}")

    # Validate timestamp
    if "analyzed_at" in record:
        try:
            datetime.fromisoformat(record["analyzed_at"].replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            errors.append(f"{prefix}: Invalid ISO 8601 timestamp - {e}")

    # Consistency: codings vs screening decision
    if "screening" in record and "codings" in record:
        decision = record["screening"].get("decision")
        codings = record["codings"]
        if decision == "no_depressive_content" and codings:
            errors.append(f"{prefix}: Decision 'no_depressive_content' but codings is non-empty")

    # Validate scratchpad and exclusion_checklist
    if "scratchpad" in record:
        errors.extend(validate_scratchpad_exclusion(record, "scratchpad", prefix))
    if "exclusion_checklist" in record:
        errors.extend(validate_scratchpad_exclusion(record, "exclusion_checklist", prefix))

    return errors


def validate_screening(screening: dict, prefix: str) -> list[str]:
    """Validate screening object structure."""
    errors = []

    if not isinstance(screening, dict):
        return [f"{prefix}: 'screening' must be an object"]

    if "decision" not in screening:
        errors.append(f"{prefix}: screening missing 'decision'")
    elif screening["decision"] not in VALID_DECISIONS:
        errors.append(f"{prefix}: screening decision must be {VALID_DECISIONS}, got '{screening['decision']}'")

    if "flagged_subscales" not in screening:
        errors.append(f"{prefix}: screening missing 'flagged_subscales'")
    elif not isinstance(screening["flagged_subscales"], list):
        errors.append(f"{prefix}: screening 'flagged_subscales' must be array")
    else:
        for sub in screening["flagged_subscales"]:
            if sub not in REQUIRED_SUBSCALES:
                errors.append(f"{prefix}: Invalid subscale code in flagged_subscales: '{sub}'")

    if "screening_rationale" not in screening:
        errors.append(f"{prefix}: screening missing 'screening_rationale'")
    elif not isinstance(screening["screening_rationale"], str):
        errors.append(f"{prefix}: screening_rationale must be string")

    # Consistency
    if "decision" in screening and "flagged_subscales" in screening:
        decision = screening["decision"]
        flagged = screening["flagged_subscales"]
        if decision == "no_depressive_content" and flagged:
            errors.append(f"{prefix}: Decision 'no_depressive_content' but flagged_subscales is not empty")
        elif decision == "needs_analysis" and not flagged:
            errors.append(f"{prefix}: Decision 'needs_analysis' but flagged_subscales is empty")

    return errors


def validate_coding(coding: dict, prefix: str) -> list[str]:
    """Validate a single coding entry."""
    errors = []

    required = ["clause", "subscale", "sub_item", "perspective", "weight", "rationale"]
    for field in required:
        if field not in coding:
            errors.append(f"{prefix}: Missing field '{field}'")

    if "subscale" in coding and coding["subscale"] not in REQUIRED_SUBSCALES:
        errors.append(f"{prefix}: Invalid subscale '{coding['subscale']}'")

    if "perspective" in coding and coding["perspective"] not in VALID_PERSPECTIVES:
        errors.append(f"{prefix}: Invalid perspective '{coding['perspective']}'")

    if "weight" in coding:
        w = coding["weight"]
        if not isinstance(w, int) or w < 1 or w > MAX_WEIGHT:
            errors.append(f"{prefix}: Weight must be 1-{MAX_WEIGHT}, got {w}")

    if "clause" in coding:
        if not isinstance(coding["clause"], str) or not coding["clause"].strip():
            errors.append(f"{prefix}: Clause must be non-empty string")

    return errors


def validate_summaries(record: dict, prefix: str) -> list[str]:
    """Validate subscale_summaries and check consistency with codings."""
    errors = []
    summaries = record.get("subscale_summaries", {})

    if not isinstance(summaries, dict):
        return [f"{prefix}: 'subscale_summaries' must be an object"]

    missing = REQUIRED_SUBSCALES - set(summaries.keys())
    if missing:
        errors.append(f"{prefix}: Missing subscales in summaries: {sorted(missing)}")

    for code, summary in summaries.items():
        if code not in REQUIRED_SUBSCALES:
            errors.append(f"{prefix}: Unexpected subscale in summaries: '{code}'")
            continue

        if not isinstance(summary, dict):
            errors.append(f"{prefix}: subscale_summaries['{code}'] must be an object")
            continue

        for field in ["count", "weighted_sum", "items_found"]:
            if field not in summary:
                errors.append(f"{prefix}: subscale_summaries['{code}'] missing '{field}'")

        if "count" in summary and not isinstance(summary["count"], int):
            errors.append(f"{prefix}: subscale_summaries['{code}'].count must be integer")

        if "weighted_sum" in summary and not isinstance(summary["weighted_sum"], int):
            errors.append(f"{prefix}: subscale_summaries['{code}'].weighted_sum must be integer")

        if "items_found" in summary and not isinstance(summary["items_found"], list):
            errors.append(f"{prefix}: subscale_summaries['{code}'].items_found must be array")

    # Cross-check codings vs summaries
    if isinstance(record.get("codings"), list):
        coding_counts = {}
        coding_weights = {}
        for coding in record["codings"]:
            sub = coding.get("subscale", "")
            if sub in REQUIRED_SUBSCALES:
                coding_counts[sub] = coding_counts.get(sub, 0) + 1
                coding_weights[sub] = coding_weights.get(sub, 0) + coding.get("weight", 0)

        for code in REQUIRED_SUBSCALES:
            expected_count = coding_counts.get(code, 0)
            expected_weight = coding_weights.get(code, 0)
            summary = summaries.get(code, {})
            actual_count = summary.get("count", 0)
            actual_weight = summary.get("weighted_sum", 0)

            if actual_count != expected_count:
                errors.append(
                    f"{prefix}: subscale_summaries['{code}'].count = {actual_count} "
                    f"but codings has {expected_count} entries"
                )
            if actual_weight != expected_weight:
                errors.append(
                    f"{prefix}: subscale_summaries['{code}'].weighted_sum = {actual_weight} "
                    f"but codings weights sum to {expected_weight}"
                )

    return errors


def validate_scratchpad_exclusion(record: dict, field_name: str, prefix: str) -> list[str]:
    """Validate scratchpad or exclusion_checklist structure."""
    errors = []
    field_data = record.get(field_name, {})

    if not isinstance(field_data, dict):
        return [f"{prefix}: '{field_name}' must be an object"]

    flagged = set()
    if "screening" in record and isinstance(record["screening"], dict):
        flagged_list = record["screening"].get("flagged_subscales", [])
        if isinstance(flagged_list, list):
            flagged = set(flagged_list)

    if not flagged and field_data:
        errors.append(f"{prefix}: {field_name} should be empty when no subscales flagged")

    for code in flagged:
        if code not in field_data:
            errors.append(f"{prefix}: Missing {field_name} entry for flagged subscale '{code}'")
        elif not isinstance(field_data[code], dict):
            errors.append(f"{prefix}: {field_name}['{code}'] must be an object")

    unexpected = set(field_data.keys()) - flagged
    if unexpected:
        errors.append(f"{prefix}: {field_name} has entries for non-flagged subscales: {sorted(unexpected)}")

    return errors


def load_input_ids(input_path: str) -> set[str]:
    """Load all IDs from input file."""
    input_ids = set()
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            try:
                records = json.loads(content)
                if isinstance(records, list):
                    for r in records:
                        if isinstance(r, dict) and "id" in r:
                            input_ids.add(r["id"])
                    return input_ids
            except json.JSONDecodeError:
                pass
            for line in content.split("\n"):
                line = line.strip()
                if line:
                    r = json.loads(line)
                    if "id" in r:
                        input_ids.add(r["id"])
    except Exception as e:
        print(f"Warning: Could not load input IDs: {e}")
    return input_ids


def print_validation_report(is_valid: bool, errors: list[str], output_path: str):
    """Print formatted validation report."""
    print("\n" + "=" * 70)
    print(f"VALIDATION REPORT: {output_path}")
    print("=" * 70)

    if is_valid:
        print("\n  VALIDATION PASSED")
        print("  All checks completed successfully.")
    else:
        print(f"\n  VALIDATION FAILED")
        print(f"  Found {len(errors)} error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    print("\n" + "=" * 70 + "\n")


def compute_statistics(output_path: str) -> dict:
    """Compute statistics from output file."""
    stats = {
        "total_utterances": 0,
        "no_depressive_content": 0,
        "needs_analysis": 0,
        "total_codings": 0,
        "subscale_counts": {s: 0 for s in REQUIRED_SUBSCALES},
        "subscale_weights": {s: 0 for s in REQUIRED_SUBSCALES},
        "codings_per_utterance": [],
    }

    with open(output_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            stats["total_utterances"] += 1

            decision = record.get("screening", {}).get("decision")
            if decision == "no_depressive_content":
                stats["no_depressive_content"] += 1
            elif decision == "needs_analysis":
                stats["needs_analysis"] += 1

            codings = record.get("codings", [])
            n_codings = len(codings)
            stats["total_codings"] += n_codings
            stats["codings_per_utterance"].append(n_codings)

            summaries = record.get("subscale_summaries", {})
            for sub in REQUIRED_SUBSCALES:
                s = summaries.get(sub, {})
                count = s.get("count", 0)
                weight = s.get("weighted_sum", 0)
                if count > 0:
                    stats["subscale_counts"][sub] += 1
                stats["subscale_weights"][sub] += weight

    return stats


def print_statistics(stats: dict):
    """Print formatted statistics."""
    print("\n" + "=" * 70)
    print("ANALYSIS STATISTICS")
    print("=" * 70)

    n = stats["total_utterances"]
    print(f"\nTotal utterances: {n}")
    print(f"  - No depressive content: {stats['no_depressive_content']}")
    print(f"  - Needed analysis:       {stats['needs_analysis']}")
    print(f"  - Total codings:         {stats['total_codings']}")

    if stats["codings_per_utterance"]:
        cpu = stats["codings_per_utterance"]
        avg = sum(cpu) / len(cpu)
        print(f"  - Avg codings/utterance: {avg:.1f}")

    print(f"\nSubscale presence (utterances with >= 1 coding):")
    for sub in sorted(REQUIRED_SUBSCALES):
        count = stats["subscale_counts"][sub]
        weight = stats["subscale_weights"][sub]
        if count > 0:
            print(f"  {sub}: {count} utterance(s), total weight: {weight}")

    total_weight = sum(stats["subscale_weights"].values())
    print(f"\nTotal weighted depression content: {total_weight}")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <output.jsonl> [input.jsonl]")
        sys.exit(1)

    output_path = sys.argv[1]
    input_path = sys.argv[2] if len(sys.argv) > 2 else None

    is_valid, errors = validate_output_file(output_path, input_path)
    print_validation_report(is_valid, errors, output_path)

    if is_valid:
        stats = compute_statistics(output_path)
        print_statistics(stats)

    sys.exit(0 if is_valid else 1)
