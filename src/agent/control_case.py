"""
Module 9: Control Case Model
Persists agent findings as trackable, stateful cases with a defined lifecycle.

Each case maps 1:1 to an investigation group from Modules 8.2-8.4.
Persistence: simple JSON file (data/processed/control_cases.json).
No database required — hackathon-appropriate simplicity.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


CASES_FILE = Path("data/processed/control_cases.json")

# --- Status Lifecycle ---
# OPEN → INVESTIGATING → ACTION_RECOMMENDED → AWAITING_HUMAN_APPROVAL → MONITORING → IMPROVED/ESCALATED → CLOSED
VALID_STATUSES = [
    "OPEN",
    "INVESTIGATING",
    "ACTION_RECOMMENDED",
    "AWAITING_HUMAN_APPROVAL",
    "MONITORING",
    "IMPROVED",
    "ESCALATED",
    "CLOSED",
]

# Valid status transitions (from → list of allowed next statuses)
STATUS_TRANSITIONS = {
    "OPEN": ["INVESTIGATING"],
    "INVESTIGATING": ["ACTION_RECOMMENDED", "CLOSED"],
    "ACTION_RECOMMENDED": ["AWAITING_HUMAN_APPROVAL", "CLOSED"],
    "AWAITING_HUMAN_APPROVAL": ["MONITORING", "ESCALATED", "CLOSED"],
    "MONITORING": ["IMPROVED", "ESCALATED", "CLOSED"],
    "IMPROVED": ["CLOSED", "MONITORING"],
    "ESCALATED": ["INVESTIGATING", "CLOSED"],
    "CLOSED": [],
}


def _load_cases() -> List[Dict[str, Any]]:
    """Load all cases from JSON persistence."""
    if not CASES_FILE.exists():
        return []
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("cases", [])


def _save_cases(cases: List[Dict[str, Any]]):
    """Save all cases to JSON persistence."""
    CASES_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "total_cases": len(cases),
        "cases": cases,
    }
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def create_case_from_group(diagnosed_group: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a single ControlCase from a diagnosed investigation group.

    The group should already be enriched with priority (Module 8.3) and
    agent_diagnosis (Module 8.4) fields.
    """
    diagnosis = diagnosed_group.get("agent_diagnosis", {})
    has_real_diagnosis = not diagnosis.get("root_cause", "").startswith("Unable")

    # Determine initial status based on diagnosis availability
    if has_real_diagnosis and diagnosis.get("human_approval_required"):
        initial_status = "AWAITING_HUMAN_APPROVAL"
    elif has_real_diagnosis:
        initial_status = "ACTION_RECOMMENDED"
    else:
        initial_status = "INVESTIGATING"

    case = {
        # Identity
        "case_id": f"CASE_{uuid.uuid4().hex[:8].upper()}",
        "created_at": datetime.now().isoformat(),
        "last_evaluated_at": datetime.now().isoformat(),

        # Source group reference
        "group_id": diagnosed_group.get("group_id", ""),
        "group_type": diagnosed_group.get("group_type", ""),

        # Root cause & rules
        "root_cause": diagnosis.get("root_cause", "Pending investigation"),
        "rule_ids": diagnosed_group.get("rule_ids", []),
        "category": diagnosed_group.get("category", ""),
        "source_status": diagnosed_group.get("source_status", "unknown"),
        "sub_instrument": diagnosed_group.get("sub_instrument", ""),

        # Affected scope
        "affected_transactions": diagnosed_group.get("transaction_ids", []),
        "transaction_count": diagnosed_group.get("transaction_count", 0),

        # Financial impact
        "financial_exposure": diagnosed_group.get("total_exposure_inr", 0.0),

        # Confidence & priority
        "confidence": diagnosis.get("confidence_level", "low"),
        "priority_score": diagnosed_group.get("priority_score", 0.0),
        "priority_rank": diagnosed_group.get("priority_rank", 0),

        # Recommended action
        "recommended_action": diagnosis.get("recommended_action", "request_manual_review"),
        "action_rationale": diagnosis.get("action_rationale", ""),
        "human_approval_required": diagnosis.get("human_approval_required", True),

        # Status lifecycle
        "status": initial_status,
        "status_history": [
            {
                "status": initial_status,
                "timestamp": datetime.now().isoformat(),
                "reason": "Case created from agent investigation",
            }
        ],

        # Baseline metrics (populated in Module 10)
        "baseline_metric": diagnosed_group.get("total_exposure_inr", 0.0),
        "current_metric": diagnosed_group.get("total_exposure_inr", 0.0),
        "target_metric": 0.0,

        # Evidence & reasoning
        "evidence": {
            "sample_transactions": diagnosed_group.get("sample_transactions", []),
            "structural_details": diagnosed_group.get("structural_details", None),
            "priority_components": diagnosed_group.get("priority_components", {}),
            "priority_explanation": diagnosed_group.get("priority_explanation", ""),
        },
        "agent_reasoning": diagnosis.get("diagnosis", ""),
    }

    return case


def build_all_cases(diagnosed_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Creates ControlCases for all diagnosed groups and persists them.
    Replaces any existing cases (fresh build per batch).
    """
    cases = []
    for group in diagnosed_groups:
        case = create_case_from_group(group)
        cases.append(case)

    _save_cases(cases)
    print(f"[InterDrift Cases] Created {len(cases)} control cases -> {CASES_FILE}")
    return cases


def get_all_cases() -> List[Dict[str, Any]]:
    """Returns all persisted control cases."""
    return _load_cases()


def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    """Returns a single case by case_id."""
    cases = _load_cases()
    for c in cases:
        if c["case_id"] == case_id:
            return c
    return None


def update_case_status(case_id: str, new_status: str, reason: str = "") -> Optional[Dict[str, Any]]:
    """
    Transitions a case to a new status if the transition is valid.
    Returns the updated case, or None if case not found or transition invalid.
    """
    if new_status not in VALID_STATUSES:
        print(f"[Error] Invalid status: {new_status}")
        return None

    cases = _load_cases()
    for case in cases:
        if case["case_id"] == case_id:
            current = case["status"]
            allowed = STATUS_TRANSITIONS.get(current, [])
            if new_status not in allowed:
                print(f"[Error] Cannot transition {current} -> {new_status}. Allowed: {allowed}")
                return None

            case["status"] = new_status
            case["last_evaluated_at"] = datetime.now().isoformat()
            case["status_history"].append({
                "status": new_status,
                "timestamp": datetime.now().isoformat(),
                "reason": reason or f"Status updated to {new_status}",
            })

            _save_cases(cases)
            return case

    return None


def get_cases_summary() -> Dict[str, Any]:
    """Returns a dashboard-friendly summary of all cases by status."""
    cases = _load_cases()
    status_counts = {}
    for c in cases:
        s = c.get("status", "UNKNOWN")
        status_counts[s] = status_counts.get(s, 0) + 1

    total_exposure = round(sum(c.get("financial_exposure", 0) for c in cases), 2)
    actionable = [c for c in cases if c.get("status") in ["ACTION_RECOMMENDED", "AWAITING_HUMAN_APPROVAL"]]

    return {
        "total_cases": len(cases),
        "total_exposure_inr": total_exposure,
        "status_counts": status_counts,
        "actionable_count": len(actionable),
        "top_priority_case": cases[0]["case_id"] if cases else None,
    }
