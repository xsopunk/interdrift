# AUDIT PROMPT 1 of 4 — Visual & Content Completeness (Judge/Merchant POV)

## Context
This is the first of four sequential audit passes covering: (1) visual/content completeness, (2) visible agentic behavior, (3) backend rigor/correctness, (4) frontend-backend wiring. This pass covers #1 only. Investigate the actual running app and code — do not assume the screenshots are the full picture.

## Goal
Assess whether the frontend, as it currently renders, gives a judge or merchant (non-technical, no prior context) a complete, accurate, and honest picture of what the system does and found — purely from a content/visual-completeness standpoint. Do not address agentic-behavior visualization here (that's the next pass) — focus only on: is anything missing, unclear, inconsistent, or misleading in what's currently displayed.

## Specific things to check (from reviewing current screenshots — verify each against live app, don't assume screenshot is current state)

1. **Header/subtitle** — "Autonomous Payment Fee Controller · Audit, Recover & Prevent Leakage" — confirm this accurately reflects everything the system now does (investigation, grouping, prioritization, case tracking, effectiveness verification), not just audit/recover/prevent. Propose a better version if it undersells or overclaims.
2. **Agent Control Status counts (Monitoring / Action Ready / Escalated / Awaiting Approval)** — confirm each count is accurate against actual case data, and that clicking each status badge does something meaningful (see Prompt 2 for the deeper agentic-behavior fix — for this pass, just confirm/report current click behavior and whether counts themselves are correct).
3. **Fee Leakage by Rail** — confirm every listed rail (RuPay Credit on UPI Large/Small, PPI Wallet Large/Small, Commercial Card L2/L3) has consistent, correctly-labeled tags ("Statutory Gazette," "Modeled Benchmark") — verify these tags are being applied correctly per rule's actual `source_status`, not just visually plausible.
4. **Batch Structural Audits section** — only 2 cards shown (MCC Drift, Blended-MDR Spread) — confirm this is the full/correct set for the current dataset, not a truncated or stale view.
5. **Agent Priority Queue case cards** — confirm the visible tag combination (Rule ID + "Modeled Benchmark"/"Statutory Gazette" + status badge) is complete and non-redundant, and that the one-line description under each title is grounded to real case data (per earlier LLM-grounding fixes), not generic filler.
6. **Transaction Spotlights** — confirm the "10 Transaction Highlights" count matches what's actually displayed/available, and that every card's explanation text is transaction-specific (spot-check a few against raw data), not templated boilerplate.
7. **Row-Level Audit Trail** — confirm the "RULE & CITATION" column's secondary text (e.g., "Bank UPI (0% Statutory Cap)") is dynamically generated per rule, not hardcoded per the 5 rules currently visible — must generalize to any rule. Confirm filter tabs (All Records/Fee Leaks/Compliant/Flagged for Review/Exceptions) map correctly to actual classification values and each returns correct, non-overlapping results.
8. **Cross-page consistency** — confirm numbers that appear in multiple places (e.g., total exceptions count, total leaked amount, case counts) match exactly everywhere they're shown — no drift between the cockpit summary, the priority queue, and the audit trail.
9. **General sweep** — identify anything else incomplete, cut off, inconsistent, or confusing from a first-time viewer's perspective that isn't listed above, including anything below the fold not captured in these screenshots.

## Constraints
- Do not fix anything yet in this response — investigate and report only.
- For each item above: confirm correct, or report the specific issue with file/component reference and a proposed fix.
- Do not address the "how do we show agentic behavior better" question — that's Prompt 2, coming next.

## Output
Concise findings list, one entry per item, using this pass's numbering. Stop after reporting — do not implement.