"""
Module 13: Agent Orchestrator
Central coordinator that chains all agent modules into a single pipeline:

  Grouping (8.2) → Prioritization (8.3) → LLM Reasoning (8.4) → Case Creation (9) → Baseline (10)

Callable from the API after each batch upload. Idempotent — safe to re-run.
"""

import time
from typing import Dict, Any, List
from datetime import datetime

from src.agent.grouping import build_investigation_groups, get_group_summary
from src.agent.prioritizer import prioritize_groups
from src.agent.reasoning import diagnose_all_groups
from src.agent.control_case import build_all_cases, get_cases_summary
from src.agent.baseline import capture_baseline, get_baseline, compute_effectiveness


def run_agent_pipeline(
    skip_llm: bool = False,
    use_cache: bool = True,
    capture_baseline_snapshot: bool = False,
    source_label: str = "batch",
) -> Dict[str, Any]:
    """
    Runs the full agent pipeline end-to-end.

    Args:
        skip_llm: If True, skips Gemini LLM calls (uses fallback diagnosis).
                  Useful for testing or when rate-limited.
        use_cache: If True, reuses cached LLM diagnoses for unchanged groups.
        capture_baseline_snapshot: If True, saves current metrics as baseline
                                   before running agent analysis.
        source_label: Label for the baseline snapshot (e.g., "batch_1", "july_settlement").

    Returns:
        Pipeline result with group summary, case summary, and effectiveness data.
    """
    pipeline_start = time.time()
    steps = []

    # --- Step 0: Optionally capture baseline before analysis ---
    baseline_data = None
    if capture_baseline_snapshot:
        baseline_data = capture_baseline(source_label=source_label)
        steps.append({
            "step": "baseline_capture",
            "status": "done" if baseline_data else "skipped",
            "snapshot_id": baseline_data.get("snapshot_id", "") if baseline_data else "",
        })

    # --- Step 1: Investigation & Grouping (Module 8.2) ---
    t0 = time.time()
    groups = build_investigation_groups()
    group_summary = get_group_summary(groups)
    steps.append({
        "step": "grouping",
        "status": "done",
        "groups_created": len(groups),
        "duration_s": round(time.time() - t0, 2),
    })

    # --- Step 2: Transparent Prioritization (Module 8.3) ---
    t0 = time.time()
    ranked_groups = prioritize_groups(groups)
    steps.append({
        "step": "prioritization",
        "status": "done",
        "top_group": ranked_groups[0]["group_id"] if ranked_groups else None,
        "duration_s": round(time.time() - t0, 2),
    })

    # --- Step 3: LLM Reasoning (Module 8.4) ---
    t0 = time.time()
    if skip_llm:
        # Attach empty fallback diagnosis to each group
        diagnosed_groups = []
        for g in ranked_groups:
            diagnosed_groups.append({
                **g,
                "agent_diagnosis": {
                    "group_id": g["group_id"],
                    "root_cause": "LLM reasoning skipped (skip_llm=True).",
                    "diagnosis": "Agent diagnosis was skipped for this run.",
                    "recommended_action": "request_manual_review",
                    "action_rationale": "LLM reasoning was intentionally skipped.",
                    "confidence_level": "low",
                    "human_approval_required": True,
                },
            })
        steps.append({
            "step": "llm_reasoning",
            "status": "skipped",
            "reason": "skip_llm=True",
            "duration_s": round(time.time() - t0, 2),
        })
    else:
        diagnosed_groups = diagnose_all_groups(ranked_groups, use_cache=use_cache)
        diagnosed_count = sum(
            1 for g in diagnosed_groups
            if not g.get("agent_diagnosis", {}).get("root_cause", "").startswith("Unable")
        )
        steps.append({
            "step": "llm_reasoning",
            "status": "done",
            "diagnosed_count": diagnosed_count,
            "total_groups": len(diagnosed_groups),
            "duration_s": round(time.time() - t0, 2),
        })

    # --- Step 4: Case Creation (Module 9) ---
    t0 = time.time()
    cases = build_all_cases(diagnosed_groups)
    case_summary = get_cases_summary()
    steps.append({
        "step": "case_creation",
        "status": "done",
        "cases_created": len(cases),
        "actionable": case_summary.get("actionable_count", 0),
        "duration_s": round(time.time() - t0, 2),
    })

    # --- Step 5: Effectiveness Check (Module 10) ---
    effectiveness = compute_effectiveness()
    steps.append({
        "step": "effectiveness_check",
        "status": effectiveness.get("status", "unknown"),
        "verdict": effectiveness.get("verdict", "N/A"),
    })

    pipeline_duration = round(time.time() - pipeline_start, 2)

    result = {
        "pipeline_status": "complete",
        "ran_at": datetime.now().isoformat(),
        "duration_s": pipeline_duration,
        "group_summary": group_summary,
        "case_summary": case_summary,
        "effectiveness": effectiveness if effectiveness.get("status") == "computed" else None,
        "steps": steps,
    }

    print(f"[InterDrift Orchestrator] Pipeline complete in {pipeline_duration}s — "
          f"{len(groups)} groups, {len(cases)} cases, "
          f"{case_summary.get('actionable_count', 0)} actionable.")

    return result
