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
    Returns the latest aggregate summary and row-level classification dataset.
    """
    summary_file = PROCESSED_DIR / "summary.json"
    row_file = PROCESSED_DIR / "row_level_results.csv"

    if not summary_file.exists() or not row_file.exists():
        raise HTTPException(
            status_code=404,
            detail="No processed audit results found. Please upload a settlement batch via /upload first."
        )

    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)

    # Load row-level audit trail
    df_rows = pd.read_csv(row_file)
    # Replace NaN values with empty string or None for valid JSON serialization
    df_rows = df_rows.fillna("")

    return {
        "summary": summary,
        "row_level_results": df_rows.to_dict(orient="records")
    }