# InterDrift: Architecture, Workflow & Agentic Evaluation

---

## 1. End-to-End System Workflow

```
[CSV Upload]
     │
     ▼
[1. Deterministic Audit Engine] ──(Rules R1-R10 + Merchant MSA)
     │ ── Row-level classification: COMPLIANT, LEAKAGE, EXCEPTION, FLAGGED
     │ ── Mathematical output: exact ₹ delta, overcharge totals, structured reports
     │
     ▼
[2. Anomaly Clustering & Investigation] ──(Module 8.2)
     │ ── Groups hundreds of individual rows into root-cause patterns (e.g., GRP_LEAKED_R2)
     │
     ▼
[3. Deterministic Priority Engine] ──(Module 8.3)
     │ ── Scores groups using a 4-factor formula (₹ Exposure, Breach Severity, Frequency, Velocity)
     │ ── Ranks issues objectively (0 to 100)
     │
     ▼
[4. Multi-Route LLM Diagnostic Engine] ──(Module 8.4)
     │ ── Gemini Flash ➔ Groq Fallback ➔ OpenRouter ➔ Deterministic Fallback
     │ ── Diagnoses *why* the pattern occurred and maps it to a single standardized action
     │
     ▼
[5. Stateful Case Management] ──(Module 9)
     │ ── Instantiates trackable cases (`OPEN` ➔ `INVESTIGATING` ➔ `AWAITING_HUMAN_APPROVAL`)
     │ ── Persisted to `control_cases.json`
     │
     ▼
[6. Human Approval Boundary (Gatekeeper)] ──(Module 11)
     │ ── Consequential actions (Refunds, Disputes, Repricing) BLOCKED until explicit human click
     │ ── Low-risk actions (Config audits, log reviews) run autonomously
     │
     ▼
[7. Multi-Batch Baseline & Effectiveness] ──(Module 10)
     │ ── Locks initial audit snapshot
     │ ── On subsequent batch uploads: calculates % fee recovery and issues an effectiveness verdict
     │
     ▼
[Execution Completes / System Idle]
```

---

## 2. When Does the Project Stop?

The automated pipeline executes asynchronously and **stops (enters idle state)** at two distinct checkpoints:

1. **Post-Upload Processing Completion:** 
   Immediately after grouping, ranking, LLM diagnosis, case instantiation, and report persistence are complete (typically 1–3 seconds with caching/Groq). The server logs completion and waits for client requests.
2. **The Human-in-the-Loop Approval Boundary:**
   The agent **never auto-executes financial actions** (e.g., submitting MDR refund claims to banks or filing disputes). It stops and waits in state `AWAITING_HUMAN_APPROVAL` until a merchant controller clicks **Approve** or **Reject** on the UI.

---

## 3. Role of AI: Where It Acts, Features & Hard Limits

### Where AI Operates:
- **Root-Cause Synthesis:** Converts numeric anomaly clusters into human-readable merchant diagnostics explaining *why* the fee discrepancy occurred (e.g., identifying acquirer misconfiguration vs. missing metadata).
- **Remediation Recommendation:** Selects the precise corrective action from an allowed vocabulary (`request_mdr_refund`, `file_regulatory_dispute`, `correct_mcc_mapping`, etc.).
- **Row-Level Plain Explanations:** Formulates contextual notes for non-technical finance teams.

### Features & Resilience:
- **Multi-Route Fallback Cascade:** Gemini ➔ Groq (`qwen/qwen3.6-27b`) ➔ OpenRouter ➔ Rule-based fallback (zero crashes if API limits are hit).
- **Group-Level Batching & Local Caching:** Diagnoses whole clusters rather than thousands of individual rows, keeping token usage minimal and responses sub-second.

### What AI is STRICTLY FORBIDDEN from Doing (Hard Guardrails):
- **No Financial Calculations:** The LLM **never calculates fees, deltas, or overcharge sums**. All arithmetic belongs solely to the Python Deterministic Rules Engine (Modules 1–7).
- **Honesty & Zero-Hallucination Constraint:** Unclassified exceptions (e.g., missing interchange metadata) have expected fee set to ₹0.00 and delta to ₹0.00. The AI is prevented from fabricating an overcharge or claiming phantom refunds on missing data.

---

## 4. Is This Project Truly "Agentic"?

**Yes — it qualifies as a Constrained Autonomous Supervisory Agent.**

### Why it is Agentic:
1. **Perception-to-Action Loop:** It ingests unstructured/semi-structured settlement data, perceives systematic patterns, establishes internal state, prioritizes based on multi-factor utility, and synthesizes action plans.
2. **Stateful Memory & Lifecycle Control:** Rather than functioning as a one-shot stateless chatbot prompt, it instantiates persistent cases (`control_cases.json`) with finite state machine transitions (`OPEN` ➔ `ACTION_RECOMMENDED` ➔ `MONITORING` ➔ `IMPROVED` / `CLOSED`).
3. **Closed-Loop Effectiveness Verification:** It captures baseline snapshots and autonomously evaluates multi-batch performance to answer: *"Did the recommended remediation actually reduce fee leakage in the next settlement?"*
4. **Safety-Gated Agency:** Like autonomous systems in medicine or high-stakes finance, true agency requires safety bounds. Consequential actions require human gating, while benign monitoring actions proceed autonomously.

---

## 5. Purpose, Practical Value & Justification

### The Core Problem:
Indian merchants processing volume via payment gateways (Razorpay, Cashfree, Pine Labs) lose **0.2% to 1.8% of top-line revenue** to subtle settlement leakage:
- Acquirers violating RBI MDR caps on RuPay debit cards (mandated 0.00%).
- Non-compliant Interchange++ surcharges on UPI transactions.
- Processors billing Premium/Corporate card interchange rates on standard consumer cards.
- MCC misclassifications causing excessive statutory interchange fees.

### Why Manual Spreadsheets Fail:
Settlement files contain hundreds of thousands of rows with convoluted fee codes. Finance teams do not have the time or technical interchange rate tables to verify every transaction line by line.

### How InterDrift Solves This:
- **Instant Mathematical Verification:** Audits 10,000+ settlement rows in seconds against codified RBI mandates and merchant agreements.
- **Actionable Financial Recovery:** Instead of handing finance teams a raw list of 500 error rows, it aggregates them into 5 prioritized cases with ready-to-dispatch claim dossiers.
- **Continuous Margin Protection:** Ensures merchant margins are safeguarded month-over-month through multi-batch drift tracking.
