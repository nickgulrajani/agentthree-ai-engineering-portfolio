# AgentThree · AI DevSecOps & Model Governance

Zero-billing pipeline that turns the Azure DevOps CI/CD **simulator** into **real gates**: Terraform validation, Checkov, pytest, MCP contract tests, agent evaluations, container scanning, deployment approvals, and rollback dry-runs.

**No cloud apply. No registry push. No LLM API calls in CI.**

Companion storyboard: [`agentthree_azure_devops_multicloud_cicd_simulator_v2.html`](../agentthree-website/agentthree_azure_devops_multicloud_cicd_simulator_v2.html) in the website repo.

---

## Implementation status

| Area | Status | Notes |
|------|--------|-------|
| Gate pipeline (pytest, Checkov, MCP contracts, eval fixtures) | **Implemented (local + CI)** | Runs via `make` / `scripts/run-gates.sh` and GitHub Actions |
| Terraform | **Validate only** | `fmt` + `validate` — never `apply` |
| Container scan (Trivy) | **Implemented (filesystem scan)** | No registry push |
| Deploy / rollback | **Simulated dry-run** | Manifests + health → rollback procedure; no AKS/GKE/EKS |
| Approvals | **Local flag + optional GitHub Environment** | Not a live Azure DevOps org |
| Cloud infrastructure | **Not deployed** | Simulator mapping only — see [docs/architecture.md](docs/architecture.md) |

**Simulated vs cloud:** Security and evaluation *gates* are real and reproducible. Cloud *deployments* are intentionally simulated so the demo stays at $0.

Architecture diagram: [docs/architecture.md](docs/architecture.md)

---

## What this proves

| Gate | How (free) |
|------|------------|
| Terraform validation | `fmt` + `validate` only |
| Checkov | Scans `infra/secure` vs deliberate `infra/insecure` |
| pytest | Unit + approval/rollback helpers |
| MCP contract tests | Schema, allowlist, deny-by-default auth |
| Agent evaluations | Offline golden fixtures + thresholds |
| Container scanning | Trivy filesystem scan (CI); optional locally |
| Deployment approvals | `PROD_APPROVED` / optional GitHub Environment |
| Rollback | Dry-run restore of previous revision on bad health |

**Demo blockers**

1. Insecure Terraform → Checkov fails → deploy skipped  
2. Failed grounding eval (`0.82 < 0.90`) → promotion blocked  
3. High canary error rate → rollback dry-run  

---

## Quick start

```bash
chmod +x scripts/run-gates.sh
make setup
make pass              # full green path
make fail-checkov      # shows Checkov block
make fail-eval         # shows grounding block
make fail-health       # shows rollback dry-run
```

Or one shot:

```bash
./scripts/run-gates.sh pass
./scripts/run-gates.sh fail-checkov
./scripts/run-gates.sh fail-eval
```

### Reproducible tests

```bash
make setup
pytest -q                 # unit + MCP + eval + approval helpers
./scripts/run-gates.sh pass
```

Expected: all pytest cases green; `pass` scenario exits 0 with Checkov/eval/approval evidence written under `artifacts/` (when present).

Optional tools (CI installs them; local optional):

- [Terraform](https://developer.hashicorp.com/terraform/install) — skipped if missing; Checkov still scans `.tf`
- [Trivy](https://trivy.dev/) — set `SKIP_TRIVY=1` to skip locally

---

## Layout

```
infra/secure/          # passes focused Checkov set
infra/insecure/        # deliberate public S3 + open SG
src/agentthree_devsecops/
  mcp_contract.py      # MCP allowlist + auth
  evaluation.py        # offline grounding gate
  deploy_dry_run.py    # approval + dry-run manifest
  rollback.py          # health → rollback procedure
evaluation/fixtures/   # pass_grounding / fail_grounding
tests/                 # pytest + MCP + eval + approval
scripts/run-gates.sh   # one-command local pipeline
.github/workflows/     # real CI, still $0
```

See [DEMO.md](DEMO.md) for a 60-second walkthrough.
