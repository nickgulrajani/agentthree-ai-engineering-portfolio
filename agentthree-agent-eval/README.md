# AgentThree · Agent Evaluation

Offline evaluation harness for agent configurations: a **40-task suite**, seeded trajectory simulation, scorecard metrics (success, tool/argument accuracy, pass^k, latency, cost), and a **regression gate** that decides whether candidate B ships over baseline A.

Companion browser lab: [Agent Evaluation · Module 07](https://agentthree.ai/ai-engineering-lab/agent-evaluation)

> **Non-billable portfolio demo.** No LLM API keys. Metrics come from a deterministic seeded simulator — the same patterns you wire into CI with real traces later.

---

## Status

**Last verified:** 2026-10-17 · suite green via [`make verify`](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio#verify-everything) in the [AI Engineering Portfolio](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio) monorepo.

## Implementation status

| Area | Status | Notes |
|------|--------|-------|
| 40-task golden suite (5 categories) | **Implemented** | Status, refund, billing, troubleshooting, adversarial |
| Seeded agent simulator | **Implemented (local)** | Model / planning / tool-description / retry knobs |
| Scorecard metrics | **Implemented** | Success, pass^k, tool & arg accuracy, p50/p95, cost |
| Regression gate | **Implemented** | Thresholds + no category regresses > 5 pts |
| Live LLM / LangSmith / Bedrock Evaluations | **Not deployed** | Documented production mapping only |

**Simulated vs cloud:** The harness is fully runnable offline. Production systems store traces and scores over time (Vertex Gen AI evaluation, Bedrock Evaluations, LangSmith, Ragas); this repo proves the gate logic without those bills.

---

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest -q
python -m evaluation.run_eval
# or: agentthree-agent-eval --thresholds evaluation/thresholds.yaml
```

Expected: pytest green; eval prints a scorecard and **PASS — ship B** for the default A/B configs (seed=7, trials=3).

---

## What gets measured

| Metric | Why it matters |
|--------|----------------|
| Task success | Outcome check — was the refund issued? Was the injection refused? |
| Tool / argument accuracy | Right tool, right args vs the reference trajectory |
| pass^k (consistency) | Share of tasks solved in *all* k trials — agents are stochastic |
| p95 latency & cost / success | Tail latency and cost of *successful* work, not just means |

Default gate (`evaluation/thresholds.yaml`): success ≥ 70%, p95 ≤ 16s, cost/task ≤ $0.08, no category regresses more than 5 points vs baseline.

---

## Architecture

```text
 Task suite (YAML-shaped Python)  →  Seeded simulator (config A / B)
                                              │
                                              ▼
                                   Scorecard (success · tools · latency · cost)
                                              │
                                              ▼
                                   Regression gate → PASS ship B / FAIL keep A
```

Lab: [agentthree.ai/ai-engineering-lab/agent-evaluation](https://agentthree.ai/ai-engineering-lab/agent-evaluation)

---

## License

[MIT](./LICENSE) — Copyright (c) 2026 AgentThree / Nicholas Gulrajani.
