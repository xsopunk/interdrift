# AUDIT PROMPT 3 of 4 — Backend Rigor & Correctness

## Context
Two prior passes covered frontend content completeness and visible agentic behavior. This pass turns to the backend itself: does it compute, classify, and reason correctly and efficiently, matching what the project actually intends? Investigate the real code and run real tests against real/synthetic data — do not infer correctness from the frontend looking reasonable.

## Goal
Verify the backend delivers what was designed, accurately and efficiently, end to end: rule classification, batch structural audits, agent grouping/prioritization, LLM diagnosis, case lifecycle, and baseline/effectiveness comparison.

## Specific things to check

1. **Rule classification correctness (ground-truth check)** — the synthetic dataset generator injects known leak/exception patterns (`injected_issue` field or equivalent). Cross-check the rules engine's actual classification output against these known ground-truth labels across the full dataset, not a handful of rows. Report: how many known-injected leaks were correctly classified as Leaked, how many known-clean rows were correctly Matched, and how many genuinely-ambiguous rows were correctly left as Exception (not force-classified). Any mismatch is a real bug — find and report root cause, not just the count.

2. **Null vs. zero handling (previously flagged issue)** — confirm `expected_fee` and `delta` are properly null/undefined for Exception rows across the entire dataset now, not just spot-checked rows. Confirm this holds after the Test Data Generator feature was added (new code path, verify it wasn't reintroduced there).

3. **Rule precedence/conflict handling** — confirm the fix for "multiple rules matching a transaction" (explicit specificity sorting, not JSON-order-dependent) actually produces correct results across the full dataset, including edge cases at exact threshold boundaries (e.g., exactly ₹2,000, exactly ₹20L turnover).

4. **Floating-point tolerance** — confirm the Matched/Leaked boundary tolerance is applied consistently everywhere fee comparisons happen (per-row classification, batch structural audits, agent exposure calculations) — check for any place still doing exact equality comparison.

5. **Batch structural audits (R11/R12) correctness** — verify the Blended-MDR and MCC-misclassification aggregate calculations are mathematically correct against the actual dataset (recompute independently and compare), not just "produces a plausible-looking number."

6. **Agent grouping and prioritization** — verify groups are being formed on genuinely shared root causes (not just coincidentally similar rule IDs), and that the priority score formula (exposure × confidence × recurrence × controllability) is actually being computed as designed, not a placeholder/simplified stand-in. Report the actual formula/weights currently implemented.

7. **LLM diagnosis grounding and reliability** — confirm the multi-routing/grouped-call approach eliminated the original rate-limit failures (test with the full ~106-item flagged/exception set, report actual success rate). Confirm diagnoses are grounded to the specific group's real data (spot-check several against raw transactions) and that illustrative vs. sourced rules are still correctly distinguished in LLM output language.

8. **Case lifecycle correctness** — verify case status transitions (OPEN → INVESTIGATING → ACTION_RECOMMENDED → AWAITING_HUMAN_APPROVAL → MONITORING → IMPROVED/ESCALATED → CLOSED) actually follow the intended logic, and that the approve/reject endpoints correctly update state (tie this to Audit 2's Stage Remediation fix — confirm the wiring actually works backend-side, not just that the endpoint exists).

9. **Baseline/effectiveness comparison accuracy** — verify percent-change and improved/worsened/unchanged determinations are mathematically correct and consistently signed (this directly follows up on the earlier "+17.1%" / "-14.29%" direction-bug fixes — confirm those fixes are correct across all metrics, not just the ones originally flagged).

10. **Test Data Generator correctness** — verify the configurable injection rates (RuPay-credit-on-UPI leak rate, L2/L3 downgrade rate, MCC misclassification rate, exception rate) actually produce datasets matching the requested rates within reasonable statistical tolerance, and that the ₹1,00,000 amount range doesn't break turnover-tier-dependent rules (R7/R8) or any other range-dependent logic.

11. **Performance/efficiency** — report actual end-to-end processing time for a full 500-transaction batch (upload → classification → agent pipeline → case generation), and flag anything unexpectedly slow given the buildathon demo context.

## Constraints
- Investigate and test against real data — run actual code, don't estimate.
- Do not fix anything in this pass — report only.
- For each item: state pass/fail with evidence (actual numbers, specific examples), and for any fail, root cause + proposed fix.

## Output
Concise findings list, numbered to match above. Stop after reporting.