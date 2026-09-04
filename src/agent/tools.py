"""
Module 8.1: Agent State & Bounded Tool Interfaces
Exposes bounded, JSON-serializable tool functions for the InterDrift agent layer.
All functions strictly read from pre-computed deterministic Module 1-7 outputs.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.parse

# Default paths to fallback data files if API server is offline
REPORT_PATH = Path("data/processed/final_report.json")
SUMMARY_PATH = Path("data/processed/summary.json")
RULE_TABLE_PATH = Path("data/rules/rule_table.json")
MSA_PATH = Path("data/raw/merchant_msa.json")
EXPLANATIONS_CSV_PATH = Path("data/processed/row_level_results_with_explanations.csv")
ROW_CSV_PATH = Path("data/processed/row_level_results.csv")

API_BASE_URL = "http://127.0.0.1:8000"


def _http_get(endpoint: str) -> Optional[Dict[str, Any]]:
    """Helper to query local FastAPI backend endpoint."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        req = urllib.request.Request(url, headers={"User-Agent": "InterDriftAgent/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def get_audit_summary() -> Dict[str, Any]:
    """
    Returns aggregate audit summary & KPI metrics.
    Data Source: GET /report (or fallback data/processed/final_report.json)
    """
    data = _http_get("/report")
    if data:
        return data.get("overview", {})

    if REPORT_PATH.exists():
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("overview", {})
    return {}


def get_transaction_details(transaction_id: str) -> Dict[str, Any]:
    """
    Returns full row-level record for a single transaction ID.
    Data Source: GET /transactions/{transaction_id}
    """
    data = _http_get(f"/transactions/{urllib.parse.quote(transaction_id)}")
    if data:
        return data

    # Local fallback
    import pandas as pd
    csv_file = EXPLANATIONS_CSV_PATH if EXPLANATIONS_CSV_PATH.exists() else ROW_CSV_PATH
    if csv_file.exists():
        df = pd.read_csv(csv_file).fillna("")
        match = df[df["transaction_id"] == transaction_id]
        if not match.empty:
            rec = match.iloc[0].to_dict()
            return rec
    return {"error": f"Transaction '{transaction_id}' not found."}


def get_rule_evidence(rule_id: str) -> Dict[str, Any]:
    """
    Returns statutory rule parameters, citations, and confidence notes for a given rule_id.
    Data Source: GET /rules/{rule_id} (or fallback data/rules/rule_table.json)
    """
    data = _http_get(f"/rules/{urllib.parse.quote(rule_id)}")
    if data:
        return data

    if RULE_TABLE_PATH.exists():
        with open(RULE_TABLE_PATH, "r", encoding="utf-8") as f:
            rules_data = json.load(f)
            for r in rules_data.get("rules", []):
                if r.get("rule_id") == rule_id:
                    return {
                        "rule_id": r.get("rule_id"),
                        "category": r.get("category"),
                        "description": r.get("description"),
                        "condition": r.get("condition"),
                        "expected_fee_type": r.get("expected_fee_type"),
                        "expected_fee_value": r.get("expected_fee_value"),
                        "source_status": r.get("source_status"),
                        "source_citation": r.get("source_citation"),
                        "confidence_note": r.get("confidence_note")
                    }
    return {"error": f"Rule '{rule_id}' not found in taxonomy."}


def get_contract_terms() -> Dict[str, Any]:
    """
    Returns merchant agreement/MSA parameters (contracted rate, registered MCC, business tier).
    Data Source: GET /contract (or fallback data/raw/merchant_msa.json)
    """
    data = _http_get("/contract")
    if data:
        return data

    if MSA_PATH.exists():
        with open(MSA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_structural_audit() -> Dict[str, Any]:
    """
    Returns batch-level structural audit metrics (R11 blended MDR spread & R12 MCC misclassification impact).
    Data Source: GET /audit/structural (or fallback data/processed/summary.json)
    """
    data = _http_get("/audit/structural")
    if data:
        return data

    if SUMMARY_PATH.exists():
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            summary = json.load(f)
            return {
                "batch_structural_audits": summary.get("batch_structural_audits", {}),
                "total_row_leakage_inr": summary.get("total_row_leakage_inr", 0.0)
            }
    return {}


def get_exception_details() -> Dict[str, Any]:
    """
    Returns full list of unclassified exception transactions with reasons/notes.
    Data Source: GET /exceptions
    """
    data = _http_get("/exceptions")
    if data:
        return data

    if REPORT_PATH.exists():
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            report = json.load(f)
            exceptions = report.get("exceptions", [])
            return {"count": len(exceptions), "exceptions": exceptions}
    return {"count": 0, "exceptions": []}


def calculate_exposure(rule_id_or_category: str) -> Dict[str, Any]:
    """
    Calculates total ₹ fee delta exposure for a specific rule_id (e.g. 'R2') or category (e.g. 'RuPay_Debit').
    Data Source: GET /exposure
    """
    # Query API by rule_id first, then fallback to category
    data_rule = _http_get("/exposure?group_by=rule_id")
    if data_rule and "groups" in data_rule:
        for group in data_rule["groups"]:
            if group.get("group_key") == rule_id_or_category:
                return {
                    "query": rule_id_or_category,
                    "matched_by": "rule_id",
                    "total_exposure_inr": group.get("total_exposure_inr", 0.0),
                    "transaction_count": group.get("transaction_count", 0),
                    "transaction_ids": group.get("transaction_ids", [])
                }

    data_cat = _http_get("/exposure?group_by=category")
    if data_cat and "groups" in data_cat:
        for group in data_cat["groups"]:
            if group.get("group_key") == rule_id_or_category:
                return {
                    "query": rule_id_or_category,
                    "matched_by": "category",
                    "total_exposure_inr": group.get("total_exposure_inr", 0.0),
                    "transaction_count": group.get("transaction_count", 0),
                    "transaction_ids": group.get("transaction_ids", [])
                }

    return {
        "query": rule_id_or_category,
        "matched_by": "none",
        "total_exposure_inr": 0.0,
        "transaction_count": 0,
        "transaction_ids": []
    }


def compare_with_baseline() -> Dict[str, Any]:
    """
    Interface stub for multi-batch baseline vs current control effectiveness comparison.
    Implementation coming in Module 10.
    """
    return {
        "status": "stub",
        "message": "Baseline comparison interface stub. Implementation coming in Module 10.",
        "baseline_batch_id": None,
        "current_batch_id": None,
        "exposure_reduction_pct": 0.0
    }
