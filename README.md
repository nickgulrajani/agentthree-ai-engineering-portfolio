# Agent Three — AI Engineering Portfolio

[![Portfolio Verify](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio/actions/workflows/verify.yml/badge.svg)](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio/actions/workflows/verify.yml)

Monorepo portfolio of Agent Three AI engineering projects: agentic systems, enterprise RAG, confidential AI, DevSecOps, and multi-cloud zero trust.

Website: [agentthree.ai](https://agentthree.ai/)

## Start here

**Flagship project:** [Healthcare Multi-Agent Prior Authorization](./agentthree-prior-auth/) (`agentthree-prior-auth/`)

Open that folder first — ADK · MCP · A2A · Gemini · human-in-the-loop, with a Live Run UI, published evaluation results (5/5 outcome accuracy), and 15 pytest cases. Then browse the rest.

```bash
cd agentthree-prior-auth
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -q
python -m evaluation.run_eval
```

Lab: [agentthree.ai/solutions/agentic-ai](https://agentthree.ai/solutions/agentic-ai)

## Projects in this repository

| Project | Path | Description | Tests |
|---------|------|-------------|------:|
| Healthcare Multi-Agent AI | [`agentthree-prior-auth/`](./agentthree-prior-auth) | Prior auth with ADK, MCP, A2A, Gemini, HITL | 15 |
| Confidential AI | [`agentthree-confidential-ai/`](./agentthree-confidential-ai) | Attestation, IAM, KMS, trusted workloads | 8 |
| Multi-Cloud Zero Trust | [`agentthree-multicloud-zero-trust/`](./agentthree-multicloud-zero-trust) | Workload identity, MCP auth, OPA, A2A trust | 31 |
| Enterprise RAG | [`agentthree-enterprise-rag/`](./agentthree-enterprise-rag) | Hybrid search, ACLs, citations, grounding | 7 |
| AI DevSecOps & Governance | [`agentthree-ai-devsecops/`](./agentthree-ai-devsecops) | CI/CD, security scanning, evaluation gates | 14 |

Test counts: pytest (and for Zero Trust, Rego + integration + Terraform mock-provider when those tools are installed).

## Verify everything

```bash
git clone https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio.git
cd agentthree-ai-engineering-portfolio
make verify
```

One command runs each project's test suite. Zero Trust **skips** allow/deny tests with a clear install hint if [OPA](https://www.openpolicyagent.org/docs/latest/#running-opa) is missing:

- **macOS:** `brew install opa`
- **Linux:** `curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64_static && chmod +x opa && sudo mv opa /usr/local/bin/opa`

CI runs the same `make verify` on every push (see the badge above).

## Clone

```bash
git clone https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio.git
cd agentthree-ai-engineering-portfolio
```

Open any project folder for its README, architecture notes, implementation status (simulated vs cloud), and reproducible tests.

## License

[MIT](./LICENSE) — Copyright (c) 2026 AgentThree / Nicholas Gulrajani. Each project directory also includes a `LICENSE`.

## Standalone mirrors (optional)

The same projects also exist as individual GitHub repositories for focused cloning. This portfolio repo is the canonical browsable collection.

## Activity

- **2026-10-17** — Portfolio verify CI live; OPA-missing tests skip cleanly; MIT LICENSE on all projects; Start here → prior-auth.
