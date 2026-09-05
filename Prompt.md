# BRIEFING CHUNK 2 of N (FINAL) — Constraints & Instruction to Begin

## Constraints for this audit round

- You have full access to the codebase — inspect actual source files for the dashboard cards, the Control Effectiveness/Module 10 comparison logic, and wherever percentage/direction formatting happens. Do not guess at root causes without checking the code.
- Do not modify any code in this phase — investigation and planning only, same as prior rounds.
- Any proposed fix must clearly state the correct intended semantics before proposing a fix — e.g., explicitly define "for this metric, an increase means X, a decrease means Y, and the display should show Z" — so there's no ambiguity for the execution phase.
- If Issues B and C share a root cause (a general "improvement direction" bug applied to multiple metric types), propose a single, consistent fix approach across all affected cards rather than one-off patches per card — flag this explicitly if you find it's the case.
- Flag any fix that touches shared/stable formatting utilities or Modules 1–7, per the existing risk-flagging convention.

## Output format

Same cumulative structure as before — append a new dated section to `implementation_plan.md` with: confirmed findings (description, root cause, severity, affected layer, evidence), planned changes (fix, reasoning, scope, risk), and open questions if any remain.

## Instruction

Begin your investigation and audit now using the actual codebase. Produce the plan section as described. Stop when done — do not implement.