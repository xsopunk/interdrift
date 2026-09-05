**PROMPT — Frontend Copy/Abstraction Pass**

**Objective (internalize this, don't just pattern-match the examples below):** every hardcoded and dynamic text on this frontend must be understandable by a merchant, a non-technical judge, and a technical judge with zero payments-domain knowledge — without needing to know what "R4," "MDR," "IC+," or "Blended-MDR" mean. Replace internal shorthand with plain, professional, self-explanatory language everywhere it appears — including places not shown below if you find the same pattern elsewhere (badges, tooltips, empty states, loading/status strings, error messages, chart labels, agent-generated status text templates). Never change layout, components, styling, or fonts — text content only.

**Specific findings in Frontend:**

**1 (Cockpit header):**
- Title "InterDrift — Interchange & Cost-of-Acceptance Autonomous Auditor" undersells current scope (it's now an agentic control system, not just an auditor). Propose a better subtitle reflecting investigate→prioritize→recommend→track→verify, not just "auditor."
- "Ingest settlement batches to execute deterministic regulatory rules (R1–R13) and multi-route agent control" — exposes internal rule-ID naming and "multi-route" (an implementation detail) to end users. Rewrite in outcome language.
- "Margin Regression (Leakage Up)" badge — "Margin Regression" is jargon; say what happened plainly.
- Card labels fine ("Direct Leakage," "Structural Spread," "Statutory Match Rate") but consider one-line tooltips/subtext if not already present, since "Structural Spread (R11)" still exposes a rule ID in the visible label.

**2 (Summary cards + rail breakdown + structural audits):**
- Every rail row shows a bare rule ID (R4, R6b, R10) as the primary label with no explanation — this is the single biggest abstraction gap on the page. Each rail needs a human-readable name (you already do this correctly in "MCC Drift Impact (R12)" and "Blended-MDR Spread (R11)" below — apply that same pattern here, rule ID as a small secondary tag, not the headline).
- "3 Rails Flagged," "Pre-negotiation audit," "Reclaimable" — check these read clearly to a layman; "Pre-negotiation audit" especially is unclear standalone.

**3 (Agent Priority Queue):**
- Case names are raw internal identifiers: "MCC_Misclassification," "Blended_vs_IC_Plus," "RuPay_Credit_UPI," "PPI_Wallet_UPI," "Credit_Cards_Market" — with underscores, clearly not written for display. Rewrite each as a real sentence/title a merchant would read naturally. Rule IDs (R12, R4, etc.) can stay as small secondary tags only.
- "Credit_Cards_Market" case says "flagged review pattern... against an illustrative benchmark with zero financial variance" — if the variance is genuinely zero, reconsider whether this belongs in a "Priority Queue" of financial findings at all, or should be labeled differently (e.g., informational, not actionable).

**4 (Transaction Spotlights):**
- Good section overall — "Agent Diagnostic Verdict" text is clear. Minor: "Rule R4" tag on each card still exposes the raw ID with no inline meaning; consider a hover/tooltip or short parenthetical.
- Confirm this pattern (rule ID + one-line plain explanation) is applied consistently to every card, not just the top ones.

**5 (Human Review Queue):**
- Very good already — "Honesty Constraint" framing and explanations are clear and merchant-readable. No major changes; check tone stays consistent with terminology fixes elsewhere.

**6 (Row-Level Audit Trail):**
- Column header "RULE" shows raw IDs (R2, R1, R6c, R8) with zero context — least abstracted section on the page. At minimum add a hover tooltip with the rule's plain description; ideally show a short human label inline or on expand.
- Filter tabs "Leaked / Matched / Exception / Flagged_For_Review" — "Flagged_For_Review" has a raw underscore, inconsistent with the polish elsewhere; fix casing/spacing.
- "SUB-INSTRUMENT" column values ("RuPay_debit," "bank_UPI," "PPI_wallet_UPI," "Debit_non_rupay") are raw internal enum values with underscores — reformat for display (e.g., "RuPay Debit," "Bank UPI," "PPI Wallet (UPI)," "Non-RuPay Debit").

**Process:** fix one finding at a time, in the order above (or your own reasonable prioritization if some share a root cause/component — note if so). After each fix, stop and output only: what changed, one-line confirmation it matches intent, and a short commit message. No verbose explanation. Proceed.