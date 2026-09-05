import json
import sys
sys.path.insert(0, ".")

from src.agent.baseline import compute_effectiveness, get_baseline, capture_baseline
from src.agent.control_case import get_all_cases

# Load baseline snapshot
base = get_baseline()
print("Baseline Snapshot:")
print(f"  Snapshot ID: {base.get('snapshot_id')}")
print(f"  Total Leaked: Rs {base.get('total_leaked_amount')}")
print(f"  Structural Overcharge: Rs {base.get('structural_overcharge_amount')}")
print(f"  Exception Count: {base.get('exception_count')}")
print(f"  Matched Percent: {base.get('matched_percent')}%")

# Compute effectiveness against current
eff = compute_effectiveness()
print("\nEffectiveness Result:")
print(f"  Status: {eff.get('status')}")
print(f"  Verdict: {eff.get('verdict')}")
print(f"  Metrics:")
for k, v in eff.get("metrics", {}).items():
    print(f"    {k}: {v}")

# Now test scenario: simulate an improvement where current batch leakage dropped
print("\n--- Simulating 50% Reduction Scenario ---")
# If baseline was 3727.92 and current is 1863.96
b_val = 3727.92
c_val = 1863.96
pct_change = round(((c_val - b_val) / b_val) * 100, 2)
pct_reduction = round(-pct_change, 2)
print(f"Baseline: Rs {b_val}, Current: Rs {c_val}")
print(f"pct_change = (({c_val} - {b_val}) / {b_val}) * 100 = {pct_change}%")
print(f"percent_reduction = -pct_change = {pct_reduction}%")
print(f"Backend verdict logic: pct_change < 0 -> 'IMPROVING' (improvement = positive reduction: +{pct_reduction}%)")

# Check frontend display logic for this:
# In ControlEffectivenessCard.jsx:
# formatDelta(totalLeaked.percent_change ?? totalLeaked.percent_reduction, true, true)
# totalLeaked.percent_change is -50.0%
# formatDelta(-50.0, isPercentage=true, invertGood=true):
#   isGood = invertGood ? val < 0 : val > 0 -> (-50.0 < 0) = True -> emerald green text
#   sign = val > 0 ? '+' : '' -> '' (negative preserves minus sign: -50.0%)
# Frontend renders: -50% in green (emerald) with 'Control Effective (Improving)' badge.
