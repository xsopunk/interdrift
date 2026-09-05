"""
Module 6: Reporting & Aggregation Engine
Synthesizes deterministic audit metrics and grounded rule-level explanations into final_report.json.
Guarantees zero arithmetic hallucination and strict adherence to honesty constraints.
"""

import json
from datetime import datetime
from pathlib import Path
import pandas as pd


def generate_grounded_explanation(row: pd.Series) -> str:
    """
    Generates a deterministic, strictly grounded explanation for a row.
    Guarantees no false 0-fee claims for unclassified exceptions.
    """
    classification = str(row.get("classification", ""))
    rule_id = str(row.get("matched_rule_id", "NONE"))
    amount = float(row.get("amount", 0.0))
    fee_charged = float(row.get("fee_charged", 0.0))
    expected_fee = float(row.get("expected_fee", 0.0))
    delta = float(row.get("delta", 0.0))
    sub_inst = str(row.get("sub_instrument", ""))

    if classification == "Exception":
        return (
            f"Missing sub-instrument routing metadata for transaction of Rs {amount:,.2f}. "
            "Fee cannot be verified against statutory caps until gateway provides complete instrument tags."
        )

    if classification == "Flagged_For_Review":
        return (
            f"Credit card transaction of Rs {amount:,.2f} billed at flat market rate (Rs {fee_charged:,.2f}). "
            "Unverified against statutory caps; requires L2/L3 metadata or IC+ rate schedule."
        )

    if classification == "Leaked":
        return (
            f"Statutory fee overcharge of Rs {delta:,.2f} detected under rule {rule_id}. "
            f"Charged fee of Rs {fee_charged:,.2f} exceeds statutory cap/expected fee of Rs {expected_fee:,.2f}."
        )

    return f"Compliant transaction of Rs {amount:,.2f}. Billed fee matches statutory rate schedule."


def build_final_report(
    summary_path: str = "data/processed/summary.json",
    csv_path: str = "data/processed/row_level_results.csv",
    output_path: str = "data/processed/final_report.json",
    output_csv_path: str = "data/processed/row_level_results_with_explanations.csv"
) -> dict:
    print(f"[InterDrift Reporter] Loading inputs from {summary_path} and {csv_path}...")
    
    # 1. Load summary metrics from Module 3
    if not Path(summary_path).exists():
        raise FileNotFoundError(f"Summary file not found at {summary_path}")

    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)

    # 2. Load row-level audit data
    df = pd.read_csv(csv_path)

    # Generate strictly grounded explanations for all rows
    df["explanation"] = df.apply(generate_grounded_explanation, axis=1)

    # Save enriched CSV
    Path(output_csv_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv_path, index=False)

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
    
    total_leaked_sum = round(row_leakage + structural_overcharge + mcc_misclassification, 2)

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
    rules_path = Path("data/rules/rule_table.json")
    rule_map = {}
    if rules_path.exists():
        with open(rules_path, "r", encoding="utf-8") as f:
            rule_map = {r["rule_id"]: r for r in json.load(f).get("rules", [])}

    leaked_df = df[df["classification"] == "Leaked"].copy()
    leak_by_category = []

    if not leaked_df.empty:
        category_col = "matched_rule_id" if "matched_rule_id" in leaked_df.columns else "injected_issue"
        grouped = leaked_df.groupby(category_col).agg(
            total_leaked=("delta", "sum"),
            transaction_count=("transaction_id", "count")
        ).reset_index()

        for _, row in grouped.iterrows():
            rule_id = str(row[category_col])
            rule_info = rule_map.get(rule_id, {})
            leak_by_category.append({
                "category": rule_id,
                "rule_name": rule_info.get("description", rule_info.get("category", rule_id)),
                "source_status": rule_info.get("source_status", "sourced"),
                "total_leaked": round(float(row["total_leaked"]), 2),
                "transaction_count": int(row["transaction_count"])
            })
        
        leak_by_category = sorted(leak_by_category, key=lambda x: x["total_leaked"], reverse=True)

    # 4. Extract Top Offenders (Top 10 highest overcharge deltas)
    top_offenders = []
    if not leaked_df.empty:
        top_df = leaked_df.sort_values(by="delta", ascending=False).head(10)
        for _, row in top_df.iterrows():
            top_offenders.append({
                "transaction_id": str(row["transaction_id"]),
                "rule_id": str(row.get("matched_rule_id", "N/A")),
                "delta": round(float(row.get("delta", 0.0)), 2),
                "explanation": str(row.get("explanation", ""))
            })

    # 5. Extract Full Exceptions list
    exceptions = []
    exception_df = df[df["classification"] == "Exception"]
    for _, row in exception_df.iterrows():
        exceptions.append({
            "transaction_id": str(row["transaction_id"]),
            "note": str(row.get("explanation", "Missing sub_instrument routing tag."))
        })

    # 6. Assemble complete presentation payload
    final_report = {
        "overview": overview,
        "batch_structural_audits": batch_audits,
        "leak_by_category": leak_by_category,
        "top_offenders": top_offenders,
        "exceptions": exceptions,
        "audit_trail_available": True,
        "generated_at": datetime.now().isoformat()
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    print(f"[InterDrift Reporter] Report successfully saved to {output_path}")
    return final_report


if __name__ == "__main__":
    build_final_report()