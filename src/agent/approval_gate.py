"""
Module 11: Human-in-the-Loop Approval Boundary
Enforces that consequential financial actions are NEVER auto-executed.
The agent may only recommend and stage — execution requires explicit human approval.

This module is the gatekeeper: no code path bypasses it for gated actions.
"""

from typing import Dict, Any, Optional
from datetime import datetime


# --- Consequential Actions (ALWAYS require human approval) ---
# These actions have real financial or contractual impact.
GATED_ACTIONS = {
    "request_mdr_refund",
    "file_regulatory_dispute",
    "renegotiate_contract_rate",
    "migrate_to_ic_plus_pricing",
    "correct_mcc_mapping",
    "enable_least_cost_routing",
    "escalate_to_acquirer",
    "supply_l2_l3_data",
}

# --- Autonomous Actions (agent can perform without human approval) ---
# These are investigation/monitoring only — no financial consequence.
AUTONOMOUS_ACTIONS = {
    "request_manual_review",
    "no_action_required",
    "audit_gateway_fee_config",  # investigation-only, no financial change
}


def is_gated_action(action: str) -> bool:
    """Returns True if this action requires human approval before execution."""
    return action in GATED_ACTIONS


def validate_action(action: str) -> Dict[str, Any]:
    """
    Validates an action and returns its approval requirements.
    Every action goes through this gate — no bypass.
    """
    if action in GATED_ACTIONS:
        return {
            "action": action,
            "human_approval_required": True,
            "auto_executable": False,
            "gate_reason": "Consequential financial action — requires explicit human approval before execution.",
        }
    elif action in AUTONOMOUS_ACTIONS:
        return {
            "action": action,
            "human_approval_required": False,
            "auto_executable": True,
            "gate_reason": "Investigation/monitoring action — no financial impact, autonomous execution permitted.",
        }
    else:
        # Unknown actions default to gated for safety
        return {
            "action": action,
            "human_approval_required": True,
            "auto_executable": False,
            "gate_reason": "Unknown action — defaulting to human approval required for safety.",
        }


def approve_case_action(case: Dict[str, Any], approver: str = "human_operator") -> Dict[str, Any]:
    """
    Records human approval on a case's recommended action.
    Returns the approval record to be attached to the case.
    Does NOT execute the action — only records the approval decision.
    """
    action = case.get("recommended_action", "")
    if not is_gated_action(action):
        return {
            "approved": True,
            "approver": "system",
            "timestamp": datetime.now().isoformat(),
            "note": "Autonomous action — no human approval needed.",
        }

    return {
        "approved": True,
        "approver": approver,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "case_id": case.get("case_id", ""),
        "note": f"Human operator approved action '{action}' for case {case.get('case_id', '')}.",
    }


def reject_case_action(case: Dict[str, Any], reason: str = "", rejector: str = "human_operator") -> Dict[str, Any]:
    """
    Records human rejection of a case's recommended action.
    """
    return {
        "approved": False,
        "rejector": rejector,
        "timestamp": datetime.now().isoformat(),
        "action": case.get("recommended_action", ""),
        "case_id": case.get("case_id", ""),
        "reason": reason or "Action rejected by human operator.",
    }


def enforce_gate(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final enforcement check before any action could theoretically execute.
    Returns a go/no-go decision with reasoning.

    This is the LAST line of defense. Even if all other checks fail,
    this function prevents auto-execution of gated actions.
    """
    action = case.get("recommended_action", "")
    status = case.get("status", "")
    approval = case.get("approval_record", {})

    # Rule 1: Gated actions MUST have human approval
    if is_gated_action(action):
        if not approval.get("approved", False):
            return {
                "execute": False,
                "reason": f"BLOCKED: Action '{action}' requires human approval. Current status: {status}.",
                "action": action,
            }
        if approval.get("approver") == "system":
            return {
                "execute": False,
                "reason": f"BLOCKED: Gated action '{action}' cannot be system-approved. Requires human operator.",
                "action": action,
            }

    # Rule 2: Case must be in correct lifecycle state
    if status not in ["AWAITING_HUMAN_APPROVAL", "MONITORING"]:
        if is_gated_action(action):
            return {
                "execute": False,
                "reason": f"BLOCKED: Case must be in AWAITING_HUMAN_APPROVAL state. Current: {status}.",
                "action": action,
            }

    return {
        "execute": True,
        "reason": "All gates passed.",
        "action": action,
    }
