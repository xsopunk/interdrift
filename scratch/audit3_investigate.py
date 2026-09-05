import os
import json
import time
import pandas as pd
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

from src.rules_engine.engine import run_pipeline
from src.agent.grouping import build_investigation_groups
from src.agent.prioritizer import prioritize_groups
from src.agent.reasoning import diagnose_group, diagnose_all_groups, _call_gemini, _call_groq, _format_group_prompt
from src.agent.control_case import build_all_cases, get_all_cases
from src.agent.baseline import compute_effectiveness, capture_baseline, get_baseline

print("=== STEP 1: Rule Classification Mismatch Details ===")
df = pd.read_csv('data/processed/row_level_results.csv')
raw = pd.read_csv('data/raw/settlement_batch_01.csv')
print(f"Total rows in raw/processed: {len(df)}")
ct = pd.crosstab(df['injected_issue'], df['classification'])
print("\nConfusion Matrix (injected_issue vs classification):")
print(ct)

# Check Item 7: Groups and LLM diagnosis
print("\n=== STEP 2: Investigation Groups (Item 7) ===")
groups = build_investigation_groups()
prioritized = prioritize_groups(groups)
print(f"Total groups created: {len(prioritized)}")
total_txns_in_groups = sum(g['transaction_count'] for g in prioritized)
print(f"Total transactions represented across all groups: {total_txns_in_groups}")
for idx, g in enumerate(prioritized, 1):
    print(f"#{idx}: {g['group_id']} | Type: {g['group_type']} | Class: {g['classification']} | Txns: {g['transaction_count']} | Exposure: Rs {g['total_exposure_inr']}")

# Check cache vs real execution
print("\n=== STEP 3: LLM Route Testing & Fallback Demonstration (Item 7) ===")
# Let's test calling one group with use_cache=False to see which route hits
test_group = prioritized[0]
print(f"Testing primary diagnosis on top group: {test_group['group_id']}...")
diag = diagnose_group(test_group, use_cache=False)
print(f"Result provider: {diag.get('provider')}")
print(f"Diagnosis root cause: {diag.get('root_cause')}")
print(f"Recommended action: {diag.get('recommended_action')}")

# Now test deterministic fallback explicitly by passing invalid keys or simulating
print("\nTesting Deterministic Fallback Route (simulate API failure / no keys):")
# Save keys
old_gem = os.environ.get("GEMINI_API_KEY")
old_groq = os.environ.get("GROQ_API_KEY")
try:
    os.environ["GEMINI_API_KEY"] = "invalid_key_for_test"
    os.environ["GROQ_API_KEY"] = "invalid_key_for_test"
    fallback_result = diagnose_group(test_group, use_cache=False)
    print("Fallback Result End-to-End:")
    print(json.dumps(fallback_result, indent=2))
finally:
    if old_gem: os.environ["GEMINI_API_KEY"] = old_gem
    if old_groq: os.environ["GROQ_API_KEY"] = old_groq

# Check Item 9: Baseline / Effectiveness
print("\n=== STEP 4: Baseline & Effectiveness (Item 9) ===")
base = get_baseline()
print("Baseline Snapshot loaded:", bool(base))
if base:
    print(f"Baseline Snapshot ID: {base.get('snapshot_id')}, Captured At: {base.get('captured_at')}")
    print(f"Baseline total leakage: Rs {base.get('total_leaked_amount')}")
eff = compute_effectiveness()
print("Effectiveness result status:", eff.get("status"))
print("Effectiveness verdict:", eff.get("verdict"))
print("Metrics:", json.dumps(eff.get("metrics"), indent=2))

# Check Item 11: Performance / Timing
print("\n=== STEP 5: Performance Timing Benchmark (Item 11) ===")
raw_path = 'data/raw/settlement_batch_01.csv'
t0 = time.perf_counter()
# 1. Pipeline classification
t_class_start = time.perf_counter()
summary = run_pipeline(raw_path)
t_class_end = time.perf_counter()
class_time = t_class_end - t_class_start

# 2. Grouping & Prioritization
t_group_start = time.perf_counter()
g_list = build_investigation_groups()
p_list = prioritize_groups(g_list)
t_group_end = time.perf_counter()
group_time = t_group_end - t_group_start

# 3. LLM Diagnosis (using cache or fresh)
t_diag_start = time.perf_counter()
diag_groups = diagnose_all_groups(p_list, use_cache=True)
t_diag_end = time.perf_counter()
diag_time = t_diag_end - t_diag_start

# 4. Case Creation
t_case_start = time.perf_counter()
cases = build_all_cases(diag_groups)
t_case_end = time.perf_counter()
case_time = t_case_end - t_case_start

total_time = time.perf_counter() - t0
print(f"\n--- Timing Results for {len(df)} Rows ---")
print(f"1. Ingestion & Classification : {class_time:.4f} s")
print(f"2. Grouping & Prioritization  : {group_time:.4f} s")
print(f"3. Agent Diagnosis (cached)   : {diag_time:.4f} s")
print(f"4. Control Case Generation    : {case_time:.4f} s")
print(f"Total End-to-End Runtime      : {total_time:.4f} s")
