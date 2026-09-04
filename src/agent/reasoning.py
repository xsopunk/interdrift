"""
Module 8.4: Agent-Level LLM Reasoning Layer (Grouped, not per-row)
Generates root-cause diagnosis and remediation recommendations per investigation group.

One Gemini call per group (~9 calls total), not per transaction (~106).
This structurally fixes the existing rate-limit problem from Module 5.

Keeps Module 5's per-transaction explanations intact — this is a separate agent-level layer.
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

CACHE_DIR = Path("data/processed/agent_cache")

# --- Fixed Action Vocabulary (from Module 9 / ROADMAP) ---
# The agent may ONLY recommend actions from this list.
REMEDIATION_ACTIONS = [
    "request_mdr_refund",
    "file_regulatory_dispute",
    "audit_gateway_fee_config",
    "migrate_to_ic_plus_pricing",
    "correct_mcc_mapping",
    "supply_l2_l3_data",
    "renegotiate_contract_rate",
    "enable_least_cost_routing",
    "escalate_to_acquirer",
    "request_manual_review",
    "no_action_required",
]


# --- Pydantic schemas for structured Gemini output ---
class GroupDiagnosis(BaseModel):
    group_id: str
    root_cause: str
    diagnosis: str
    recommended_action: str
    action_rationale: str
    confidence_level: str
    human_approval_required: bool


# --- System prompt for agent-level group reasoning ---
AGENT_SYSTEM_PROMPT = """You are an autonomous Payment-Cost Control Agent analyzing grouped settlement fee audit findings for an Indian merchant.

You will receive a GROUP of related transactions that share the same root cause. Your job is to:
1. Diagnose the root cause of the fee discrepancy pattern in 1-2 sentences.
2. Provide a clear, actionable diagnosis explaining WHY this pattern is occurring.
3. Recommend exactly ONE remediation action from the allowed action vocabulary.
4. Explain why that action is the right fix in 1 sentence.
5. Assess confidence_level as "high", "medium", or "low".
6. Set human_approval_required to true for consequential actions (dispute filing, pricing changes, PSP contact, routing changes, contract renegotiation). Set false for investigation/monitoring only.

ALLOWED REMEDIATION ACTIONS (use exactly one of these strings):
- request_mdr_refund: Merchant should request refund of overcharged MDR fees
- file_regulatory_dispute: File a formal dispute citing regulatory violation
- audit_gateway_fee_config: Ask acquirer/gateway to audit their fee configuration
- migrate_to_ic_plus_pricing: Switch from blended to interchange-plus pricing model
- correct_mcc_mapping: Fix merchant category code in gateway configuration
- supply_l2_l3_data: Provide Level 2/3 commercial card data to avoid downgrades
- renegotiate_contract_rate: Renegotiate contracted flat rate with acquirer
- enable_least_cost_routing: Enable routing optimization to prefer lower-cost rails
- escalate_to_acquirer: Escalate issue to acquiring bank relationship manager
- request_manual_review: Flag for human analyst review (insufficient data to recommend)
- no_action_required: No remediation needed

STRICT RULES:
- Never fabricate rupee figures. Use only the numbers provided.
- If source_status is "illustrative", explicitly note that the comparison uses a modeled benchmark.
- Never auto-execute actions. Only recommend.
- For exceptions (missing data), recommend request_manual_review — do not force a classification.
"""


def _get_client():
    """Lazy-init Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env")
    return genai.Client(api_key=api_key)


def _cache_key(group: Dict[str, Any]) -> str:
    """Generate a stable cache key for a group to avoid re-diagnosing unchanged groups."""
    sig = json.dumps({
        "group_id": group["group_id"],
        "transaction_count": group["transaction_count"],
        "total_exposure_inr": group["total_exposure_inr"],
        "rule_ids": group["rule_ids"],
    }, sort_keys=True)
    return hashlib.md5(sig.encode()).hexdigest()


def _load_cached(cache_key: str) -> Optional[Dict[str, Any]]:
    """Load a cached diagnosis if it exists."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _save_cache(cache_key: str, diagnosis: Dict[str, Any]):
    """Save a diagnosis to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(diagnosis, f, indent=2)


