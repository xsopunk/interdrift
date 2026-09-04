"""
Module 8.3: Transparent Prioritization
Ranks investigation groups using a simple, explainable weighted scoring formula.
Priority = exposure_score × confidence × recurrence × controllability

No LLM calls. No new calculations. Reads group data from Module 8.2.
Every score component is transparent and explainable in one sentence.
"""

from typing import Dict, Any, List
import math


# --- Scoring weights (tunable, but intentionally simple) ---
# These are NOT learned — they are fixed, explainable constants.

WEIGHT_EXPOSURE = 0.40       # Financial materiality
WEIGHT_CONFIDENCE = 0.25     # Source reliability (sourced vs illustrative)
WEIGHT_RECURRENCE = 0.20     # How many transactions exhibit this pattern
WEIGHT_CONTROLLABILITY = 0.15  # Can the merchant actually fix this?


# --- Controllability lookup ---
# Maps group categories to a 0-1 controllability score.
# Higher = merchant has more agency to fix it.
CONTROLLABILITY_MAP = {
    # Sourced rule violations — merchant can dispute/reclaim directly
    "Bank_UPI": 0.9,
    "RuPay_Debit": 0.9,
    "RuPay_Credit_UPI": 0.8,
    "PPI_Wallet_UPI": 0.8,
    "Debit_Non_RuPay": 0.7,
    # Structural — merchant can renegotiate pricing model
    "Blended_vs_IC_Plus": 0.7,
    "MCC_Misclassification": 0.8,
    # Credit card market rate — requires bilateral negotiation
    "Credit_Cards_Market": 0.4,
    # Commercial downgrade — requires data integration fix
    "Commercial_L2_L3_Downgrade": 0.6,
    # Routing flag — advisory only
    "Least_Cost_Routing_Flag": 0.3,
    # Exceptions — no direct action possible without more data
    "Unclassified": 0.2,
}


def _normalize_exposure(exposure_inr: float, max_exposure: float) -> float:
    """
    Normalize exposure to 0-1 scale using log scaling to prevent
    the single largest group from dominating all others.
    """
    if max_exposure <= 0 or exposure_inr <= 0:
        return 0.0
    # Log-scaled normalization: ensures Rs 40 vs Rs 5000 still produces
    # meaningful differentiation without the top group always being 1.0
    return min(math.log1p(exposure_inr) / math.log1p(max_exposure), 1.0)


def _confidence_score(source_status: str) -> float:
    """
    Maps rule source_status to a confidence multiplier.
    Sourced (legally verified) rules get full confidence.
    Illustrative (modeled) rules get reduced confidence.
    """
    return {
        "sourced": 1.0,
        "illustrative": 0.6,
        "unknown": 0.3,
        "n/a": 0.3,
    }.get(source_status, 0.3)


def _recurrence_score(transaction_count: int, total_non_matched: int) -> float:
    """
    Measures how frequently this pattern occurs relative to all flagged transactions.
    A single occurrence is less urgent than a systemic pattern.
    """
    if total_non_matched <= 0:
        return 0.0
    # Fraction of non-matched transactions in this group
    raw = transaction_count / total_non_matched
    # Apply sqrt to dampen extreme values (56/106 shouldn't be 10x more than 9/106)
    return min(math.sqrt(raw), 1.0)


def _controllability_score(category: str) -> float:
    """Returns merchant's ability to act on this finding (0-1)."""
    return CONTROLLABILITY_MAP.get(category, 0.5)


def prioritize_groups(groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scores and ranks investigation groups by transparent priority formula.

    Priority = (w1 × exposure_norm) + (w2 × confidence) + (w3 × recurrence) + (w4 × controllability)

    Returns groups sorted descending by priority_score, each enriched with:
      - priority_score: float (0-1)
      - priority_rank: int (1 = highest)
      - priority_components: dict with individual factor scores
      - priority_explanation: str (one-sentence human-readable rationale)
    """
    if not groups:
        return []

    # Compute max exposure for normalization
    max_exposure = max(g["total_exposure_inr"] for g in groups)
    total_non_matched = sum(g["transaction_count"] for g in groups)

    scored_groups = []
    for g in groups:
        exposure_norm = _normalize_exposure(g["total_exposure_inr"], max_exposure)
        confidence = _confidence_score(g.get("source_status", "unknown"))
        recurrence = _recurrence_score(g["transaction_count"], total_non_matched)
        controllability = _controllability_score(g.get("category", ""))

        priority_score = round(
            (WEIGHT_EXPOSURE * exposure_norm) +
            (WEIGHT_CONFIDENCE * confidence) +
            (WEIGHT_RECURRENCE * recurrence) +
            (WEIGHT_CONTROLLABILITY * controllability),
            4
        )

        # Build one-sentence explanation
        factors = []
        if exposure_norm > 0.5:
            factors.append(f"high exposure (Rs {g['total_exposure_inr']:,.2f})")
        elif exposure_norm > 0.2:
            factors.append(f"moderate exposure (Rs {g['total_exposure_inr']:,.2f})")
        else:
            factors.append(f"low exposure (Rs {g['total_exposure_inr']:,.2f})")

        if confidence >= 0.8:
            factors.append("legally verified rule")
        else:
            factors.append("illustrative/modeled rule")

        if recurrence > 0.3:
            factors.append(f"systemic pattern ({g['transaction_count']} transactions)")
        elif g["transaction_count"] > 0:
            factors.append(f"{g['transaction_count']} occurrences")

        explanation = f"Priority driven by {', '.join(factors)}."

        enriched = {
            **g,
            "priority_score": priority_score,
            "priority_rank": 0,  # filled after sorting
            "priority_components": {
                "exposure_normalized": round(exposure_norm, 4),
                "confidence": confidence,
                "recurrence": round(recurrence, 4),
                "controllability": controllability,
            },
            "priority_explanation": explanation,
        }
        scored_groups.append(enriched)

    # Sort descending by score
    scored_groups.sort(key=lambda x: x["priority_score"], reverse=True)

    # Assign ranks
    for i, g in enumerate(scored_groups):
        g["priority_rank"] = i + 1

    return scored_groups
