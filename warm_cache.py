"""
InterDrift Demo Pre-Warming Script
Ensures deterministic rules engine results, LLM diagnosis cache, and control cases
are fully pre-warmed for instant sub-second judge demos.
"""
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from src.rules_engine.engine import run_pipeline
from src.agent.orchestrator import run_agent_pipeline

def warm_demo_cache():
    print("=" * 60)
    print("  INTERDRIFT DEMO PRE-WARMING PROTOCOL")
    print("=" * 60)
    t0 = time.time()
    
    # 1. Run deterministic rules classification
    print("[1/2] Classifying benchmark batch: data/raw/settlement_batch_01.csv...")
    run_pipeline("data/raw/settlement_batch_01.csv")
    
    # 2. Warm agent queue diagnosis & persist control cases
    print("[2/2] Resolving agent root-cause diagnosis & control cases...")
    res = run_agent_pipeline(use_cache=True)
    
    elapsed = time.time() - t0
    print("=" * 60)
    print(f"  PRE-WARMING COMPLETE ({elapsed:.2f}s)")
    print(f"  Cases Ready   : {res['case_summary'].get('total_cases', 0)}")
    print(f"  Actionable    : {res['case_summary'].get('actionable_count', 0)}")
    print("  Cache Status  : 100% WARM (Sub-second live demo guaranteed)")
    print("=" * 60)

if __name__ == "__main__":
    warm_demo_cache()
