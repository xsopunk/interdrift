"""
Module 8.4: Agent-Level LLM Reasoning Layer with Multi-Route Fallback
Generates root-cause diagnosis and remediation recommendations per investigation group.

Multi-Route Fallback Architecture:
  Route 1 (Primary): Google Gemini Flash (via GEMINI_API_KEY)
  Route 2 (Fallback): Groq High-Speed Engine (via GROQ_API_KEY)
  Route 3 (Fallback): OpenRouter / OpenAI (via OPENROUTER_API_KEY / OPENAI_API_KEY)
  Route 4 (Safety Net): Deterministic Domain-Rule Fallback

One call per group (~9 calls total) with local caching to guarantee instant execution on repeated runs.
"""

import os
import json
import time
import hashlib
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = Path("data/processed/agent_cache")

# --- Fixed Action Vocabulary (from Module 9 / ROADMAP) ---
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


class GroupDiagnosis(BaseModel):
    group_id: str
    root_cause: str
    diagnosis: str
    recommended_action: str
    action_rationale: str
    confidence_level: str
    human_approval_required: bool


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
- Output ONLY valid JSON matching this schema:
{
  "group_id": "string",
  "root_cause": "string",
  "diagnosis": "string",
  "recommended_action": "string",
  "action_rationale": "string",
  "confidence_level": "high" | "medium" | "low",
  "human_approval_required": true | false
}
"""


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
    """Format a single group into a structured prompt."""
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

    if "priority_rank" in group:
        lines.append(f"Priority Rank: #{group['priority_rank']} (score: {group.get('priority_score', 'N/A')})")
        lines.append(f"Priority Rationale: {group.get('priority_explanation', '')}")

    if "structural_details" in group:
        lines.append(f"Structural Details: {json.dumps(group['structural_details'], indent=2)}")

    samples = group.get("sample_transactions", [])
    if samples:
        lines.append("\nSample Transactions:")
        for s in samples:
            lines.append(
                f"  - {s.get('transaction_id')}: amount=Rs {s.get('amount', 0):,.2f}, "
                f"fee_charged=Rs {s.get('fee_charged', 0):,.2f}, "
                f"expected_fee={'N/A' if s.get('expected_fee') is None else f'Rs {s[\"expected_fee\"]:,.2f}'}, "
                f"delta={'N/A' if s.get('delta') is None else f'Rs {s[\"delta\"]:,.2f}'}"
            )

    return "\n".join(lines)


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Helper to cleanly extract JSON object from markdown or raw string."""
    try:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return None


# ============================================================
# Multi-Route LLM Implementations
# ============================================================

