"""
Module 4: InterDrift Gateway API
Exposes the deterministic settlement audit engine to web interfaces and services.

"""

import json
from pathlib import Path
import shutil
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.rules_engine.engine import run_pipeline

REPORT_FILE_PATH = Path("data/processed/final_report.json")

app = FastAPI(
    title="InterDrift Autonomous Finance Controller API",
    description="Deterministic regulatory fee auditing and margin leakage detection for Indian payment rails.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


RULE_TABLE_PATH = Path("data/rules/rule_table.json")
MSA_PATH = Path("data/raw/merchant_msa.json")
EXPLANATIONS_CSV_PATH = Path("data/processed/row_level_results_with_explanations.csv")
ROW_CSV_PATH = Path("data/processed/row_level_results.csv")


def load_rule_map():
    """Loads rule taxonomy mapping from rule_table.json."""
    if not RULE_TABLE_PATH.exists():
        return {}
    with open(RULE_TABLE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {r["rule_id"]: r for r in data.get("rules", [])}


def get_normalized_row_records():
    """
    Helper function to load row-level audit trail with complete normalized fields:
    transaction_id, classification, matched_rule_id, category, amount, fee_charged, expected_fee, delta, explanation.
    """
    csv_file = EXPLANATIONS_CSV_PATH if EXPLANATIONS_CSV_PATH.exists() else ROW_CSV_PATH
    if not csv_file.exists():
        return []

    df = pd.read_csv(csv_file).fillna("")
    rule_map = load_rule_map()
    records = []

    for row in df.to_dict(orient="records"):
        rule_id = str(row.get("matched_rule_id", "NONE"))
        rule_info = rule_map.get(rule_id, {})
        category = rule_info.get("category", "Unclassified" if rule_id == "NONE" else rule_id)

        rec = {
            **row,
            "transaction_id": str(row.get("transaction_id", "")),
            "classification": str(row.get("classification", "")),
            "matched_rule_id": rule_id,
            "category": category,
            "amount": float(row.get("amount", 0.0)) if row.get("amount") != "" else 0.0,
            "fee_charged": float(row.get("fee_charged", 0.0)) if row.get("fee_charged") != "" else 0.0,
            "expected_fee": float(row.get("expected_fee", 0.0)) if row.get("expected_fee") != "" else 0.0,
            "delta": float(row.get("delta", 0.0)) if row.get("delta") != "" else 0.0,
            "explanation": str(row.get("explanation", row.get("note", "")))
        }
        records.append(rec)

    return records


@app.get("/health")
def health_check():
    """Health check endpoint to verify server availability."""
    return {"status": "ok", "service": "InterDrift API", "version": "1.0.0"}


@app.post("/upload")
async def upload_settlement_batch(file: UploadFile = File(...)):
    """
    Accepts settlement CSV batch, saves to disk, and triggers full audit pipeline.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only CSV files are supported.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / file.filename

    # Save uploaded file safely
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Execute deterministic audit pipeline
    try:
        summary = run_pipeline(data_path=str(target_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit engine execution failed: {str(e)}")

    return {
        "status": "success",
        "filename": file.filename,
        "rows_processed": summary["total_transactions"],
        "accuracy_rate_pct": summary["accuracy_rate_pct"],
        "total_leakage_detected_inr": summary["total_row_leakage_inr"],
        "message": "Audit completed successfully."
    }


@app.get("/results")
def get_audit_results():
    """
    Returns the latest aggregate summary and normalized row-level classification dataset.
    """
    summary_file = PROCESSED_DIR / "summary.json"
    if not summary_file.exists():
        raise HTTPException(
            status_code=404,
            detail="No processed audit results found. Please upload a settlement batch via /upload first."
        )

    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)

    records = get_normalized_row_records()

    return {
        "summary": summary,
        "row_level_results": records
    }


@app.get("/report")
def get_final_report():
    """
    Returns the synthesized audit report for dashboard visualization.
    """
    if not REPORT_FILE_PATH.exists():
        raise HTTPException(
            status_code=404, 
            detail="Final report not found. Please run the audit and reporting pipeline first."
        )
    with open(REPORT_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/transactions/{transaction_id}")
def get_transaction_detail(transaction_id: str):
    """
    Capability 2: Single transaction detail lookup by transaction_id.
    """
    records = get_normalized_row_records()
    for rec in records:
        if rec["transaction_id"] == transaction_id:
            return rec
    raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")


@app.get("/rules")
def get_all_rules():
    """
    Capability 3: List all rules from the rule table taxonomy.
    """
    if not RULE_TABLE_PATH.exists():
        raise HTTPException(status_code=404, detail="Rule table file not found.")
    with open(RULE_TABLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/rules/{rule_id}")
def get_rule_evidence(rule_id: str):
    """
    Capability 3: Rule evidence lookup by rule_id (returns condition, source_status, source_citation, confidence_note).
    """
    rule_map = load_rule_map()
    if rule_id not in rule_map:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found in rule table.")
    rule = rule_map[rule_id]
    return {
        "rule_id": rule.get("rule_id"),
        "category": rule.get("category"),
        "description": rule.get("description"),
        "condition": rule.get("condition"),
        "expected_fee_type": rule.get("expected_fee_type"),
        "expected_fee_value": rule.get("expected_fee_value"),
        "source_status": rule.get("source_status"),
        "source_citation": rule.get("source_citation"),
        "confidence_note": rule.get("confidence_note")
    }


@app.get("/contract")
def get_contract_terms():
    """
    Capability 4: Contract / MSA terms lookup from synthetic MSA.
    """
    if not MSA_PATH.exists():
        raise HTTPException(status_code=404, detail="Merchant MSA contract file not found.")
    with open(MSA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/audit/structural")
def get_structural_audit():
    """
    Capability 5: Structural / batch-level audit results (R11 & R12 aggregate metrics).
    """
    summary_file = PROCESSED_DIR / "summary.json"
    if not summary_file.exists():
        raise HTTPException(status_code=404, detail="Summary results not found.")
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
    return {
        "batch_structural_audits": summary.get("batch_structural_audits", {}),
        "total_row_leakage_inr": summary.get("total_row_leakage_inr", 0.0)
    }


@app.get("/exceptions")
def get_exceptions():
    """
    Capability 6: Exception list (unclassified / missing tag transactions).
    """
    records = get_normalized_row_records()
    exceptions = [r for r in records if r.get("classification") == "Exception"]
    return {
        "count": len(exceptions),
        "exceptions": exceptions
    }


@app.get("/exposure")
def get_exposure_calculation(group_by: str = "rule_id"):
    """
    Capability 7: Exposure calculation by rule_id or category (sum of delta grouped by key).
    """
    records = get_normalized_row_records()
    leaked = [r for r in records if r.get("classification") == "Leaked"]
    
    group_map = {}
    for r in leaked:
        key = r.get("matched_rule_id" if group_by == "rule_id" else "category", "Unknown")
        if key not in group_map:
            group_map[key] = {
                "group_key": key,
                "total_exposure_inr": 0.0,
                "transaction_count": 0,
                "transaction_ids": []
            }
        group_map[key]["total_exposure_inr"] += r.get("delta", 0.0)
        group_map[key]["transaction_count"] += 1
        group_map[key]["transaction_ids"].append(r.get("transaction_id"))

    # Round exposure amounts
    result = []
    for k, v in group_map.items():
        v["total_exposure_inr"] = round(v["total_exposure_inr"], 2)
        result.append(v)

    # Sort descending by exposure
    result = sorted(result, key=lambda x: x["total_exposure_inr"], reverse=True)

    return {
        "group_by": group_by,
        "total_leaked_inr": round(sum(r["total_exposure_inr"] for r in result), 2),
        "groups": result
    }