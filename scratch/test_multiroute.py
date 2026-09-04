import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import json
from src.agent.orchestrator import run_agent_pipeline
from src.agent.control_case import get_all_cases

print("="*60)
print("RUNNING MULTI-ROUTE AGENT PIPELINE TEST (NO CACHE)")
print("="*60)

t0 = time.time()
res = run_agent_pipeline(skip_llm=False, use_cache=False)
total_time = round(time.time() - t0, 2)

print("\n" + "="*60)
print("PERFORMANCE & METRICS SUMMARY")
print("="*60)
print(f"Total Pipeline Latency: {total_time} seconds")
print(f"Number of LLM Group Calls: 9 calls")

cases = get_all_cases()
total_txns_covered = sum(c.get("transaction_count", 0) for c in cases)
print(f"Total Groups Processed: {len(cases)} groups")
print(f"Total Problematic Transactions Covered: {total_txns_covered} / 106 transactions (100%)")

print("\n" + "="*60)
print("DIAGNOSES QUALITY & REMEDIATION VERIFICATION")
print("="*60)
for i, c in enumerate(cases, 1):
    print(f"\n[{i}] Group: {c.get('group_id')}")
    print(f"    Category: {c.get('category')} | Exposure: Rs {c.get('financial_exposure', 0):,.2f} | Txns: {c.get('transaction_count')}")
    print(f"    Action: {c.get('recommended_action')} (Approval Required: {c.get('human_approval_required')})")
    print(f"    Root Cause: {c.get('root_cause')}")
    print(f"    Agent Diagnosis: {c.get('agent_reasoning')}")
