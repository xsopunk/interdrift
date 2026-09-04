"""
Module 3.2: Batch-Level Structural Auditor
Evaluates macro portfolio leakages: Blended vs. IC+ spread (R11)
and MCC misclassification penalties (R12).

"""

from typing import Dict, Any
import pandas as pd


# Modeled domestic interchange baseline by card tier (Illustrative)
CARD_TIER_NETWORK_COST = {
    "basic": 0.012,             # 1.20%
    "premium_rewards": 0.018,   # 1.80%
    "corporate": 0.024          # 2.40%
}

MCC_EXPECTED_RATES = {
    "5045": 0.011,  # B2B Wholesale / Tech
    "5411": 0.018,  # Retail / Grocery
    "8220": 0.007,  # Education
    "5812": 0.016   # Restaurant
}


def audit_blended_vs_ic_plus(df: pd.DataFrame, msa: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates structural margin leakage from flat blended pricing vs underlying card cost."""
    card_txns = df[df["declared_instrument"] == "Card"].copy()
    if card_txns.empty:
        return {"total_card_volume": 0.0, "blended_overcharge": 0.0, "details": "No card transactions found."}

    flat_rate = float(msa["contracted_rates"].get("cards_flat_blended", 0.02))
    total_volume = card_txns["amount"].sum()
    
    # What the merchant would pay under their flat 2.0% blended contract:
    billed_flat_fees = round(total_volume * flat_rate, 2)

    def get_tier_cost(tier: str) -> float:
        return CARD_TIER_NETWORK_COST.get(tier, 0.015)

    card_txns["true_network_rate"] = card_txns["card_tier"].apply(get_tier_cost)
    card_txns["true_network_cost"] = card_txns["amount"] * card_txns["true_network_rate"]
    total_true_cost = round(card_txns["true_network_cost"].sum(), 2)

    # Structural overcharge = what flat rate cost them minus true IC cost
    blended_overcharge = round(max(0.0, billed_flat_fees - total_true_cost), 2)
    effective_blended_rate = flat_rate * 100
    effective_ic_rate = (total_true_cost / total_volume) * 100 if total_volume > 0 else 0.0

    return {
        "total_card_volume": round(total_volume, 2),
        "actual_flat_fees_billed": round(billed_flat_fees, 2),
        "true_underlying_network_cost": round(total_true_cost, 2),
        "structural_overcharge_delta": blended_overcharge,
        "effective_blended_rate_pct": round(effective_blended_rate, 2),
        "effective_true_rate_pct": round(effective_ic_rate, 2),
        "recommendation": "Migrate to Interchange-Plus (IC+) pricing structure to capture network rate spreads."
    }


def audit_mcc_misclassification(df: pd.DataFrame, msa: Dict[str, Any]) -> Dict[str, Any]:
    """Detects rows billed under misclassified MCC and calculates the resulting fee disparity."""
    expected_mcc = str(msa.get("expected_mcc", "5045")).strip()
    expected_rate = MCC_EXPECTED_RATES.get(expected_mcc, 0.011)

    # Detect rows where transaction MCC diverges from merchant registered category
    mismatched_mask = (df["mcc"].astype(str).str.strip() != expected_mcc) & (df["sub_instrument"] != "")
    mismatched_txns = df[mismatched_mask].copy()

    total_mismatched_count = int(len(mismatched_txns))
    if total_mismatched_count == 0:
        return {"mismatched_count": 0, "financial_impact": 0.0, "status": "No MCC misclassification detected."}

    # Financial impact = amount * (mismatched rate - expected rate)
    def calc_disparity(row):
        actual_rate = MCC_EXPECTED_RATES.get(str(row["mcc"]).strip(), 0.018)
        rate_diff = max(0.0, actual_rate - expected_rate)
        return round(row["amount"] * rate_diff, 2)

    financial_impact = round(mismatched_txns.apply(calc_disparity, axis=1).sum(), 2)

    return {
        "mismatched_count": total_mismatched_count,
        "expected_mcc": expected_mcc,
        "registered_business_type": msa.get("registered_business_type", "B2B wholesale"),
        "financial_impact_delta": financial_impact,
        "recommendation": f"Update gateway configuration to registered MCC {expected_mcc} to prevent interchange downgrades."
    }