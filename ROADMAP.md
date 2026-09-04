# ROADMAP_AGENTIC.md — InterDrift Agentic Evolution
### Module 7.5 → End · Deviation build sequence (Modules 1–7 frozen/stable)

---

## Ground rules carried forward (do not violate in any module below)

- Deterministic engine (Modules 1–6) remains sole financial authority. Agent never calculates fees, deltas, or classifications.
- No LLM call per transaction. LLM/agent reasons over **grouped, material findings only**.
- Exceptions stay first-class and unclassified — never force-resolved.
- Illustrative rules (R10–R13) stay visibly labeled through every new layer.
- Consequential financial actions (dispute filing, pricing changes, PSP contact) require human approval — agent may only recommend/stage, never execute.
- Prefer adapters/extensions over rewriting Modules 1–7.

---

## Module 7.5 — Backend Compatibility Pass (prerequisite, do first)

**Goal:** make Modules 1–7's existing outputs cleanly consumable by an agent layer, with minimal changes.
- Audit existing API/data shapes (`final_report.json`, row-level results, rule table) against what the new agent tools (Module 8.1) will need.
- Add any missing structured fields (e.g., stable `rule_id` + `category` on every row, a queryable exceptions endpoint) — additive only, no breaking changes to existing frontend.
- Confirm existing endpoints are reusable as-is for `get_audit_summary()`, `get_transaction_details()`, `get_rule_evidence()`, `get_exception_details()`.
- **Exit check:** every planned agent tool (Module 8.1) has a real data source already available, with no schema gaps.

---

## Module 8.1 — Agent State & Tool Interfaces

**Goal:** define the bounded functions the agent is allowed to call — nothing more.
- Implement tool functions: `get_audit_summary()`, `get_transaction_details(id)`, `get_rule_evidence(id/rule_id)`, `get_contract_terms()`, `get_structural_audit()`, `get_exception_details()`, `calculate_exposure(rule/category)`, `compare_with_baseline()`.
- Each tool reads only from existing Module 1–7 outputs — no new calculation logic here.
- **Exit check:** every tool callable and manually tested with real output from your 500-row dataset.

---

## Module 8.2 — Investigation & Grouping

**Goal:** turn 500 row-level findings into a handful of root-cause groups.
- Group flagged/leaked/exception transactions by shared rule_id + instrument + pattern similarity (start simple: group by `rule_id` first; refine only if time allows).
- Output: N groups, each with member transaction IDs, shared rule(s), and aggregate ₹ exposure.
- **Exit check:** running this on your dataset produces a small, sensible number of groups (not 1, not 500) — e.g., R2 debit-MDR-overcharge group, R11 blended-MDR group, etc.

---

## Module 8.3 — Prioritization

**Goal:** rank groups, not individual transactions.
- Implement the transparent scoring model: priority ∝ exposure × confidence × recurrence × controllability. Keep it a simple weighted formula, not a black box — this needs to be explainable in one sentence during the pitch.
- **Exit check:** R11 (blended-MDR) and other high-exposure groups surface at the top; low-value/low-confidence groups rank lower.

---

## Module 8.4 — LLM Reasoning Layer (grouped, not per-row)

