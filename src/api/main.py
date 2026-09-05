"""
Module 4: InterDrift Gateway API
Exposes the deterministic settlement audit engine to web interfaces and services.

"""

import json
from pathlib import Path
import shutil
from typing import Optional, Dict, Any, List
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.rules_engine.engine import run_pipeline
from src.data_generation.generate_settlement_data import generate_dataset, generate_msa
from src.agent.control_case import get_all_cases, get_case, update_case_status, get_cases_summary
from src.agent.approval_gate import validate_action, approve_case_action, reject_case_action, enforce_gate
from src.agent.baseline import capture_baseline, get_baseline, compute_effectiveness
from src.agent.orchestrator import run_agent_pipeline

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
ACTIVE_MSA_PATH = Path("data/raw/custom_merchant_msa.json")
ACTIVE_CSV_PATH = Path("data/raw/custom_settlement_batch.csv")
EXPLANATIONS_CSV_PATH = Path("data/processed/row_level_results_with_explanations.csv")
ROW_CSV_PATH = Path("data/processed/row_level_results.csv")

REQUIRED_CSV_COLUMNS = ["transaction_id", "amount", "declared_instrument", "sub_instrument", "fee_charged"]


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
            "rule_description": rule_info.get("description", ""),
            "source_status": rule_info.get("source_status", "sourced"),
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

    # Execute Agent Orchestrator Pipeline (Module 14: Integration Wiring)
    try:
        print(f"[Integration] Triggering Agent Pipeline for {file.filename}...")
        agent_result = run_agent_pipeline(
            skip_llm=False,
            use_cache=True,
            capture_baseline_snapshot=False
        )
        print(f"[Integration] Agent Pipeline complete. Actionable cases: {agent_result.get('case_summary', {}).get('actionable_count', 0)}")
    except Exception as e:
        print(f"[Warning] Agent pipeline execution failed: {str(e)}")
        # We don't fail the whole upload if the agent fails; graceful degradation.

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
    Capability 4: Contract / MSA terms lookup from active synthetic MSA.
    """
    target = ACTIVE_MSA_PATH if ACTIVE_MSA_PATH.exists() else MSA_PATH
    if not target.exists():
        raise HTTPException(status_code=404, detail="Merchant MSA contract file not found.")
    with open(target, "r", encoding="utf-8") as f:
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


# ============================================================
# Agent Case Management Endpoints (Module 9 + Module 11)
# ============================================================

@app.get("/cases")
def list_cases():
    """
    Returns all control cases with summary statistics.
    """
    cases = get_all_cases()
    summary = get_cases_summary()
    return {
        "summary": summary,
        "cases": cases,
    }


@app.get("/cases/{case_id}")
def get_case_detail(case_id: str):
    """
    Returns a single control case by ID.
    """
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")

    # Enrich with gate validation
    gate_check = enforce_gate(case)
    return {
        **case,
        "gate_status": gate_check,
    }


@app.post("/cases/{case_id}/approve")
def approve_case(case_id: str):
    """
    Human approves a case's recommended action.
    Transitions case from AWAITING_HUMAN_APPROVAL to MONITORING.
    """
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")

    action_validation = validate_action(case.get("recommended_action", ""))
    if not action_validation.get("human_approval_required"):
        return {"message": "This action does not require human approval.", "case_id": case_id}

    if case.get("status") != "AWAITING_HUMAN_APPROVAL":
        raise HTTPException(
            status_code=400,
            detail=f"Case must be in AWAITING_HUMAN_APPROVAL status. Current: {case.get('status')}"
        )

    # Record approval and transition
    approval = approve_case_action(case)
    updated = update_case_status(case_id, "MONITORING", reason="Human operator approved recommended action.")
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update case status.")

    return {
        "message": "Action approved. Case moved to MONITORING.",
        "case_id": case_id,
        "approval_record": approval,
    }


@app.post("/cases/{case_id}/reject")
def reject_case(case_id: str, reason: str = "Rejected by operator"):
    """
    Human rejects a case's recommended action.
    Transitions case back to INVESTIGATING for re-evaluation.
    """
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")

    if case.get("status") != "AWAITING_HUMAN_APPROVAL":
        raise HTTPException(
            status_code=400,
            detail=f"Case must be in AWAITING_HUMAN_APPROVAL status. Current: {case.get('status')}"
        )

    rejection = reject_case_action(case, reason=reason)
    # Transition back to INVESTIGATING requires going through valid transitions
    # AWAITING_HUMAN_APPROVAL -> ESCALATED -> INVESTIGATING
    updated = update_case_status(case_id, "ESCALATED", reason=reason)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update case status.")

    return {
        "message": "Action rejected. Case escalated for re-investigation.",
        "case_id": case_id,
        "rejection_record": rejection,
    }


# ============================================================
# Baseline & Control Effectiveness Endpoints (Module 10)
# ============================================================

@app.post("/baseline/capture")
def capture_baseline_snapshot(source_label: str = "batch_1"):
    """
    Captures current audit metrics as the baseline snapshot.
    Call this after the first batch is fully processed.
    """
    snapshot = capture_baseline(source_label=source_label)
    if not snapshot:
        raise HTTPException(status_code=400, detail="No report available to snapshot.")
    return {"message": "Baseline captured.", "snapshot": snapshot}


@app.get("/baseline")
def get_baseline_snapshot():
    """
    Returns the saved baseline snapshot.
    """
    baseline = get_baseline()
    if not baseline:
        return {"status": "no_baseline", "message": "No baseline captured yet."}
    return baseline


@app.get("/effectiveness")
def get_control_effectiveness():
    """
    Compares current batch metrics against saved baseline.
    Returns % reduction per metric and overall verdict.
    """
    return compute_effectiveness()


# ============================================================
# Agent Orchestrator Endpoint (Module 13)
# ============================================================

@app.post("/agent/run")
def trigger_agent_pipeline(
    skip_llm: bool = False,
    capture_baseline: bool = False,
    source_label: str = "batch",
):
    """
    Triggers the full agent pipeline:
    Grouping → Prioritization → LLM Reasoning → Case Creation → Effectiveness.

    Args:
        skip_llm: Skip Gemini calls (use fallback diagnosis).
        capture_baseline: Save current metrics as baseline before analysis.
        source_label: Label for the baseline snapshot.
    """
    result = run_agent_pipeline(
        skip_llm=skip_llm,
        use_cache=True,
        capture_baseline_snapshot=capture_baseline,
        source_label=source_label,
    )
    return result


# ============================================================
# Test Data Generation & Ingestion Endpoints (Capability 15)
# ============================================================

class DatasetPreviewRequest(BaseModel):
    num_transactions: int = 500
    min_amount: float = 50.0
    max_amount: float = 100000.0
    rupay_credit_leak_rate: float = 0.15
    l2_l3_downgrade_rate: float = 0.12
    mcc_misclass_rate: float = 0.10
    exception_rate: float = 0.05
    msa: Optional[Dict[str, Any]] = None


class MSAPreviewRequest(BaseModel):
    merchant_id: Optional[str] = None
    merchant_name: Optional[str] = None
    business_category: Optional[str] = None
    registered_business_type: Optional[str] = None
    expected_mcc: Optional[str] = None
    annual_turnover_tier: Optional[str] = None
    contracted_flat_rate: Optional[float] = None
    cards_flat_blended: Optional[float] = None
    tax_rate_gst: Optional[float] = None


class ActivateAuditRequest(BaseModel):
    dataset_mode: str = "default"  # "generated" | "uploaded" | "default"
    dataset_config: Optional[Dict[str, Any]] = None
    uploaded_csv_filename: Optional[str] = None
    msa_mode: str = "default"  # "generated" | "uploaded" | "default"
    msa_data: Optional[Dict[str, Any]] = None


@app.post("/api/generate/dataset/preview")
def preview_generated_dataset(req: DatasetPreviewRequest):
    """
    Generates synthetic settlement dataset preview and summary metrics without running the audit.
    """
    try:
        config = req.dict(exclude={"msa"})
        df = generate_dataset(config=config, msa=req.msa)
        summary = {
            "total_records": len(df),
            "total_volume_inr": round(float(df["amount"].sum()), 2),
            "min_amount": float(df["amount"].min()) if not df.empty else 0.0,
            "max_amount": float(df["amount"].max()) if not df.empty else 0.0,
            "avg_amount": round(float(df["amount"].mean()), 2) if not df.empty else 0.0,
            "issues_breakdown": df["injected_issue"].value_counts().to_dict() if not df.empty else {}
        }
        return {
            "status": "success",
            "summary": summary,
            "columns": list(df.columns),
            "preview_rows": df.head(25).fillna("").to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dataset preview: {str(e)}")


@app.post("/api/generate/msa/preview")
def preview_generated_msa(req: MSAPreviewRequest):
    """
    Generates synthetic Merchant Service Agreement (MSA) preview based on configuration.
    """
    try:
        config = {k: v for k, v in req.dict().items() if v is not None}
        msa = generate_msa(config)
        return {
            "status": "success",
            "msa": msa
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate MSA preview: {str(e)}")


@app.post("/api/upload/csv")
async def upload_custom_csv(file: UploadFile = File(...)):
    """
    Uploads and validates a user settlement CSV file without triggering the full audit.
    Checks required columns and verifies that amount values are valid numbers.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Uploaded file must be a CSV (.csv).")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOAD_DIR / f"upload_{file.filename}"

    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write uploaded file: {str(e)}")

    try:
        df = pd.read_csv(target_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Unable to parse CSV: {str(e)}")

    missing_cols = [col for col in REQUIRED_CSV_COLUMNS if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=422,
            detail=f"CSV is missing required columns: {', '.join(missing_cols)}. Found columns: {', '.join(list(df.columns))}"
        )

    # Validate numeric amounts
    if not pd.to_numeric(df["amount"], errors="coerce").notnull().all():
        raise HTTPException(
            status_code=422,
            detail="The 'amount' column contains invalid non-numeric values."
        )

    return {
        "status": "success",
        "filename": target_path.name,
        "original_filename": file.filename,
        "total_rows": len(df),
        "columns": list(df.columns),
        "preview_rows": df.head(15).fillna("").to_dict(orient="records")
    }


@app.post("/api/upload/msa")
async def upload_custom_msa(file: UploadFile = File(...)):
    """
    Uploads and validates a user Merchant Service Agreement (MSA) JSON specification.
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=422, detail="Uploaded file must be a JSON file (.json).")

    try:
        content = await file.read()
        msa_data = json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON format: {str(e)}")

    required_keys = ["merchant_id", "annual_turnover_tier", "contracted_rates"]
    missing_keys = [k for k in required_keys if k not in msa_data]
    if missing_keys:
        raise HTTPException(
            status_code=422,
            detail=f"MSA JSON is missing required fields: {', '.join(missing_keys)}"
        )

    if not isinstance(msa_data.get("contracted_rates"), dict):
        raise HTTPException(
            status_code=422,
            detail="Field 'contracted_rates' must be an object with rate definitions."
        )

    return {
        "status": "success",
        "filename": file.filename,
        "msa": msa_data
    }


@app.post("/api/generate/activate")
def activate_audit_data(req: ActivateAuditRequest):
    """
    Activates custom dataset and/or MSA, runs audit engine, and triggers the agent pipeline.
    Falls back gracefully to default files if either component is missing.
    """
    notices = []
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Resolve Active MSA
    active_msa_path = MSA_PATH
    if req.msa_mode in ["generated", "uploaded"] and req.msa_data:
        try:
            with open(ACTIVE_MSA_PATH, "w", encoding="utf-8") as f:
                json.dump(req.msa_data, f, indent=2)
            active_msa_path = ACTIVE_MSA_PATH
        except Exception as e:
            notices.append(f"Failed to persist custom MSA ({str(e)}). Using default MSA.")
            active_msa_path = MSA_PATH
    else:
        # Fallback to default MSA
        if ACTIVE_MSA_PATH.exists():
            ACTIVE_MSA_PATH.unlink(missing_ok=True)
        active_msa_path = MSA_PATH
        notices.append("Using default Merchant Service Agreement (MSA).")

    # 2. Resolve Active Dataset
    active_data_path = Path("data/raw/settlement_batch_01.csv")
    if req.dataset_mode == "uploaded" and req.uploaded_csv_filename:
        candidate_path = UPLOAD_DIR / req.uploaded_csv_filename
        if candidate_path.exists():
            active_data_path = candidate_path
        else:
            notices.append(f"Uploaded file '{req.uploaded_csv_filename}' not found. Using default dataset.")
            active_data_path = Path("data/raw/settlement_batch_01.csv")
    elif req.dataset_mode == "generated" and req.dataset_config:
        try:
            with open(active_msa_path, "r", encoding="utf-8") as f:
                current_msa = json.load(f)
            df = generate_dataset(config=req.dataset_config, msa=current_msa)
            df.to_csv(ACTIVE_CSV_PATH, index=False)
            active_data_path = ACTIVE_CSV_PATH
        except Exception as e:
            notices.append(f"Dataset generation failed ({str(e)}). Using default dataset.")
            active_data_path = Path("data/raw/settlement_batch_01.csv")
    else:
        active_data_path = Path("data/raw/settlement_batch_01.csv")
        notices.append("Using default settlement transactions dataset.")

    # 3. Run Pipeline
    try:
        summary = run_pipeline(
            data_path=str(active_data_path),
            msa_path=str(active_msa_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit engine execution failed: {str(e)}")

    # 4. Trigger Agent Pipeline
    agent_summary = {}
    try:
        agent_result = run_agent_pipeline(
            skip_llm=False,
            use_cache=True,
            capture_baseline_snapshot=False
        )
        agent_summary = agent_result.get("case_summary", {})
    except Exception as e:
        print(f"[Warning] Agent pipeline execution error: {str(e)}")

    return {
        "status": "success",
        "active_data_path": str(active_data_path),
        "active_msa_path": str(active_msa_path),
        "notices": notices,
        "rows_processed": summary.get("total_transactions", 0),
        "accuracy_rate_pct": summary.get("accuracy_rate_pct", 0.0),
        "total_leakage_detected_inr": summary.get("total_row_leakage_inr", 0.0),
        "actionable_cases": agent_summary.get("actionable_count", 0),
        "message": "Audit completed successfully with active test data."
    }


class CopilotChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None


@app.post("/api/copilot/chat")
def copilot_chat(req: CopilotChatRequest):
    """
    RAG Copilot assistant answering questions grounded in live audit results.
    """
    from src.agent.copilot import ask_copilot
    return ask_copilot(message=req.message, chat_history=req.history)