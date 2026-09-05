# AUDIT PROMPT 4 of 4 — Frontend-Backend Wiring & Full-Stack Integration

## Context
Final audit pass. Prior passes covered frontend content, visible agentic behavior, and backend correctness independently. This pass checks the **connective tissue**: is every backend capability actually reachable and correctly used from the frontend, and does every frontend feature actually work against real backend state (not stale/mocked/partial data)? Investigate live, running behavior — not just that both sides "look" complete in isolation.

## Goal
Confirm the full stack is genuinely wired end-to-end: every backend endpoint/capability built across all prior modules is exposed and functioning through the UI, and every UI element that implies a backend action actually performs it correctly.

## Specific things to check

1. **Endpoint inventory vs. UI usage** — list every backend API endpoint that currently exists (upload, results, report, monitor, cases, approve/reject, structural audits, exception details, rule evidence, contract terms, exposure calculation, test-data generation, MSA generation, etc.). For each, confirm: is it actually called from the frontend anywhere? If a working backend endpoint has zero frontend caller, flag it as an unused/orphaned capability — this may mean a feature was built but never surfaced, which matters given how much was built.

2. **UI actions vs. backend effect** — inversely, for every clickable action in the UI (Execute Audit, Lock Baseline, Select CSV, approve/reject on cases, status badge filters, Test Data Generator's "Run Audit with This Data," CSV export, any navigation added during Audit 2's fixes), confirm it actually triggers the correct backend call and the correct backend-side effect — not just a local state change that looks right.

3. **Post-fix regression check** — re-verify the fixes from Audits 1–3 are correctly wired together, since they touched overlapping files: confirm Stage Remediation → Case linkage (Audit 2, item 3/4) actually calls the real `/cases/{case_id}/approve`/`reject` endpoints and that the case's status change is reflected back in `AgentControlStatus` counts and the Priority Queue in real time (not just on next page reload, unless that's an accepted/documented limitation).

4. **Test Data Generator end-to-end path** — confirm the full flow works live: generate/upload dataset → generate/upload MSA → "Run Audit with This Data" → results actually reflect the custom data (not silently falling back to the default `settlement_batch_01.csv`). Test at least one non-default configuration (different transaction count, different injection rates, amount up to ₹1,00,000) and confirm the resulting dashboard numbers are internally consistent with that specific run, not leftover from a previous default run.

5. **Baseline/effectiveness live flow** — confirm the full multi-batch flow works end-to-end through the actual UI: lock a baseline, run a second batch (ideally via the Test Data Generator with different injection rates), and confirm the Control Effectiveness card updates correctly and consistently with what Audit 3 verified at the backend level.

6. **Error/failure states** — confirm the frontend handles backend failures gracefully: API server not running, malformed CSV upload, LLM provider failures (should fall back per the multi-route architecture, not surface a raw error to the user), empty/first-run states (no baseline yet, no cases yet). None of these should crash the UI or show a blank/broken screen.

7. **Data freshness / stale-state check** — confirm there's no scenario where the UI displays results from a previous run after a new one has completed (e.g., check for missing state resets, cached API responses not being invalidated after a new upload/audit run).

8. **Cross-check against original Track 4 intent** — using your own understanding of the project (and, if useful, Razorpay's actual Track 4 brief you researched earlier), confirm the full connected system actually delivers what was intended: a merchant/judge can upload or generate a batch, get an accurate audit with match rate and honest exceptions, see agent-driven investigation/prioritization/recommendation, approve an action, and verify improvement over time — entirely through the UI, with no step requiring direct API/backend access to demonstrate.

## Constraints
- Test live, running behavior — click through the actual app, don't just read code and infer.
- Do not fix anything in this pass — report only.
- For each item: pass/fail with specific evidence (what you clicked, what happened, what endpoint was/wasn't called). For any fail, root cause + proposed fix.

## Output
Concise findings list, numbered to match above. Stop after reporting — this is the final audit pass before consolidated fixes and final demo prep.