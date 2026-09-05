AUDIT PROMPT 2 of 4 — Visible Agentic Behavior

Goal

Assess whether the frontend actually demonstrates agentic behavior — investigation, grouping, reasoning, decision-making, and a closed action loop — rather than just displaying static labels that claim agency. Investigate actual code/behavior, don't assume.

Specific things to check
Agent Orchestration Pipeline (currently: 5 static checkmarks, "Idle · 5/5 Steps Verified") — this doesn't show reasoning happening, just a fixed completion state. Determine: does the backend actually expose per-step data (timing, input/output, intermediate results) for Grouping/Prioritization/LLM Diagnosis/Case Lifecycle/Effectiveness? If yes, propose surfacing it — e.g., expandable steps showing what each stage actually did on this run (X transactions grouped into Y clusters, Z cases prioritized, N LLM calls made, etc.), not just a checkmark. If the backend doesn't expose this granularity, flag it as a backend gap, don't fabricate frontend-only detail.
Status badges (Monitoring/Action Ready/Escalated/Awaiting Approval) — after Audit 1's fix, clicking now filters the queue. Verify this alone is sufficient, or whether each status needs its own explanatory context when filtered (e.g., when viewing "Monitoring" cases, does the UI explain what baseline it's tracking against and current drift, not just list cases with that badge).
"Stage Remediation" button — currently just turns green with no visible downstream effect. This is the biggest gap: it should visibly close the agentic loop. Determine what actually should happen in the data model when this is clicked (per the ControlCase status lifecycle: does it move a case to AWAITING_HUMAN_APPROVAL or ACTION_RECOMMENDED → next state?), verify if that state change exists in the backend at all, and if so, wire the frontend to: (a) actually call the backend to update case status, (b) reflect the new status somewhere the user can see (e.g., the case now appears under a different Agent Control Status count, or shows an updated timeline/history on the case card itself).
Case → Transaction traceability — verify a user can click from a Priority Queue case down into the specific transactions that make up that case (the "orchestrated in the Agent Priority Queue above" language in Transaction Spotlights implies this relationship should be navigable, not just stated in text).
General sweep — identify any other place where the UI implies autonomous agent activity (words like "agent," "autonomous," "diagnostic") without actual visible mechanism behind it, or any other missing feedback loop that would make a judge doubt genuine agentic behavior versus a static report with agent-flavored labels.
Constraints
Do not fix anything yet — investigate and report only.
For each item: confirm what currently exists in code/data vs. what's just visual, and propose the minimal fix that makes the behavior real and visible without inventing new backend capabilities that don't exist (flag as a backend gap instead, for prioritization).
Output

Concise findings list. Stop after reporting.