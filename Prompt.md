# BRIEFING CHUNK 4 of N (FINAL) — Audit Lens, Research Directive, Output Format, and Instruction to Begin

## Your research directive (do this before/alongside the audit)

Independently research Razorpay Buildathon Track 4 ("AI Finance Controller") — its actual stated scope, example directions, and evaluation criteria, from Razorpay's own current materials. Do not rely solely on the summary given to you in earlier chunks; verify it. Specifically determine: what does "closing one finance-ops loop" mean in their own words, what does an "honest exception list" and "audit trail" imply for judging, and what does "using AI appropriately, deterministic where AI is unnecessary" imply for how this project should be architected and demoed. Note any place where your research contradicts or refines something stated in earlier chunks — flag it explicitly rather than silently overriding it.

## The audit — apply all of the following lenses to the actual codebase, data, and running output. Investigate for real; do not speculate where you can verify.

**As a senior developer:** review code correctness, especially around the three known issues in Chunk 3 — find exact root causes, not just symptoms. Check for null-handling, floating-point comparison tolerance, silent fallback/exception-swallowing patterns, and any other latent bugs across the full pipeline (data generation → rules engine → LLM layer → agent layer → API → frontend).

**As a financial/data auditor:** verify that every number a merchant would see (leaked ₹, match rate, structural overcharge, case exposure) is actually traceable to a correct calculation, with no rounding, unit (%, ₹), or aggregation errors. Check that illustrative vs. sourced rules are never conflated in any output.

**As a systems architect:** assess whether the deterministic-engine-decides / agent-only-investigates boundary is actually enforced in code, not just in design intent. Check whether the human-approval gating is real (i.e., no code path can bypass it) or currently just a UI label. Assess whether the multi-routing LLM solution is architecturally sound and will hold up under demo conditions.

**As the merchant end user:** walk through the actual frontend as a non-technical business owner would. Is the exceptions section genuinely reassuring/honest, or does it (per known issue 1/2) currently look broken or confusing? Is "Stage Remediation" clearly not an auto-filed dispute? Would the priority queue and case tracking make sense without further explanation?

**As a Razorpay Track 4 judge:** using your research above, assess whether the current build, as it actually behaves right now (not as designed), would hold up to scrutiny — does it demonstrate one well-closed loop, an honest exception list, a real audit trail, and appropriate (not decorative) AI usage? Identify any gap between the intended design (per Chunks 1–3) and the actual current behavior that would hurt this specific evaluation.

## Output format for `implementation_plan.md`

Structure as: (1) Executive summary — overall health assessment in a few sentences; (2) Confirmed findings — one entry per issue, each with: description, root cause, severity (Critical/High/Medium/Low), affected layer(s), evidence (specific file/line/data example); (3) Track 4 alignment assessment, citing your research; (4) Planned changes — one entry per finding, each with: proposed fix, why this approach, estimated scope (small/medium/large), and any risk of breaking currently-working functionality; (5) Explicitly out-of-scope / deferred items, with reasoning; (6) Open questions for the human, if any remain. Append each chunk's findings under clearly dated/numbered headers rather than overwriting previous sections — the document should read as a cumulative audit trail of its own.

## Hard constraints for this entire audit-and-planning phase

- Do not modify any code or data during this phase — investigation and planning only.
- Do not propose any change that would remove or weaken the honesty features (visible exceptions, sourced/illustrative labeling, human-approval gating) — you may propose making them stronger/more correct, never simpler-but-less-honest.
- Every proposed fix in the "Planned changes" section must state explicitly whether it risks touching currently-stable Modules 1–7 functionality, so the human can weigh risk before a later execution phase begins.
- You have latitude in how you organize and word your findings — you are not required to match the exact structure above rigidly if a clearer structure serves the same purpose better, but all six sections' content must be present in some form.

## Instruction

You now have full context. Begin your research and audit, and produce the first version of `implementation_plan.md` covering everything above. When done, stop and wait for review — do not proceed to any implementation.