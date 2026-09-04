"""
Module 8.2: Investigation & Grouping
Groups 500 row-level audit findings into a small number of root-cause groups
for agent-level reasoning. Groups by shared rule_id + sub_instrument pattern,
plus structural/batch-level findings (R11/R12) and exception clusters.

No LLM calls. No new fee calculations. Reads exclusively from Module 8.1 tools.
"""

from typing import Dict, Any, List
from src.agent.tools import (
    get_audit_summary,
    get_exception_details,
    get_structural_audit,
    calculate_exposure,
)

# Internal imports for direct data access (read-only, no calculation)
import json
import pandas as pd
from pathlib import Path

EXPLANATIONS_CSV = Path("data/processed/row_level_results_with_explanations.csv")
ROW_CSV = Path("data/processed/row_level_results.csv")
RULE_TABLE_PATH = Path("data/rules/rule_table.json")


def _load_row_data() -> pd.DataFrame:
    """Load normalized row-level audit data."""
    csv = EXPLANATIONS_CSV if EXPLANATIONS_CSV.exists() else ROW_CSV
    return pd.read_csv(csv).fillna("")


def _load_rule_map() -> Dict[str, Dict]:
    """Load rule taxonomy for category/source_status lookups."""
    if not RULE_TABLE_PATH.exists():
        return {}
    with open(RULE_TABLE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {r["rule_id"]: r for r in data.get("rules", [])}


def build_investigation_groups() -> List[Dict[str, Any]]:
    """
    Primary grouping function. Groups all non-Matched transactions into
    root-cause groups by (classification, matched_rule_id, sub_instrument).

    Also creates synthetic groups for batch-level structural findings (R11, R12).

    Returns a list of group dicts, each containing:
      - group_id: str (e.g. "GRP_LEAKED_R2_RuPay_debit")
      - group_type: str ("row_leak" | "flagged_review" | "exception" | "structural")
      - classification: str
      - rule_ids: list[str]
      - sub_instrument: str
      - category: str (from rule_table.json)
      - source_status: str ("sourced" | "illustrative")
      - transaction_count: int
      - transaction_ids: list[str]
      - total_exposure_inr: float
      - sample_transactions: list[dict] (up to 3 representative records)
    """
    df = _load_row_data()
    rule_map = _load_rule_map()
    groups = []

    # --- 1. Row-level leaked groups (by rule_id + sub_instrument) ---
    leaked = df[df["classification"] == "Leaked"].copy()
    if not leaked.empty:
        for (rule_id, sub_inst), grp in leaked.groupby(["matched_rule_id", "sub_instrument"]):
            rule_info = rule_map.get(str(rule_id), {})
            category = rule_info.get("category", str(rule_id))
            source_status = rule_info.get("source_status", "unknown")
            txn_ids = grp["transaction_id"].tolist()
            total_delta = round(grp["delta"].sum(), 2)

            # Collect up to 3 sample transactions for LLM context
            samples = []
            for _, row in grp.head(3).iterrows():
                samples.append({
                    "transaction_id": str(row["transaction_id"]),
                    "amount": float(row.get("amount", 0)),
                    "fee_charged": float(row.get("fee_charged", 0)),
                    "expected_fee": float(row.get("expected_fee")) if row.get("expected_fee") is not None else None,
                    "delta": float(row.get("delta")) if row.get("delta") is not None else None,
                })

            groups.append({
                "group_id": f"GRP_LEAKED_{rule_id}_{sub_inst}",
                "group_type": "row_leak",
                "classification": "Leaked",
                "rule_ids": [str(rule_id)],
                "sub_instrument": str(sub_inst),
                "category": category,
                "source_status": source_status,
                "transaction_count": len(txn_ids),
                "transaction_ids": txn_ids,
                "total_exposure_inr": total_delta,
                "sample_transactions": samples,
            })

    # --- 2. Flagged-for-review groups (by rule_id) ---
    flagged = df[df["classification"] == "Flagged_For_Review"].copy()
    if not flagged.empty:
        for rule_id, grp in flagged.groupby("matched_rule_id"):
            rule_info = rule_map.get(str(rule_id), {})
            category = rule_info.get("category", str(rule_id))
            source_status = rule_info.get("source_status", "unknown")
            txn_ids = grp["transaction_id"].tolist()
            total_delta = round(grp["delta"].sum(), 2)

            samples = []
            for _, row in grp.head(3).iterrows():
                samples.append({
                    "transaction_id": str(row["transaction_id"]),
                    "amount": float(row.get("amount", 0)),
                    "fee_charged": float(row.get("fee_charged", 0)),
                    "expected_fee": float(row.get("expected_fee")) if row.get("expected_fee") is not None else None,
                    "delta": float(row.get("delta")) if row.get("delta") is not None else None,
                })

            groups.append({
                "group_id": f"GRP_FLAGGED_{rule_id}",
                "group_type": "flagged_review",
                "classification": "Flagged_For_Review",
                "rule_ids": [str(rule_id)],
                "sub_instrument": "",
                "category": category,
                "source_status": source_status,
                "transaction_count": len(txn_ids),
                "transaction_ids": txn_ids,
                "total_exposure_inr": total_delta,
                "sample_transactions": samples,
            })

    # --- 3. Exception group (all exceptions share the same root cause: missing data) ---
    exception_data = get_exception_details()
    exc_list = exception_data.get("exceptions", [])
    if exc_list:
        exc_txn_ids = [e.get("transaction_id", e.get("transaction_id", "")) for e in exc_list]
        # Pull sample records from the exception list
        samples = []
        for e in exc_list[:3]:
            tid = e.get("transaction_id", "")
            exc_row = df[df["transaction_id"] == tid]
            if not exc_row.empty:
                row = exc_row.iloc[0]
                samples.append({
                    "transaction_id": str(tid),
                    "amount": float(row.get("amount", 0)),
                    "fee_charged": float(row.get("fee_charged", 0)),
                    "expected_fee": None,
                    "delta": None,
                    "note": str(row.get("note", "")),
                })

        groups.append({
            "group_id": "GRP_EXCEPTION_MISSING_TAG",
            "group_type": "exception",
            "classification": "Exception",
            "rule_ids": ["NONE"],
            "sub_instrument": "",
            "category": "Unclassified",
            "source_status": "n/a",
            "transaction_count": len(exc_txn_ids),
            "transaction_ids": exc_txn_ids,
            "total_exposure_inr": 0.0,
            "sample_transactions": samples,
        })

    # --- 4. Structural groups (R11 blended MDR spread, R12 MCC misclassification) ---
    structural = get_structural_audit()
    batch_audits = structural.get("batch_structural_audits", {})

    r11 = batch_audits.get("R11_blended_mdr_spread", {})
    if r11:
        r11_info = rule_map.get("R11", {})
        groups.append({
            "group_id": "GRP_STRUCTURAL_R11_BLENDED_MDR",
            "group_type": "structural",
            "classification": "Structural_Leak",
            "rule_ids": ["R11"],
            "sub_instrument": "all_cards",
            "category": r11_info.get("category", "Blended_vs_IC_Plus"),
            "source_status": r11_info.get("source_status", "illustrative"),
            "transaction_count": 0,  # batch-level, not per-transaction
            "transaction_ids": [],
            "total_exposure_inr": float(r11.get("structural_overcharge_delta", 0)),
            "sample_transactions": [],
            "structural_details": {
                "total_card_volume": r11.get("total_card_volume"),
                "actual_flat_fees_billed": r11.get("actual_flat_fees_billed"),
                "true_underlying_network_cost": r11.get("true_underlying_network_cost"),
                "effective_blended_rate_pct": r11.get("effective_blended_rate_pct"),
                "effective_true_rate_pct": r11.get("effective_true_rate_pct"),
                "recommendation": r11.get("recommendation"),
            }
        })

    r12 = batch_audits.get("R12_mcc_misclassification", {})
    if r12:
        r12_info = rule_map.get("R12", {})
        groups.append({
            "group_id": "GRP_STRUCTURAL_R12_MCC_MISMATCH",
            "group_type": "structural",
            "classification": "Structural_Leak",
            "rule_ids": ["R12"],
            "sub_instrument": "",
            "category": r12_info.get("category", "MCC_Misclassification"),
            "source_status": r12_info.get("source_status", "illustrative"),
            "transaction_count": int(r12.get("mismatched_count", 0)),
            "transaction_ids": [],
            "total_exposure_inr": float(r12.get("financial_impact_delta", 0)),
            "sample_transactions": [],
            "structural_details": {
                "expected_mcc": r12.get("expected_mcc"),
                "registered_business_type": r12.get("registered_business_type"),
                "recommendation": r12.get("recommendation"),
            }
        })

    return groups


def get_group_summary(groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Returns a concise summary of all investigation groups for dashboard/logging.
    """
    total_exposure = round(sum(g["total_exposure_inr"] for g in groups), 2)
    return {
        "total_groups": len(groups),
        "total_exposure_inr": total_exposure,
        "by_type": {
            "row_leak": len([g for g in groups if g["group_type"] == "row_leak"]),
            "flagged_review": len([g for g in groups if g["group_type"] == "flagged_review"]),
            "exception": len([g for g in groups if g["group_type"] == "exception"]),
            "structural": len([g for g in groups if g["group_type"] == "structural"]),
        },
        "groups": [
            {
                "group_id": g["group_id"],
                "group_type": g["group_type"],
                "category": g["category"],
                "source_status": g["source_status"],
                "transaction_count": g["transaction_count"],
                "total_exposure_inr": g["total_exposure_inr"],
            }
            for g in groups
        ]
    }
