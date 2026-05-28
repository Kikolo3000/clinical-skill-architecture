"""
End-to-end evaluation: ground-truth dir + predicted-output dir → MetricsReport.

The MetricsReport renders a clean text table when printed and exposes every
underlying number programmatically (`.hierarchical`, `.per_subscale`, etc.)
for plotting in notebooks.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from csa.eval.matcher import match_codings
from csa.eval.metrics import binomial_ci, cohens_kappa, weighted_kappa
from csa.schemas import SUBSCALES, Subscale


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _load_jsonl(path: Path) -> dict[str, dict]:
    """Load fragment records from `path`, indexed by id.

    Accepts two formats:
    - JSONL: one fragment record per line, each with a top-level "id".
    - JSON: a single ScoringResult dump (as written by `csa-score --json`),
      whose `fragments` list contains the per-fragment records.
    """
    text = path.read_text(encoding="utf-8").strip()
    out: dict[str, dict] = {}
    if text.startswith("{") and "\n" in text and text.endswith("}"):
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = None
        if isinstance(obj, dict) and isinstance(obj.get("fragments"), list):
            for rec in obj["fragments"]:
                if "id" in rec:
                    out[rec["id"]] = rec
            return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        out[rec["id"]] = rec
    return out


# ---------------------------------------------------------------------------
# Per-instance evaluation
# ---------------------------------------------------------------------------


def evaluate_instance(gt_record: dict, pred_record: dict) -> dict:
    """Compare predicted vs ground-truth codings for one instance."""
    gt_codings = gt_record.get("codings", [])
    pred_codings = pred_record.get("codings", [])
    matches = match_codings(gt_codings, pred_codings)

    tp = sum(1 for m in matches if m["match_type"] == "tp")
    fn = sum(1 for m in matches if m["match_type"] == "fn")
    fp = sum(1 for m in matches if m["match_type"] == "fp")

    subscale_correct = 0
    sub_item_correct = 0
    perspective_correct = 0
    weight_correct = 0
    subscale_pairs: list[tuple[str, str]] = []
    weight_pairs: list[tuple[int, int]] = []

    for m in matches:
        if m["match_type"] != "tp":
            continue
        gt_c = m["gt_coding"] or {}
        pr_c = m["pred_coding"] or {}
        gt_sub = gt_c.get("subscale", "")
        pr_sub = pr_c.get("subscale", "")
        subscale_pairs.append((gt_sub, pr_sub))

        if gt_sub == pr_sub:
            subscale_correct += 1
            if gt_c.get("sub_item") == pr_c.get("sub_item"):
                sub_item_correct += 1
                if gt_c.get("perspective") == pr_c.get("perspective"):
                    perspective_correct += 1
                    weight_pairs.append((int(gt_c.get("weight", 0)), int(pr_c.get("weight", 0))))
                    if gt_c.get("weight") == pr_c.get("weight"):
                        weight_correct += 1

    return {
        "id": gt_record.get("id", ""),
        "gt_decision": gt_record.get("screening", {}).get("decision", ""),
        "pred_decision": pred_record.get("screening", {}).get("decision", ""),
        "decision_correct": (
            gt_record.get("screening", {}).get("decision")
            == pred_record.get("screening", {}).get("decision")
        ),
        "matches": matches,
        "tp": tp, "fn": fn, "fp": fp,
        "subscale_correct": subscale_correct,
        "sub_item_correct": sub_item_correct,
        "perspective_correct": perspective_correct,
        "weight_correct": weight_correct,
        "subscale_pairs": subscale_pairs,
        "weight_pairs": weight_pairs,
        "gt_n_codings": len(gt_codings),
        "pred_n_codings": len(pred_codings),
    }


# ---------------------------------------------------------------------------
# Aggregate report dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PerSubscale:
    subscale: Subscale
    tp: int
    fn: int
    fp: int
    sensitivity: float
    sensitivity_ci: tuple[float, float]
    precision: float
    f1: float
    n_gt: int


@dataclass(frozen=True)
class HierarchicalLevel:
    correct: int
    total: int
    accuracy: float


@dataclass
class MetricsReport:
    n_instances: int
    n_gt_codings: int
    decision_accuracy: float
    detection_tp: int
    detection_fn: int
    detection_fp: int
    detection_sensitivity: float
    detection_sensitivity_ci: tuple[float, float]
    detection_precision: float
    detection_f1: float
    hierarchical: dict[str, HierarchicalLevel]
    per_subscale: dict[Subscale, PerSubscale] = field(default_factory=dict)
    subscale_confusion: dict[str, int] = field(default_factory=dict)
    binary_kappa: float = 0.0
    weighted_kappa: float = 0.0

    def to_dict(self) -> dict:
        return {
            "n_instances": self.n_instances,
            "n_gt_codings": self.n_gt_codings,
            "decision_accuracy": self.decision_accuracy,
            "detection": {
                "tp": self.detection_tp, "fn": self.detection_fn, "fp": self.detection_fp,
                "sensitivity": self.detection_sensitivity,
                "sensitivity_ci": list(self.detection_sensitivity_ci),
                "precision": self.detection_precision,
                "f1": self.detection_f1,
            },
            "hierarchical": {
                level: {"correct": h.correct, "total": h.total, "accuracy": h.accuracy}
                for level, h in self.hierarchical.items()
            },
            "per_subscale": {
                sub: {
                    "tp": p.tp, "fn": p.fn, "fp": p.fp,
                    "sensitivity": p.sensitivity,
                    "sensitivity_ci": list(p.sensitivity_ci),
                    "precision": p.precision, "f1": p.f1, "n_gt": p.n_gt,
                }
                for sub, p in self.per_subscale.items()
            },
            "subscale_confusion": dict(self.subscale_confusion),
            "binary_kappa": self.binary_kappa,
            "weighted_kappa": self.weighted_kappa,
        }

    def __str__(self) -> str:  # noqa: D401 — clean tabular summary
        lines: list[str] = []
        lines.append("=" * 72)
        lines.append(f" Gottschalk-Gleser Evaluation Report — {self.n_instances} instances")
        lines.append("=" * 72)
        lines.append(f"  Decision accuracy:        {self.decision_accuracy:6.3f}")
        lines.append(f"  Clause-level F1:          {self.detection_f1:6.3f}")
        sens_lo, sens_hi = self.detection_sensitivity_ci
        lines.append(
            f"  Sensitivity:              {self.detection_sensitivity:6.3f} "
            f"({sens_lo:.3f}, {sens_hi:.3f})"
        )
        lines.append(f"  Precision:                {self.detection_precision:6.3f}")
        lines.append(f"  Cohen's kappa:            {self.binary_kappa:6.3f}")
        lines.append(f"  Weighted kappa (weights): {self.weighted_kappa:6.3f}")
        lines.append("")
        lines.append("  Hierarchical attribution (conditional on previous level):")
        for level, h in self.hierarchical.items():
            lines.append(
                f"    {level:32s} {h.correct:4d} / {h.total:4d}  ({h.accuracy:5.3f})"
            )
        lines.append("")
        lines.append("  Per-subscale F1:")
        for sub, p in self.per_subscale.items():
            lines.append(
                f"    {sub}: F1={p.f1:5.3f}  sens={p.sensitivity:5.3f}  "
                f"prec={p.precision:5.3f}  (n_gt={p.n_gt})"
            )
        lines.append("=" * 72)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _aggregate(instance_results: list[dict]) -> MetricsReport:
    total_tp = sum(r["tp"] for r in instance_results)
    total_fn = sum(r["fn"] for r in instance_results)
    total_fp = sum(r["fp"] for r in instance_results)
    total_gt = sum(r["gt_n_codings"] for r in instance_results)
    n_inst = len(instance_results)

    sens = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    f1 = 2 * prec * sens / (prec + sens) if (prec + sens) > 0 else 0.0
    sens_ci = binomial_ci(total_tp, total_tp + total_fn)
    decision_acc = (
        sum(1 for r in instance_results if r["decision_correct"]) / n_inst if n_inst else 0.0
    )

    sub_correct = sum(r["subscale_correct"] for r in instance_results)
    item_correct = sum(r["sub_item_correct"] for r in instance_results)
    persp_correct = sum(r["perspective_correct"] for r in instance_results)
    weight_correct = sum(r["weight_correct"] for r in instance_results)

    hierarchical: dict[str, HierarchicalLevel] = {
        "subscale_given_detection":
            HierarchicalLevel(sub_correct, total_tp, sub_correct / total_tp if total_tp else 0.0),
        "sub_item_given_subscale":
            HierarchicalLevel(item_correct, sub_correct, item_correct / sub_correct if sub_correct else 0.0),
        "perspective_given_sub_item":
            HierarchicalLevel(persp_correct, item_correct, persp_correct / item_correct if item_correct else 0.0),
        "weight_given_perspective":
            HierarchicalLevel(weight_correct, persp_correct, weight_correct / persp_correct if persp_correct else 0.0),
    }

    per_subscale: dict[Subscale, PerSubscale] = {}
    for sub in SUBSCALES:
        s_tp = s_fn = s_fp = 0
        for r in instance_results:
            for m in r["matches"]:
                t = m["match_type"]
                if t == "tp":
                    if (m["gt_coding"] or {}).get("subscale") == sub:
                        if (m["pred_coding"] or {}).get("subscale") == sub:
                            s_tp += 1
                        else:
                            s_fn += 1
                elif t == "fn":
                    if (m["gt_coding"] or {}).get("subscale") == sub:
                        s_fn += 1
                elif t == "fp":
                    if (m["pred_coding"] or {}).get("subscale") == sub:
                        s_fp += 1
        s_sens = s_tp / (s_tp + s_fn) if (s_tp + s_fn) > 0 else 0.0
        s_prec = s_tp / (s_tp + s_fp) if (s_tp + s_fp) > 0 else 0.0
        s_f1 = 2 * s_prec * s_sens / (s_prec + s_sens) if (s_prec + s_sens) > 0 else 0.0
        per_subscale[sub] = PerSubscale(
            subscale=sub, tp=s_tp, fn=s_fn, fp=s_fp,
            sensitivity=s_sens, sensitivity_ci=binomial_ci(s_tp, s_tp + s_fn),
            precision=s_prec, f1=s_f1, n_gt=s_tp + s_fn,
        )

    confusion: Counter = Counter()
    for r in instance_results:
        for gt_sub, pr_sub in r["subscale_pairs"]:
            confusion[(gt_sub, pr_sub)] += 1

    weight_confusion: Counter = Counter()
    all_weights: list[int] = []
    for r in instance_results:
        for gt_w, pr_w in r["weight_pairs"]:
            weight_confusion[(gt_w, pr_w)] += 1
            all_weights.extend([gt_w, pr_w])

    wk = weighted_kappa(weight_confusion, all_weights) if all_weights else 0.0
    bk = cohens_kappa(total_tp, total_fp, total_fn, 0)

    return MetricsReport(
        n_instances=n_inst,
        n_gt_codings=total_gt,
        decision_accuracy=decision_acc,
        detection_tp=total_tp,
        detection_fn=total_fn,
        detection_fp=total_fp,
        detection_sensitivity=sens,
        detection_sensitivity_ci=sens_ci,
        detection_precision=prec,
        detection_f1=f1,
        hierarchical=hierarchical,
        per_subscale=per_subscale,
        subscale_confusion={f"{gt}->{pr}": c for (gt, pr), c in sorted(confusion.items())},
        binary_kappa=bk,
        weighted_kappa=wk,
    )


# ---------------------------------------------------------------------------
# Public entrypoints
# ---------------------------------------------------------------------------


def evaluate_run(
    gt_dir: str | Path,
    pred_dir: str | Path,
    *,
    gt_filename: str = "ground_truth.jsonl",
    pred_filename: str = "output.jsonl",
) -> MetricsReport:
    """
    Compare every instance under `gt_dir/<id>/<gt_filename>` against
    `pred_dir/<id>/<pred_filename>`. Returns an aggregated `MetricsReport`.
    """
    gt_root = Path(gt_dir)
    pred_root = Path(pred_dir)
    instance_dirs = sorted(d for d in gt_root.iterdir() if d.is_dir())

    instance_results: list[dict] = []
    for d in instance_dirs:
        gt_path = d / gt_filename
        pred_path = pred_root / d.name / pred_filename
        if not gt_path.exists() or not pred_path.exists():
            continue
        gt = _load_jsonl(gt_path)
        pred = _load_jsonl(pred_path)
        gt_records = list(gt.values())
        pred_records = list(pred.values())
        # Prefer matching by id; if no ids overlap (e.g. agent used a default
        # id_prefix while GT used the instance-specific one), fall back to
        # positional pairing as long as the fragment counts match.
        id_overlap = set(gt.keys()) & set(pred.keys())
        if id_overlap:
            for inst_id in id_overlap:
                instance_results.append(evaluate_instance(gt[inst_id], pred[inst_id]))
        elif len(gt_records) == len(pred_records):
            for gt_rec, pred_rec in zip(gt_records, pred_records):
                instance_results.append(evaluate_instance(gt_rec, pred_rec))

    return _aggregate(instance_results)


def compare_runs(
    run_a: str | Path,
    run_b: str | Path,
    *,
    filename: str = "output.jsonl",
) -> float:
    """
    Cohen's kappa of clause-level coded/not-coded decisions between any two
    runs. Use to compare two human raters or two model runs.
    """
    a_root = Path(run_a)
    b_root = Path(run_b)
    inst_dirs = sorted(d for d in a_root.iterdir() if d.is_dir())
    tp = fn = fp = 0
    for d in inst_dirs:
        path_a = d / filename
        path_b = b_root / d.name / filename
        if not path_a.exists() or not path_b.exists():
            continue
        a_recs = _load_jsonl(path_a)
        b_recs = _load_jsonl(path_b)
        for inst_id, a_rec in a_recs.items():
            b_rec = b_recs.get(inst_id)
            if b_rec is None:
                continue
            matches = match_codings(a_rec.get("codings", []), b_rec.get("codings", []))
            tp += sum(1 for m in matches if m["match_type"] == "tp")
            fn += sum(1 for m in matches if m["match_type"] == "fn")
            fp += sum(1 for m in matches if m["match_type"] == "fp")
    return cohens_kappa(tp, fp, fn, 0)
