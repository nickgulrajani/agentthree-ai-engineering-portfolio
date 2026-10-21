# Agent Three — AI Engineering Portfolio

[![Portfolio Verify](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio/actions/workflows/verify.yml/badge.svg)](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio/actions/workflows/verify.yml)

Monorepo portfolio of Agent Three AI engineering projects: agentic systems, enterprise RAG, agent evaluation, confidential AI, DevSecOps, and multi-cloud zero trust.

Website: [agentthree.ai](https://agentthree.ai/)

## Start here

**Flagship project:** [Healthcare Multi-Agent Prior Authorization](./agentthree-prior-auth/) (`agentthree-prior-auth/`)

Open that folder first — ADK · MCP · A2A · Gemini · human-in-the-loop, with a Live Run UI, published evaluation results (5/5 outcome accuracy), and 21 pytest cases. Then browse the rest.

```bash
cd agentthree-prior-auth
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -q
python -m evaluation.run_eval
```

Lab: [agentthree.ai/solutions/agentic-ai](https://agentthree.ai/solutions/agentic-ai)

## Projects in this repository

| Project | Path | Lab on agentthree.ai | Tests |
|---------|------|----------------------|------:|
| Healthcare Multi-Agent AI | [`agentthree-prior-auth/`](./agentthree-prior-auth) | [Prior Authorization](https://agentthree.ai/solutions/agentic-ai) | 21 |
| Confidential AI | [`agentthree-confidential-ai/`](./agentthree-confidential-ai) | [Confidential Computing](https://agentthree.ai/solutions/confidential-computing) | 8 |
| Multi-Cloud Zero Trust | [`agentthree-multicloud-zero-trust/`](./agentthree-multicloud-zero-trust) | [Multi-Cloud AI](https://agentthree.ai/solutions/multi-cloud-ai) | 33 (15 pytest + Rego + Terraform) |
| Enterprise RAG | [`agentthree-enterprise-rag/`](./agentthree-enterprise-rag) | [RAG Engineering](https://agentthree.ai/ai-engineering-lab/rag-engineering) | 8 |
| AI DevSecOps & Governance | [`agentthree-ai-devsecops/`](./agentthree-ai-devsecops) | [OPA Anomaly Lab](https://agentthree.ai/solutions/opa-anomaly-detection) | 14 |
| Agent Evaluation | [`agentthree-agent-eval/`](./agentthree-agent-eval) | [Agent Evaluation](https://agentthree.ai/ai-engineering-lab/agent-evaluation) | 7 |

Test counts: pytest (and for Zero Trust, Rego + integration + Terraform mock-provider when those tools are installed). Agent Evaluation also runs a published A/B gate via `python -m evaluation.run_eval`.

## Verify everything

```bash
git clone https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio.git
cd agentthree-ai-engineering-portfolio
make verify
```

One command runs each project's test suite. Zero Trust **skips** allow/deny tests with a clear install hint if [OPA](https://www.openpolicyagent.org/docs/latest/#running-opa) is missing:

- **macOS:** `brew install opa`
- **Linux:** `curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64_static && chmod +x opa && sudo mv opa /usr/local/bin/opa`

CI runs the same `make verify` on every push, pull request, and a nightly schedule (see the badge above). Runs show on the [Actions](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio/actions) tab; they do not create git commits.

## Clone

```bash
git clone https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio.git
cd agentthree-ai-engineering-portfolio
```

Open any project folder for its README, architecture notes, implementation status (simulated vs cloud), and reproducible tests.

## License

[MIT](./LICENSE) — Copyright (c) 2026 AgentThree / Nicholas Gulrajani. Each project directory also includes a `LICENSE`.

## Standalone mirrors (optional)

The same projects also exist as individual GitHub repositories for focused cloning. This portfolio repo is the canonical browsable collection—and matches the six Featured Labs on [agentthree.ai](https://agentthree.ai/).

| Project | Standalone repo |
|---------|-----------------|
| Healthcare Multi-Agent AI | [agentthree-prior-auth](https://github.com/nickgulrajani/agentthree-prior-auth) |
| Confidential AI | [agentthree-confidential-ai](https://github.com/nickgulrajani/agentthree-confidential-ai) |
| Multi-Cloud Zero Trust | [agentthree-multicloud-zero-trust](https://github.com/nickgulrajani/agentthree-multicloud-zero-trust) |
| Enterprise RAG | [agentthree-enterprise-rag](https://github.com/nickgulrajani/agentthree-enterprise-rag) |
| AI DevSecOps & Governance | [agentthree-ai-devsecops](https://github.com/nickgulrajani/agentthree-ai-devsecops) |
| Agent Evaluation | [agentthree-agent-eval](https://github.com/nickgulrajani/agentthree-agent-eval) |

## Activity

Daily changelog for this monorepo (newest first). Each day work lands, add a dated bullet here.

- **2026-10-21** — Nightly GitHub Actions health checks: portfolio `make verify` plus per-project CI on the standalone mirrors (pytest/eval, and frontend lint/build where a UI exists). Same real suites; no dummy commits.
- **2026-10-18** — Homepage / site references re-synced to portfolio table (test counts, Start here 21 pytest + 5/5 eval, standalone mirror links); Azure Zero Trust demo Use Case tab for parity with AWS/GCP.
- **2026-10-18** — Fix demo CDS regression: citation allow-list from guideline **and** policy hits + POL-AHP corpus ids; no-fault cases assert `unsupported == 0`; `set -euo pipefail` on every `verify-all` project block so failing pytest cannot be masked by a later command. Prior-auth pytest 21.
- **2026-10-18** — CI/drill follow-ups: `opa test` no longer uses invalid `-q` (Rego suite fails closed in `verify-all`); DevSecOps deploy dry-run only on `workflow_dispatch` so push/PR stays green with approval default false; prior-auth `grounding_fail` injects a real uncited claim before the citation filter. Prior-auth pytest 18.
- **2026-10-18** — Closed flagship caveats: prior-auth real A2A POSTs + MCP `set_fault` drills + async Gemini + decision `409`; RAG unknown classifications fail closed; Zero Trust audit append/resume + `list_datasets` entitlement filter; DevSecOps Trivy exit-code `1` + prod approval default `false`. Test counts: prior-auth 16 · RAG 8 · Zero Trust 33 (15 pytest + Rego + Terraform).
- **2026-10-17** — Homepage Featured Labs ↔ portfolio 1:1 (six labs / six projects); Agent Evaluation sixth project; Zero Trust test count clarified (13 pytest + Rego + Terraform).
- **2026-10-17** — Portfolio verify CI live; OPA-missing tests skip cleanly; MIT LICENSE on all projects; Start here → prior-auth.
