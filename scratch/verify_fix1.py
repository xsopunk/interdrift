import sys
sys.path.insert(0, ".")
import pandas as pd
from src.rules_engine.engine import run_pipeline

res = run_pipeline("data/raw/settlement_batch_01.csv")
df = pd.read_csv("data/processed/row_level_results.csv")

print("\n=== UPDATED CONFUSION MATRIX (injected_issue vs classification) ===")
ct = pd.crosstab(df["injected_issue"], df["classification"], margins=True)
print(ct)

print("\n=== R10 INJECTED ROWS CLASSIFICATION ===")
r10 = df[df["injected_issue"] == "R10_l2_l3_downgrade"]
print(r10["classification"].value_counts())
print("\nR10 matched rules:")
print(r10["matched_rule_id"].value_counts())

print("\n=== SAMPLE R10 ROWS (PREVIOUSLY FALSE-MATCHED) ===")
sample_ids = ["TXN_000032", "TXN_000091", "TXN_000140", "TXN_000171", "TXN_000184", "TXN_000485"]
samples = df[df["transaction_id"].isin(sample_ids)]
for _, r in samples.iterrows():
    rate_billed = round((r['fee_charged'] / r['amount']) * 100, 2)
    rate_exp = round((r['expected_fee'] / r['amount']) * 100, 2)
    delta_rate = round(rate_billed - rate_exp, 2)
    print(f"{r['transaction_id']}: amount=Rs {r['amount']:,.2f}, charged=Rs {r['fee_charged']} ({rate_billed}%), expected=Rs {r['expected_fee']} ({rate_exp}%), delta=Rs {r['delta']} (+{delta_rate}% penalty) -> {r['classification']}")
