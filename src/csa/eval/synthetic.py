"""
Helpers for working with the synthetic test suite.

The full 150-instance suite lives at the repo root under `synthetic/`; this
module also exposes the 3 demo instances that ship inside the wheel.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

DEMO_INSTANCE_IDS: tuple[str, ...] = (
    "SYN_001_easy_hopelessness",
    "SYN_095_distractor",
    "SYN_110_denial",
)


@dataclass(frozen=True)
class DemoInstance:
    """One synthetic instance bundled inside the package, with paths to its files."""

    id: str
    transcript_path: Path
    input_jsonl_path: Path
    ground_truth_path: Path

    def transcript(self) -> str:
        return self.transcript_path.read_text(encoding="utf-8")

    def ground_truth(self) -> list[dict]:
        return [json.loads(line) for line in self.ground_truth_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def list_demo_instances() -> list[DemoInstance]:
    """Return the 3 bundled demo instances."""
    base = resources.files("csa") / "scales" / "gg_depression" / "data" / "demo"
    out: list[DemoInstance] = []
    for inst_id in DEMO_INSTANCE_IDS:
        d = base / inst_id
        out.append(
            DemoInstance(
                id=inst_id,
                transcript_path=Path(str(d / "transcript.md")),
                input_jsonl_path=Path(str(d / "input.jsonl")),
                ground_truth_path=Path(str(d / "ground_truth.jsonl")),
            )
        )
    return out


def get_demo_instance(instance_id: str) -> DemoInstance:
    """Load one demo instance by id (e.g. `'SYN_001_easy_hopelessness'`)."""
    for inst in list_demo_instances():
        if inst.id == instance_id:
            return inst
    raise KeyError(f"Unknown demo instance: {instance_id!r}. "
                   f"Available: {DEMO_INSTANCE_IDS}")
