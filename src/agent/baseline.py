"""
Module 10: Baseline & Control Effectiveness
Records audit metrics as a baseline snapshot, then computes % reduction
when a subsequent batch is processed.

Enables the agent to answer: "Did the merchant's fee leakage improve?"
No LLM calls. Pure deterministic comparison.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

BASELINE_FILE = Path("data/processed/baseline_snapshot.json")
REPORT_FILE = Path("data/processed/final_report.json")


def _load_report() -> Dict[str, Any]:
    """Load the current final report."""
    if not REPORT_FILE.exists():
        return {}
    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def capture_baseline(source_label: str = "batch_1") -> Dict[str, Any]:
    """
    Captures current audit metrics as the baseline snapshot.
    Called after the first batch is fully processed.

    Saves: total leakage, per-rule exposure, structural spread,
    matched rate, exception count, flagged count.
    """
    report = _load_report()
    if not report:
        print("[Baseline] No report found — run the engine first.")
        return {}

    overview = report.get("overview", {})
    leak_by_category = report.get("leak_by_category", {})

    snapshot = {
        "snapshot_id": f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "source_label": source_label,
        "captured_at": datetime.now().isoformat(),

        # Top-level metrics
        "total_transactions": overview.get("total_transactions", 0),
        "total_leaked_amount": overview.get("total_leaked_amount", 0.0),
        "leaked_count": overview.get("leaked_count", 0),
        "leaked_percent": overview.get("leaked_percent", 0.0),
        "matched_count": overview.get("matched_count", 0),
        "matched_percent": overview.get("matched_percent", 0.0),
        "exception_count": overview.get("exception_count", 0),
        "flagged_for_review_count": overview.get("flagged_for_review_count", 0),
        "structural_overcharge_amount": overview.get("structural_overcharge_amount", 0.0),
        "mcc_misclassification_amount": overview.get("mcc_misclassification_amount", 0.0),

        # Per-category breakdown
        "leak_by_category": leak_by_category,
    }

    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print(f"[Baseline] Snapshot saved: {snapshot['snapshot_id']} (₹{snapshot['total_leaked_amount']:,.2f} total leakage)")
    return snapshot


def get_baseline() -> Optional[Dict[str, Any]]:
    """Load the saved baseline snapshot, if it exists."""
    if not BASELINE_FILE.exists():
        return None
    with open(BASELINE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_effectiveness() -> Dict[str, Any]:
    """
    Compares current batch metrics against the saved baseline.
    Returns a control effectiveness report with % changes.

    Formula: % reduction = ((baseline - current) / baseline) × 100
    Positive = improvement (leakage went down).
    Negative = regression (leakage went up).
    """
    baseline = get_baseline()
    if not baseline:
        return {
            "status": "no_baseline",
            "message": "No baseline snapshot found. Upload a first batch to establish baseline.",
        }

    report = _load_report()
    if not report:
        return {
            "status": "no_current",
            "message": "No current report found. Run the engine on a new batch.",
        }

    current = report.get("overview", {})

    def pct_change(baseline_val: float, current_val: float) -> Optional[float]:
        """Calculate % change. Positive = improvement (reduction in leakage)."""
        if baseline_val == 0:
            return None
        return round(((baseline_val - current_val) / baseline_val) * 100, 2)

    # Core effectiveness metrics
    leaked_change = pct_change(
        baseline.get("total_leaked_amount", 0),
        current.get("total_leaked_amount", 0)
    )
    structural_change = pct_change(
        baseline.get("structural_overcharge_amount", 0),
        current.get("structural_overcharge_amount", 0)
    )
    exception_change = pct_change(
        baseline.get("exception_count", 0),
        current.get("exception_count", 0)
    )
    match_rate_delta = round(
        current.get("matched_percent", 0) - baseline.get("matched_percent", 0), 2
    )

    # Per-category comparison
    # leak_by_category is a list of {category, total_leaked, transaction_count}
    def _cats_to_dict(cats):
        if isinstance(cats, list):
            return {c.get("category", ""): c for c in cats}
        return cats if isinstance(cats, dict) else {}

    baseline_cats = _cats_to_dict(baseline.get("leak_by_category", []))
    current_cats = _cats_to_dict(report.get("leak_by_category", []))
    category_changes = {}
    all_cats = set(list(baseline_cats.keys()) + list(current_cats.keys()))
    for cat in all_cats:
        b_val = baseline_cats.get(cat, {}).get("total_leaked", 0)
        c_val = current_cats.get(cat, {}).get("total_leaked", 0)
        change = pct_change(b_val, c_val)
        category_changes[cat] = {
            "baseline_inr": b_val,
            "current_inr": c_val,
            "percent_reduction": change,
        }

    # Determine overall verdict
    if leaked_change is not None and leaked_change > 0:
        verdict = "IMPROVING"
    elif leaked_change is not None and leaked_change < 0:
        verdict = "REGRESSING"
    elif leaked_change == 0:
        verdict = "STABLE"
    else:
        verdict = "INSUFFICIENT_DATA"

    return {
        "status": "computed",
        "verdict": verdict,
        "baseline_snapshot_id": baseline.get("snapshot_id", ""),
        "baseline_captured_at": baseline.get("captured_at", ""),
        "baseline_source": baseline.get("source_label", ""),

        "metrics": {
            "total_leaked": {
                "baseline_inr": baseline.get("total_leaked_amount", 0),
                "current_inr": current.get("total_leaked_amount", 0),
                "percent_reduction": leaked_change,
            },
            "structural_overcharge": {
                "baseline_inr": baseline.get("structural_overcharge_amount", 0),
                "current_inr": current.get("structural_overcharge_amount", 0),
                "percent_reduction": structural_change,
            },
            "exception_count": {
                "baseline": baseline.get("exception_count", 0),
                "current": current.get("exception_count", 0),
                "percent_reduction": exception_change,
            },
            "match_rate": {
                "baseline_pct": baseline.get("matched_percent", 0),
                "current_pct": current.get("matched_percent", 0),
                "delta_pct": match_rate_delta,
            },
        },
        "by_category": category_changes,
    }
