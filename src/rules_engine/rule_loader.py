"""
Module 2: Rule Loader Utility
Loads, validates, and indexes regulatory & illustrative rules from JSON.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_rules(filepath: str = "data/rules/rule_table.json") -> List[Dict[str, Any]]:
    """Loads and validates the structured rule table."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Rule table not found at: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "rules" not in data or not isinstance(data["rules"], list):
        raise ValueError("Malformed rule table: root must contain a 'rules' list.")

    return data["rules"]


def get_rule_by_id(rule_id: str, filepath: str = "data/rules/rule_table.json") -> Dict[str, Any]:
    """Fetches a single rule definition by its unique identifier."""
    rules = load_rules(filepath)
    for rule in rules:
        if rule["rule_id"] == rule_id:
            return rule
    raise KeyError(f"Rule ID '{rule_id}' not found in rule table.")


def get_rules_summary(filepath: str = "data/rules/rule_table.json") -> Dict[str, int]:
    """Returns counts of sourced vs illustrative rules for reporting transparency."""
    rules = load_rules(filepath)
    summary = {"total": len(rules), "sourced": 0, "illustrative": 0}
    for rule in rules:
        status = rule.get("source_status", "illustrative")
        if status == "sourced":
            summary["sourced"] += 1
        else:
            summary["illustrative"] += 1
    return summary


if __name__ == "__main__":
    rules = load_rules()
    summary = get_rules_summary()
    print(f"[InterDrift] Loaded {summary['total']} rules successfully.")
    print(f" - Sourced (Regulatory): {summary['sourced']}")
    print(f" - Illustrative (Modeled): {summary['illustrative']}\n")

    print(f"{'Rule ID':<8} | {'Category':<28} | {'Status':<12} | {'Fee Type'}")
    print("-" * 65)
    for r in rules:
        print(f"{r['rule_id']:<8} | {r['category']:<28} | {r['source_status']:<12} | {r['expected_fee_type']}")