def _format_group_prompt(group: Dict[str, Any]) -> str:
    """Format a single group into a structured prompt for Gemini."""
    lines = [
        f"GROUP ID: {group['group_id']}",
        f"Group Type: {group['group_type']}",
        f"Classification: {group['classification']}",
        f"Rule IDs: {', '.join(group['rule_ids'])}",
        f"Category: {group['category']}",
        f"Source Status: {group['source_status']}",
        f"Sub-instrument: {group.get('sub_instrument', 'N/A')}",
        f"Transaction Count: {group['transaction_count']}",
        f"Total Exposure: Rs {group['total_exposure_inr']:,.2f}",
    ]

    # Add priority context if available
    if "priority_rank" in group:
        lines.append(f"Priority Rank: #{group['priority_rank']} (score: {group.get('priority_score', 'N/A')})")
        lines.append(f"Priority Rationale: {group.get('priority_explanation', '')}")

    # Add structural details if present
    if "structural_details" in group:
        lines.append(f"Structural Details: {json.dumps(group['structural_details'], indent=2)}")

    # Add sample transactions
    samples = group.get("sample_transactions", [])
    if samples:
        lines.append("\nSample Transactions:")
        for s in samples:
            lines.append(
                f"  - {s.get('transaction_id')}: amount=Rs {s.get('amount', 0):,.2f}, "
                f"fee_charged=Rs {s.get('fee_charged', 0):,.2f}, "
                f"expected_fee=Rs {s.get('expected_fee', 0):,.2f}, "
                f"delta=Rs {s.get('delta', 0):,.2f}"
            )

    return "\n".join(lines)


def diagnose_group(group: Dict[str, Any], use_cache: bool = True, max_retries: int = 3) -> Dict[str, Any]:
    """
    Send a single group to Gemini for root-cause diagnosis and remediation recommendation.
    Includes retry with exponential backoff and caching.
    """
    # Check cache first
    ck = _cache_key(group)
    if use_cache:
        cached = _load_cached(ck)
        if cached:
            return cached

    client = _get_client()
    prompt = _format_group_prompt(group)

    gen_config = types.GenerateContentConfig(
        system_instruction=AGENT_SYSTEM_PROMPT,
        max_output_tokens=1000,
        response_mime_type="application/json",
        response_schema=GroupDiagnosis,
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=gen_config,
            )

            if response.text:
                parsed = GroupDiagnosis.model_validate_json(response.text)
                result = parsed.model_dump()

                # Validate action is from vocabulary
                if result["recommended_action"] not in REMEDIATION_ACTIONS:
                    result["recommended_action"] = "request_manual_review"
                    result["action_rationale"] += " (action normalized to allowed vocabulary)"

                # Cache successful result
                _save_cache(ck, result)
                return result

        except Exception as e:
            last_error = e
            wait = 2 ** attempt
            print(f"  [Retry {attempt + 1}/{max_retries}] Error: {e}. Waiting {wait}s...")
            time.sleep(wait)

    # Fallback if all retries fail
    fallback = {
        "group_id": group["group_id"],
        "root_cause": "Unable to generate diagnosis — LLM call failed.",
        "diagnosis": f"Automated diagnosis unavailable after {max_retries} retries. Error: {str(last_error)}",
        "recommended_action": "request_manual_review",
        "action_rationale": "Fallback: requires human analyst review due to LLM failure.",
        "confidence_level": "low",
        "human_approval_required": True,
    }
    return fallback


def diagnose_all_groups(
    prioritized_groups: List[Dict[str, Any]],
    use_cache: bool = True,
    delay_between_calls: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Runs agent-level LLM diagnosis on all prioritized groups.
    Returns the groups enriched with diagnosis fields.
    """
    print(f"[InterDrift Agent] Diagnosing {len(prioritized_groups)} groups via Gemini...")
    results = []

    for i, group in enumerate(prioritized_groups):
        gid = group["group_id"]
        print(f"  [{i + 1}/{len(prioritized_groups)}] Diagnosing {gid}...")

        diagnosis = diagnose_group(group, use_cache=use_cache)

        # Merge diagnosis into group
        enriched = {
            **group,
            "agent_diagnosis": diagnosis,
        }
        results.append(enriched)

        # Rate limit courtesy delay
        if i < len(prioritized_groups) - 1:
            time.sleep(delay_between_calls)

    success_count = sum(1 for r in results if r["agent_diagnosis"].get("root_cause", "").startswith("Unable") is False)
    print(f"[InterDrift Agent] Diagnosis complete: {success_count}/{len(results)} groups diagnosed successfully.")
    return results
