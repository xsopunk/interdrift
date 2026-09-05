import pandas as pd
import json
import time
import math
from pathlib import Path
import os
import sys

# Append workspace root to path
sys.path.append(os.getcwd())

from src.rules_engine.engine import run_pipeline
from src.data_generation.generate_settlement_data import generate_dataset

print("=== Audit Pass 3: Backend Rigor Checks ===\n")

print("10. Test Data Generator Correctness")
config = {
    "num_transactions": 2000,
    "min_amount": 10.0,
    "max_amount": 150000.0, # Check if >1,00,000 works
    "rupay_credit_leak_rate": 0.15,
    "l2_l3_downgrade_rate": 0.12,
    "mcc_misclass_rate": 0.10,
    "exception_rate": 0.05
}

df_gen = generate_dataset(config)
total = len(df_gen)
counts = df_gen["injected_issue"].value_counts().to_dict()
print(f"Generated {total} rows.")
print(f"Rates - RuPay Credit: {counts.get('R3', 0) + counts.get('R4', 0)} / {total}")
print(f"Rates - Exception: {counts.get('EXCEPTION', 0)} / {total}")
print(f"Rates - MCC: {counts.get('R12', 0)} / {total}")

df_gen.to_csv("data/raw/audit3_test.csv", index=False)

print("\n11. Performance/Efficiency")
start_time = time.time()
summary = run_pipeline("data/raw/audit3_test.csv")
pipeline_time = time.time() - start_time
print(f"Rules Pipeline Time: {pipeline_time:.2f}s")

df_res = pd.read_csv("data/processed/row_level_results.csv")

print("\n1. Rule classification correctness")
mismatches = 0
for idx, row in df_res.iterrows():
    injected = str(row.get("injected_issue", "NONE"))
    matched = str(row.get("matched_rule_id", "NONE"))
    classif = row.get("classification", "")
    
    if injected == "NONE" and classif != "Matched":
        mismatches += 1
    elif injected == "EXCEPTION" and classif != "Exception":
        mismatches += 1
    elif injected in ["R1", "R2", "R3", "R4", "R5", "R6b", "R8", "R10"]:
        if matched != injected:
            mismatches += 1
print(f"Classification Mismatches against injected truth: {mismatches}")

print("\n2. Null vs zero handling")
exc_rows = df_res[df_res["classification"] == "Exception"]
delta_nulls = exc_rows["delta"].isna().sum()
exp_nulls = exc_rows["expected_fee"].isna().sum()
print(f"Exceptions: {len(exc_rows)}. Delta Nulls: {delta_nulls}. Expected Fee Nulls: {exp_nulls}")
zero_deltas = exc_rows[exc_rows["delta"] == 0.0].shape[0]
print(f"Zero deltas in exceptions (should be 0 if correctly null): {zero_deltas}")

print("\n3. Rule Precedence / Conflict Handling")
with open("src/rules_engine/row_classifier.py", "r") as f:
    code = f.read()
    if "specificity" in code.lower() or "sort" in code.lower():
         print("Precedence logic found in code: True")
    else:
         print("Precedence logic found in code: False")

print("\n4. Floating point tolerance")
if "math.isclose" in code or "1e-5" in code or "round(" in code:
    print("Floating point tolerance found in row_classifier.py: True")
else:
    print("Floating point tolerance found in row_classifier.py: False")

print("\n5. Batch structural audits correctness")
with open("data/processed/summary.json", "r") as f:
    summ = json.load(f)
r12_audit = summ.get("batch_structural_audits", {}).get("R12_mcc_misclassification", {})
print(f"R12 Delta in structural audit: {r12_audit.get('financial_impact_delta')}")

print("\n6. Agent grouping and prioritization")
with open("src/agent/prioritizer.py", "r") as f:
    code = f.read()
    print("Priority logic features extracted from code:")
    for line in code.split("\n"):
        if "priority_score =" in line or "weight" in line.lower():
            print(f"  {line.strip()}")

print("\n8 & 9. Case Lifecycle & Baseline")
try:
    with open("src/agent/baseline.py", "r") as f:
        code = f.read()
        for line in code.split("\n"):
            if "change_pct" in line or "percent_change" in line:
                print(f"  Baseline computation line: {line.strip()}")
except Exception as e:
    print("Baseline error:", e)

print("\nDone with backend checks.")
