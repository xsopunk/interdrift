"""
Module 6: Reporting & Aggregation Engine
Synthesizes deterministic audit metrics and LLM explanations into final_report.json.
"""

import json
from datetime import datetime
import pandas as pd


def build_final_report(
    summary_path: str = "data/processed/summary.json",
    csv_path: str = "data/processed/row_level_results_with_explanations.csv",
    output_path: str = "data/processed/final_report.json"
) -> dict:
    print(f"[InterDrift Reporter] Loading inputs from {summary_path} and {csv_path}...")
    
    # 1. Load summary metrics from Module 3
    with open(summary_path, "r") as f:
        summary_data = json.load(f)

    # 2. Load row-level audit and explanation data
    df = pd.read_csv(csv_path)

    total_txns = int(summary_data.get("total_transactions", len(df)))
    counts = summary_data.get("classification_counts", {})
    
    matched_count = int(counts.get("Matched", 0))
    leaked_count = int(counts.get("Leaked", 0))
    exception_count = int(counts.get("Exception", 0))
    flagged_count = int(counts.get("Flagged_For_Review", 0))

    # Extract structural audit amounts
    batch_audits = summary_data.get("batch_structural_audits", {})
    r11_audit = batch_audits.get("R11_blended_mdr_spread", {})
    r12_audit = batch_audits.get("R12_mcc_misclassification", {})

    structural_overcharge = float(r11_audit.get("structural_overcharge_delta", 0.0))
    mcc_misclassification = float(r12_audit.get("financial_impact_delta", 0.0))
    row_leakage = float(summary_data.get("total_row_leakage_inr", 0.0))
    
    # Total leaked encompasses row leakage + batch structural overcharge
    total_leaked_sum = round(row_leakage + structural_overcharge + mcc_misclassification, 2)

    # Calculate exact percentages for frontend dashboard
    overview = {
        "total_transactions": total_txns,
        "matched_count": matched_count,
        "matched_percent": round((matched_count / total_txns * 100), 2) if total_txns else 0.0,
        "leaked_count": leaked_count,
        "leaked_percent": round((leaked_count / total_txns * 100), 2) if total_txns else 0.0,
        "exception_count": exception_count,
        "exception_percent": round((exception_count / total_txns * 100), 2) if total_txns else 0.0,
        "flagged_for_review_count": flagged_count,
        "flagged_for_review_percent": round((flagged_count / total_txns * 100), 2) if total_txns else 0.0,
        "total_leaked_amount": total_leaked_sum,
        "structural_overcharge_amount": structural_overcharge,
        "mcc_misclassification_amount": mcc_misclassification
    }

    # 3. Build leak_by_category breakdown
    leaked_df = df[df["classification"] == "Leaked"].copy()
    leak_by_category = []

    if not leaked_df.empty:
        category_col = "matched_rule_id" if "matched_rule_id" in leaked_df.columns else "injected_issue"
        grouped = leaked_df.groupby(category_col).agg(
            total_leaked=("delta", "sum"),
            transaction_count=("transaction_id", "count")
        ).reset_index()

        for _, row in grouped.iterrows():
            leak_by_category.append({
                "category": str(row[category_col]),
                "total_leaked": round(float(row["total_leaked"]), 2),
                "transaction_count": int(row["transaction_count"])
            })
        
        # Sort categories by total leaked descending
        leak_by_category = sorted(leak_by_category, key=lambda x: x["total_leaked"], reverse=True)

    # 4. Extract Top Offenders (Top 5-10 highest overcharge deltas)
    top_offenders = []
    if not leaked_df.empty:
        top_df = leaked_df.sort_values(by="delta", ascending=False).head(10)
        for _, row in top_df.iterrows():
            explanation = str(row.get("explanation", ""))
            if not explanation or pd.isna(row.get("explanation")):
                explanation = f"Statutory overcharge detected under rule {row.get('matched_rule_id', 'N/A')}."

            top_offenders.append({
                "transaction_id": str(row["transaction_id"]),
                "rule_id": str(row.get("matched_rule_id", "N/A")),
                "delta": round(float(row.get("delta", 0.0)), 2),
                "explanation": explanation
            })

    # 5. Extract Full Exceptions list (untruncated for audit integrity)
    exceptions = []
    exception_df = df[df["classification"] == "Exception"]
    for _, row in exception_df.iterrows():
        note_text = str(row.get("note", ""))
        if not note_text or pd.isna(note_text):
            note_text = "No matching rule found — check sub_instrument/mcc fields"

        exceptions.append({
            "transaction_id": str(row["transaction_id"]),
            "note": note_text
        })

    # 6. Assemble complete presentation payload
    final_report = {
        "overview": overview,
        "leak_by_category": leak_by_category,
        "top_offenders": top_offenders,
        "exceptions": exceptions,
        "audit_trail_available": True,
        "generated_at": datetime.now().isoformat()
    }

    with open(output_path, "w") as f:
        json.dump(final_report, f, indent=2)

    print(f"[InterDrift Reporter] Report successfully saved to {output_path}")
    return final_report


if __name__ == "__main__":
    build_final_report()