def _call_gemini(prompt: str) -> Optional[Dict[str, Any]]:
    """Route 1: Google Gemini Flash."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    # Attempt 1: google-genai
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        gen_config = types.GenerateContentConfig(
            system_instruction=AGENT_SYSTEM_PROMPT,
            max_output_tokens=1000,
            response_mime_type="application/json",
            response_schema=GroupDiagnosis,
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=gen_config,
        )
        if response and response.text:
            return json.loads(response.text)
    except Exception as e:
        print(f"    [Gemini Route] google-genai attempt failed: {e}")

    # Attempt 2: google.generativeai fallback
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=AGENT_SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )
        resp = model.generate_content(prompt)
        if resp and resp.text:
            return _extract_json_from_text(resp.text)
    except Exception as e:
        print(f"    [Gemini Route] Request failed: {e}")

    return None


def _call_groq(prompt: str) -> Optional[Dict[str, Any]]:
    """Route 2: Groq high-speed engine."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    candidate_models = ["qwen/qwen3.6-27b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    for model in candidate_models:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key.strip()}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
                "max_tokens": 1000,
            }

            resp = requests.post(url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = _extract_json_from_text(content)
                if parsed:
                    return parsed
        except Exception as e:
            print(f"    [Groq Route] Model {model} failed: {e}")
            continue

    return None


def _call_openrouter(prompt: str) -> Optional[Dict[str, Any]]:
    """Route 3: OpenRouter / OpenAI API Fallback."""
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        is_openai = "OPENAI_API_KEY" in os.environ and not os.getenv("OPENROUTER_API_KEY")
        url = "https://api.openai.com/v1/chat/completions" if is_openai else "https://openrouter.ai/api/v1/chat/completions"
        model = "gpt-4o-mini" if is_openai else "meta-llama/llama-3.3-70b-instruct"

        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 1000,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return _extract_json_from_text(content)
    except Exception as e:
        print(f"    [OpenRouter/OpenAI Route] Request failed: {e}")

    return None


# ============================================================
# Main Multi-Route Diagnosis Functions
# ============================================================

def diagnose_group(group: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
    """
    Diagnoses a group using the multi-route LLM chain.
    """
    ck = _cache_key(group)
    if use_cache:
        cached = _load_cached(ck)
        if cached:
            return cached

    prompt = _format_group_prompt(group)
    raw_result = None
    provider_used = None

    # Route 1: Gemini
    raw_result = _call_gemini(prompt)
    if raw_result:
        provider_used = "Gemini Flash"

    # Route 2: Groq (if Gemini failed/rate limited)
    if not raw_result:
        print("    [Fallback Router] Calling Groq Engine...")
        raw_result = _call_groq(prompt)
        if raw_result:
            provider_used = "Groq High-Speed"

    # Route 3: OpenRouter / OpenAI
    if not raw_result:
        print("    [Fallback Router] Calling OpenRouter / OpenAI...")
        raw_result = _call_openrouter(prompt)
        if raw_result:
            provider_used = "OpenRouter / OpenAI"

    # Parse and enforce schema
    if raw_result:
        try:
            parsed = GroupDiagnosis.model_validate(raw_result)
            result = parsed.model_dump()

            if result["recommended_action"] not in REMEDIATION_ACTIONS:
                result["recommended_action"] = "request_manual_review"
                result["action_rationale"] += " (action normalized to allowed vocabulary)"

            result["provider"] = provider_used
            _save_cache(ck, result)
            return result
        except Exception as err:
            print(f"    [Validation Error]: {err}")

    # Route 4: Deterministic Domain-Rule Safety Fallback
    fallback = {
        "group_id": group["group_id"],
        "root_cause": f"Discrepancy pattern identified for rule(s): {', '.join(group['rule_ids'])}.",
        "diagnosis": f"Automated diagnosis completed via deterministic statutory baseline. Total exposure: Rs {group['total_exposure_inr']:,.2f}.",
        "recommended_action": "request_manual_review" if group.get("group_type") == "exception" else "request_mdr_refund",
        "action_rationale": "Requires human operator confirmation prior to financial recovery execution.",
        "confidence_level": "medium",
        "human_approval_required": True,
        "provider": "Deterministic Rules Fallback",
    }
    return fallback


def diagnose_all_groups(
    prioritized_groups: List[Dict[str, Any]],
    use_cache: bool = True,
    delay_between_calls: float = 0.2,
) -> List[Dict[str, Any]]:
    """
    Runs multi-route agent diagnosis on all prioritized groups.
    """
    print(f"[InterDrift Agent] Diagnosing {len(prioritized_groups)} groups via Multi-Route LLM Engine...")
    results = []

    for i, group in enumerate(prioritized_groups):
        gid = group["group_id"]
        print(f"  [{i + 1}/{len(prioritized_groups)}] Diagnosing {gid}...")

        diagnosis = diagnose_group(group, use_cache=use_cache)

        enriched = {
            **group,
            "agent_diagnosis": diagnosis,
        }
        results.append(enriched)

        if i < len(prioritized_groups) - 1:
            time.sleep(delay_between_calls)

    success_count = sum(
        1 for r in results
        if not r["agent_diagnosis"].get("root_cause", "").startswith("Unable")
    )
    print(f"[InterDrift Agent] Multi-Route diagnosis complete: {success_count}/{len(results)} groups successfully diagnosed.")
    return results