**Goal:** fix the Gemini rate-limit problem structurally, and generate agent-level diagnosis/recommendation per group instead of per transaction.
- One LLM call per **group** (not per transaction) — this alone should cut call volume from ~106 to a handful.
- Prompt per group: shared rule(s), member count, total exposure, sample transaction(s) → ask for root-cause diagnosis + recommended remediation action (from the fixed action vocabulary in Module 9).
- Keep Module 5's existing per-transaction explanations as-is where already built (Layer 2) — this is a new, separate Layer (agent-level), not a replacement.
- Add basic resilience: retry w/ backoff, simple caching (don't re-diagnose an unchanged group twice).
- **Exit check:** all material groups get a diagnosis with zero rate-limit failures.

---

## Module 9 — Control Case Model

**Goal:** persist findings as trackable cases instead of a one-time report.
- Implement `ControlCase` (fields: case_id, created_at, root_cause, rule_ids, affected_transactions, financial_exposure, confidence, priority, recommended_action, status, baseline_metric, current_metric, target_metric, evidence, agent_reasoning, human_approval_required, last_evaluated_at).
- Status lifecycle: OPEN → INVESTIGATING → ACTION_RECOMMENDED → AWAITING_HUMAN_APPROVAL → MONITORING → IMPROVED/ESCALATED → CLOSED.
- One case created per group from Module 8.2/8.3, populated with Module 8.4's diagnosis.
- Simple persistence is enough (JSON file or SQLite) — no need for a full database system.
- **Exit check:** cases created, inspectable, correctly populated from real data.

---

## Module 10 — Baseline & Control Effectiveness

**Goal:** extend existing Module 8 (from original roadmap) baseline concept into full control-effectiveness verification.
- On a second/subsequent batch upload: recompute exposure per existing case's root cause, compare to `baseline_metric`, determine IMPROVED / UNCHANGED / WORSENED, update case status accordingly.
- Compute headline effectiveness stat (e.g., "79.5% reduction in exposure") per case and in aggregate.
- **Exit check:** feeding a deliberately-improved second dataset (like your original Module 8 test) correctly flips relevant cases to IMPROVED with an accurate % figure.

---

## Module 11 — Human-in-the-Loop Boundary

**Goal:** enforce the approval gate explicitly in code and UI, not just in principle.
- Tag every recommended action with `human_approval_required: true` for anything in the consequential list (pricing change, real dispute filing, PSP contact, routing/config change, contract renegotiation).
- Agent-permitted autonomous actions (investigate, classify importance, group, recommend, create/update case, compare batches, escalate) require no gate.
- **Exit check:** no code path lets the agent auto-execute a gated action — recommendation only, always stopping at "awaiting approval."

---

## Module 12 — Minimal Frontend Evolution

**Goal:** relabel/extend existing UI surfaces, don't rebuild.
- "Top Priority Fee Discrepancies" → Agent Priority Queue (now group-level, not row-level)
- "LLM Diagnostic Verdict" → Agent Diagnosis + Reasoning (per group)
- "Stage Dispute" → "Stage Remediation / Stage Action" (relabel — critical fix, avoids implying auto-filing)
- "Exceptions & Ambiguities" → Human Review Queue (no functional change, framing only)
- Add: Agent Control Status card (open/improving/awaiting-action/escalated/new counts), Agent Recommendation card (per top case), Control Effectiveness card (baseline vs current vs % reduction).
- **Exit check:** all additions are additive to existing dashboard, nothing removed, no visual rebuild.

---

## Module 13 — Evaluation Framework

**Goal:** real, measured metrics — not fabricated ones.
- Ensure the 500-row synthetic dataset has known ground-truth labels (from your Module 1 injection logic) to score against.
- Compute and log: records processed, throughput, classification accuracy, leakage precision/recall, false-positive rate, ₹ estimation error, exception count, case closure/improvement rate.
- **Exit check:** every number in your final pitch traces to an actual computed metric, reproducible on demand.

---

## Module 14 — Demo Assembly (supersedes/extends original Module 9)

**Goal:** demonstrate one full control lifecycle, not a feature tour.
- Script: upload batch 1 → agent investigates/groups/prioritizes → top case (R11-style) created with recommendation → (simulate time passing) upload batch 2 → agent verifies control effectiveness → case moves to IMPROVED.
- Reuse pitch structure/persona work from original Module 9 where still applicable; update "what we built" and architecture diagram to reflect the new agent layer.
- **Exit check:** the full lifecycle can be demoed live, start to finish, within your pitch time budget.

---

## Explicitly out of scope (do not build)

Generic AI CFO features, payroll, invoicing, GST/accounting, generic cash forecasting, unrelated bank reconciliation, live production Razorpay integration, real payment routing execution, real autonomous dispute submission, live BIN lookup dependency, multi-PSP optimization.

---

## Suggested build order if time is short

1. Module 7.5 (prerequisite)
2. Module 8.1 → 8.2 → 8.3 → 8.4 (agent core — this is the heart of the deviation)
3. Module 9 (Control Case) — needed to demonstrate "not a report generator"
4. Module 11 (approval boundary) — cheap to add, protects credibility
5. Module 12 (frontend relabel/additions) — needed to *show* any of the above
6. Module 10 (baseline/effectiveness) — needed for the full lifecycle story
7. Module 13 (evaluation) — needed for Track 4's measurability requirement
8. Module 14 (demo) — always last

If truly time-constrained, Module 10 (multi-batch verification) is the most cuttable — a strong single-batch investigate→prioritize→recommend→case demo is still a legitimate, compelling submission even without a second-batch verification pass, though it's a materially weaker story than the full loop.