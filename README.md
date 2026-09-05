# InterDrift: Agentic Payment Fee Auditor

Autonomous fee auditing and leakage control agent for Indian merchants.

## Quickstart & Demo Setup

### 1. Pre-Warm Demo Cache (Important)
Before any judge-facing demo, run the pre-warming protocol to ensure all deterministic audit results and agent LLM diagnoses are cached in `data/processed/agent_cache/`:
```bash
python warm_cache.py
```
> **Demo Performance Note:** Pre-warming guarantees that all 11 control cases, investigation groupings, and LLM diagnoses load instantly (**< 0.3s runtime**), avoiding live network/rate-limiting latency during judging.

### 2. Cache Invalidation Risk Notice
The LLM diagnosis cache key in `src/agent/reasoning.py` incorporates `group_id`, `transaction_count`, and `total_exposure_inr`.
- **Benchmark Demo Dataset (`settlement_batch_01.csv`)**: 100% cached and safe.
- **New Dataset Upload Risk**: If an arbitrary new CSV is uploaded with different transaction counts or exposure amounts, it will generate new cache signatures and invoke uncached LLM calls. For live demo presentations, stick to the benchmark batch (`settlement_batch_01.csv`) or pre-warm any custom test batches in advance using `python warm_cache.py`.

### 3. Start Backend & Frontend
```bash
# Terminal 1 (Backend API):
uvicorn src.api.main:app --reload

# Terminal 2 (Frontend React App):
cd frontend && npm run dev
```
Open `http://localhost:5173` to view the dashboard.
