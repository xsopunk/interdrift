# PROMPT — Module 8.1: Agent State & Tool Interfaces

## Goal
Define a bounded set of tool functions the agent layer is allowed to call. These are the *only* way the agent touches the system — no direct DB/file access from agent code outside these tools. No LLM calls in this module — this is pure plumbing, same spirit as Module 4's API layer.

## Task

Create a new module (e.g. `src/agent/tools.py`) implementing these functions, each reading from existing Module 1–6 outputs (via the endpoints/files confirmed in Module 7.5 — reuse them, do not reimplement underlying logic):

- `get_audit_summary()` → returns the overview/summary object (total transactions, match/leak/exception counts, total leaked amount, etc.)
- `get_transaction_details(transaction_id)` → full row-level record for one transaction
- `get_rule_evidence(rule_id)` → the rule's condition, source_status, source_citation, confidence_note from the rule table
- `get_contract_terms()` → synthetic MSA contents
- `get_structural_audit()` → R11/R12 batch-level aggregate results
- `get_exception_details()` → full exception list with reasons
- `calculate_exposure(rule_id_or_category)` → sum of ₹ delta for a given rule or category (reuse existing aggregation, do not recompute independently)
- `compare_with_baseline()` → stub only in this module — return a placeholder/not-yet-implemented response; full logic comes in Module 10. Just define the function signature and return shape now so later modules have a stable interface to build against.

## Constraints
- Each function is a thin read/wrapper — no new calculation, no classification logic, no LLM calls.
- Each function should have a docstring stating exactly what it returns and which existing data source it reads from.
- Keep return shapes as plain dicts/lists (JSON-serializable) — the agent reasoning layer (Module 8.2+) and any future API exposure will consume these directly.
- If a function needs data that Module 7.5 didn't expose, flag it rather than silently building new backend logic — check back against Module 7.5's output first.

## Exit check (confirm before summarizing)
- Every tool function runs standalone against the real 500-row dataset and returns sensible, correctly-shaped output — test each with at least one real example (e.g., `get_transaction_details("TXN_000006")` returns that exact exception record).
- No tool function performs a calculation Module 3/6 didn't already do.
- `compare_with_baseline()` exists as a clear stub, not silently skipped.

## When done
Summarize: list of all tool functions implemented, which existing data source/endpoint each one wraps, one real example output per function, and anything you had to add back in Module 7.5's territory to make a tool work (should be rare/none if Module 7.5 was thorough).