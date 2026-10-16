# Agent Three — AI Engineering Portfolio

Monorepo portfolio of Agent Three AI engineering projects: agentic systems, enterprise RAG, confidential AI, DevSecOps, and multi-cloud zero trust.

Website: [agentthree.ai](https://agentthree.ai/)

## Projects in this repository

| Project | Path | Description | Tests |
|---------|------|-------------|------:|
| Healthcare Multi-Agent AI | [`agentthree-prior-auth/`](./agentthree-prior-auth) | Prior auth with ADK, MCP, A2A, Gemini, HITL | 15 |
| Confidential AI | [`agentthree-confidential-ai/`](./agentthree-confidential-ai) | Attestation, IAM, KMS, trusted workloads | 5 |
| Multi-Cloud Zero Trust | [`agentthree-multicloud-zero-trust/`](./agentthree-multicloud-zero-trust) | Workload identity, MCP auth, OPA, A2A trust | 31 |
| Enterprise RAG | [`agentthree-enterprise-rag/`](./agentthree-enterprise-rag) | Hybrid search, ACLs, citations, grounding | 7 |
| AI DevSecOps & Governance | [`agentthree-ai-devsecops/`](./agentthree-ai-devsecops) | CI/CD, security scanning, evaluation gates | 14 |

Test counts: pytest (and for Zero Trust, Rego + integration + Terraform mock-provider). Re-run each project's test target after cloning.

## Clone

```bash
git clone https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio.git
cd agentthree-ai-engineering-portfolio
```

Open any project folder above for its README, architecture notes, implementation status (simulated vs cloud), and reproducible tests.

## Standalone mirrors (optional)

The same projects also exist as individual GitHub repositories for focused cloning. This portfolio repo is the canonical browsable collection.
