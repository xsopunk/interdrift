"""
Module 3.1: Deterministic Row Classifier
Applies transactional rules (R1-R10, R13) to classify settlement records.
"""

from typing import Dict, Any, List, Optional
import pandas as pd


TOLERANCE = 0.05  # 5 paise tolerance for floating point rounding


def evaluate_condition(row: pd.Series, condition: Dict[str, Any]) -> bool:
    """Evaluates whether a transaction satisfies a rule's criteria."""
    for field, expected_val in condition.items():
        if field == "sub_instrument":
            if str(row.get("sub_instrument", "")).strip() != str(expected_val).strip():
                return False
        elif field == "declared_instrument":
            if row.get("declared_instrument") != expected_val:
                return False
        elif field == "mcc":
            if str(row.get("mcc", "")).strip() != str(expected_val).strip():
                return False
        elif field == "turnover_tier":
            if row.get("turnover_tier") != expected_val:
                return False
        elif field == "card_tier":
            if row.get("card_tier") != expected_val:
                return False
        elif field == "tax_amount_provided":
            if bool(row.get("tax_amount_provided", True)) != bool(expected_val):
                return False
        elif field == "amount_operator":
            threshold = float(condition.get("amount_threshold", 0.0))
            amt = float(row.get("amount", 0.0))
            if expected_val == "<=" and not (amt <= threshold):
                return False
            elif expected_val == ">" and not (amt > threshold):
                return False
        elif field in ["amount_threshold", "mismatch_detected", "high_cost_rail_used", "pricing_model"]:
            continue
        else:
            if row.get(field) != expected_val:
                return False
    return True


def compute_expected_fee(row: pd.Series, rule: Dict[str, Any]) -> float:
    """Calculates statutory or benchmark base fee from rule parameters."""
    fee_type = rule.get("expected_fee_type")
    val = float(rule.get("expected_fee_value", 0.0))
    amount = float(row.get("amount", 0.0))

    if fee_type == "zero":
        return 0.0
    elif fee_type == "percentage":
        return round(amount * (val / 100.0), 2)
    elif fee_type == "capped_percentage":
        cap = float(rule.get("cap_amount", 1000.0))
        fee = amount * (val / 100.0)
        return round(min(fee, cap), 2)
    elif fee_type == "downgrade_penalty":
        # Commercial card base benchmark (2.0%) + penalty (0.80%)
        return round(amount * ((2.0 + val) / 100.0), 2)
    elif fee_type == "contract_benchmark":
        return round(amount * (val / 100.0), 2)
    return 0.0


def classify_row(row: pd.Series, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Classifies a single transaction into Matched, Leaked, Exception, or Flagged."""
    tx_id = row.get("transaction_id", "UNKNOWN")
    sub_raw = row.get("sub_instrument")
    # Honest Exception: missing sub-instrument tag prevents classification
    if pd.isna(sub_raw) or not str(sub_raw).strip() or str(sub_raw).strip().lower() in ["nan", "none"]:
        return {
            "transaction_id": tx_id,
            "classification": "Exception",
            "matched_rule_id": "NONE",
            "expected_fee": None,
            "fee_charged": float(row.get("fee_charged", 0.0)),
            "delta": None,
            "note": "Missing sub_instrument routing tag; cannot verify applicable statutory MDR."
        }
    # Find candidate rules (excluding batch-level R11/R12)
    row_rules = [r for r in rules if r["rule_id"] not in ["R11", "R12", "R13"]]
    matching_rules = [r for r in row_rules if evaluate_condition(row, r.get("condition", {}))]

    if not matching_rules:
        return {
            "transaction_id": tx_id,
            "classification": "Exception",
            "matched_rule_id": "NONE",
            "expected_fee": None,
            "fee_charged": float(row.get("fee_charged", 0.0)),
            "delta": None,
            "note": "No matching statutory rule criteria found for transaction profile."
        }

    # If multiple match, prioritize by condition specificity (most condition fields = most specific).
    # Fields like amount_threshold are auxiliary to amount_operator, not independent conditions.
    _AUX_FIELDS = {"amount_threshold", "mismatch_detected", "high_cost_rail_used", "pricing_model"}
    def _specificity(r):
        cond = r.get("condition", {})
        return sum(1 for k in cond if k not in _AUX_FIELDS)

    matching_rules.sort(key=_specificity, reverse=True)
    rule = matching_rules[0]
    expected_fee = compute_expected_fee(row, rule)
    actual_fee = float(row.get("fee_charged", 0.0))
    delta = round(actual_fee - expected_fee, 2)

    # Advisory rule
    if rule["rule_id"] == "R9":
        return {
            "transaction_id": tx_id,
            "classification": "Flagged_For_Review",
            "matched_rule_id": "R9",
            "expected_fee": expected_fee,
            "fee_charged": actual_fee,
            "delta": delta,
            "note": "Market credit card rate applied; requires bilateral MSA contract review."
        }

    # Match or Leak evaluation
    if abs(delta) <= TOLERANCE:
        return {
            "transaction_id": tx_id,
            "classification": "Matched",
            "matched_rule_id": rule["rule_id"],
            "expected_fee": expected_fee,
            "fee_charged": actual_fee,
            "delta": 0.0,
            "note": f"Accurate fee verified against {rule['rule_id']}."
        }
    else:
        return {
            "transaction_id": tx_id,
            "classification": "Leaked",
            "matched_rule_id": rule["rule_id"],
            "expected_fee": expected_fee,
            "fee_charged": actual_fee,
            "delta": delta,
            "note": f"Statutory disparity against {rule['rule_id']}: expected Rs {expected_fee:.2f}, charged Rs {actual_fee:.2f}."
        }