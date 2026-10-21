# AgentThree · Hands-On AI Architecture Lab

Governed **small-business lending assistant**: the model writes, deterministic code decides, humans sign off over $250k, and every answer is cited. Same design maps to AWS, Azure, or GCP.

Companion browser lab: [Hands-On AI Architecture Lab](https://agentthree.ai/ai-engineering-lab/ai-architect-hands-on) · storyboard in [`web/index.html`](web/index.html)

**How to run:** [How_to_Run_Demo.md](./How_to_Run_Demo.md)

> **$0 cloud. All runs are simulated.** This repo does **not** call AWS, Azure, GCP, Anthropic, or OpenAI.
>
> - No cloud account, credentials, or SDK (`boto3`, Azure/GCP clients)
> - No `terraform apply`
> - Python CLI and pytest never leave the machine
> - The HTML lab defaults to **SIMULATED · zero cost**. Pasting an Anthropic key in the page is optional demo-only and is **not** required to build or verify.

Prequal math, BM25 retrieval, the critic/eval gate, and the model router all run locally against fixture policy (`LP-101`–`LP-110`).

---

## Status

[![Verify](https://github.com/nickgulrajani/agentthree-ai-architect-lab/actions/workflows/verify.yml/badge.svg)](https://github.com/nickgulrajani/agentthree-ai-architect-lab/actions/workflows/verify.yml)

**Last verified:** 2026-10-21 · 9 pytest green · suite via [`make verify`](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio#verify-everything) in the [AI Engineering Portfolio](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio) monorepo.

## Implementation status

| Area | Status | Notes |
|------|--------|-------|
| Prequalification tool | **Implemented (local)** | DSCR, credit, revenue, amount — numbers never from an LLM |
| Guardrails | **Implemented (local)** | PII redaction + prompt-injection block |
| Retrieval | **Implemented (local BM25)** | Policy corpus `LP-101`–`LP-110` |
| Critic / HITL | **Implemented (local)** | Citations, ECOA adverse action, $250k underwriter pause |
| Model router | **Implemented (catalog math)** | Private endpoint when PII is on; no live provider calls |
| Eval gate | **Implemented (10 cases)** | Merge allowed at ≥90% |
| HTML storyboard | **Implemented (static)** | `web/index.html` — no backend |
| Live Claude / Bedrock / Vertex | **Not required** | Optional browser key only; Python path never uses it |

**Simulated vs cloud:** Lending decisions, routing, and the CI gate are real code on fixtures. There is **no cloud bill** for `make verify`.

Architecture: [docs/architecture.md](docs/architecture.md)

---

## Quick start (local, free)

```bash
make verify                 # venv, pytest, CLI demo
agentthree-architect serve  # HTML lab at http://127.0.0.1:8767/
```

## What the CLI proves

```text
Strong applicant            →  PREQUALIFIED
Injection                   →  blocked (no draft node)
PII + $400k request         →  redacted SSN/email · HITL queued
Weak DSCR                   →  NOT PREQUALIFIED + LP-106
Router with PII on          →  private endpoint only
Eval suite                  →  ≥9/10 · MERGE ALLOWED
```

## Layout

```
src/agentthree_ai_architect/   # prequal, guardrails, BM25, router, evals
tests/                         # 9 pytest cases
web/index.html                 # original simulation
.github/workflows/             # pytest + CLI demo
```

## License

[MIT](./LICENSE) — Copyright (c) 2026 AgentThree / Nicholas Gulrajani.
