"""
Module 3.3: Main Rules Engine Pipeline
Runs full audit against raw settlement batch and outputs structured analytics.

"""

import json
from pathlib import Path
import pandas as pd

from src.rules_engine.rule_loader import load_rules
from src.rules_engine.row_classifier import classify_row
from src.rules_engine.batch_auditor import audit_blended_vs_ic_plus, audit_mcc_misclassification


def run_pipeline(
    data_path: str = "data/raw/settlement_batch_01.csv",
    msa_path: str = "data/raw/merchant_msa.json",
    rules_path: str = "data/rules/rule_table.json",
    output_dir: str = "data/processed"
):
    print("[InterDrift Engine] Loading data and rule taxonomy...")
    df = pd.read_csv(data_path)
    with open(msa_path, "r", encoding="utf-8") as f:
        msa = json.load(f)
    rules = load_rules(rules_path)

    print(f"[InterDrift Engine] Classifying {len(df)} transactions row-by-row...")
    row_results = []
    for _, row in df.iterrows():
        res = classify_row(row, rules)
        row_results.append(res)

    results_df = pd.DataFrame(row_results)
    full_audit_df = pd.concat([df, results_df.drop(columns=["transaction_id"])], axis=1)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    row_output_path = Path(output_dir) / "row_level_results.csv"
    full_audit_df.to_csv(row_output_path, index=False)

    print("[InterDrift Engine] Running batch structural audits (R11 & R12)...")
    r11_audit = audit_blended_vs_ic_plus(df, msa)
    r12_audit = audit_mcc_misclassification(df, msa)

    # Aggregations
    total_txns = len(results_df)
    counts = results_df["classification"].value_counts().to_dict()
    total_row_leakage = round(results_df[results_df["classification"] == "Leaked"]["delta"].sum(), 2)

    summary = {
        "total_transactions": total_txns,
        "classification_counts": {
            "Matched": counts.get("Matched", 0),
            "Leaked": counts.get("Leaked", 0),
            "Exception": counts.get("Exception", 0),
            "Flagged_For_Review": counts.get("Flagged_For_Review", 0)
        },
        "accuracy_rate_pct": round((counts.get("Matched", 0) / total_txns) * 100, 2),
        "total_row_leakage_inr": total_row_leakage,
        "batch_structural_audits": {
            "R11_blended_mdr_spread": r11_audit,
            "R12_mcc_misclassification": r12_audit
        }
    }

    summary_path = Path(output_dir) / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("      INTERDRIFT AUDIT RUN COMPLETE")
    print("=" * 50)
    print(f"Total Transactions Audited : {total_txns}")
    print(f"  - Matched                : {summary['classification_counts']['Matched']} ({summary['accuracy_rate_pct']}%)")
    print(f"  - Leaked (Overcharged)   : {summary['classification_counts']['Leaked']}")
    print(f"  - Exceptions             : {summary['classification_counts']['Exception']}")
    print(f"  - Flagged for Review     : {summary['classification_counts']['Flagged_For_Review']}")
    print(f"\nTotal Direct Fee Leakage  : Rs {total_row_leakage:,.2f}")
    print(f"R11 Blended Spread Leakage: Rs {r11_audit['structural_overcharge_delta']:,.2f}")
    print(f"R12 MCC Misalignment Loss : Rs {r12_audit['financial_impact_delta']:,.2f}")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()