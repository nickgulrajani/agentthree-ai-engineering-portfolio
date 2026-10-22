# AgentThree · AWS FinOps Lab

Local FinOps control plane for an **illustrative credit card issuer**: see spend, allocate it with a tag standard, block untagged Terraform plans, then project architecture savings.

Companion browser lab: [AWS FinOps Lab](https://agentthree.ai/ai-engineering-lab/aws-finops-lab) · storyboard in [`web/index.html`](web/index.html)

**How to run:** [How_to_Run_Demo.md](./How_to_Run_Demo.md)

> **$0 AWS. All data is simulated.** This repo does **not** call any AWS service.
>
> - No AWS account, credentials, or `AWS_PROFILE`
> - No **boto3**, AWS CLI, or SDK
> - No Cost Explorer APIs (`ce:GetCostAndUsage`, `ce:GetCostForecast`, …)
> - No CUR export, Athena, CloudWatch API, Compute Optimizer, or Cloud Custodian against a live account
> - No `terraform apply`
>
> Spend, tags, policy FAIL/PASS/WARN, and savings math come from local YAML/JSON fixtures. Names like “Cost Explorer” in the HTML lab are the **production mapping**, not live calls. See [docs/architecture.md](docs/architecture.md).

---

## Status

[![Verify](https://github.com/nickgulrajani/agentthree-aws-finops/actions/workflows/verify.yml/badge.svg)](https://github.com/nickgulrajani/agentthree-aws-finops/actions/workflows/verify.yml)

**Last verified:** 2026-10-21 · 8 pytest green · suite via [`make verify`](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio#verify-everything) in the [AI Engineering Portfolio](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio) monorepo. This repo also runs pytest, the CLI demo, and `opa test` on push, PR, and a nightly schedule.

## Implementation status

| Area | Status | Notes |
|------|--------|-------|
| Spend overview / unit cost | **Implemented (local fixtures)** | Oct 2026 $412.8k · $2.58 / 1k txns |
| Tag coverage + showback | **Implemented (local)** | 61% → 91% after applying the tag standard |
| OPA-style Terraform gates | **Implemented (Python + Rego)** | Missing tags, bad values, oversized non-prod |
| Infracost review threshold | **Implemented (fixture JSON)** | Warn above $1k/mo delta |
| Savings backlog | **Implemented (math only)** | $88k/mo if all recs selected → $324.8k run rate |
| HTML storyboard | **Implemented (static)** | `web/index.html` — no backend, no AWS |
| Live AWS / CUR / Cost Explorer | **Not deployed** | Documented production mapping only |
| Cloud Custodian / Savings Plans purchase | **Not deployed** | Would be billable — out of scope |

**Simulated vs cloud:** Coverage, gates, and savings math are real and tested against fixtures. There is **no boto3** and **no Cost Explorer (or other AWS) API call**. Accounts, SDKs, and applies are absent so the demo stays at **$0**.

Architecture: [docs/architecture.md](docs/architecture.md)

---

## Quick start (local, free)

Step-by-step: **[How_to_Run_Demo.md](./How_to_Run_Demo.md)** (also [DEMO.md](./DEMO.md) for a 60-second version).

```bash
make verify                 # creates .venv, pytest, CLI demo
make serve                  # HTML lab at http://127.0.0.1:8766/
# or: .venv/bin/agentthree-finops serve
```

## What the CLI proves

```text
Untagged Terraform plan     →  FAIL  (required tags / size / CostCenter format)
Fully tagged plan           →  PASS
Infracost +$1,387/mo        →  WARN  (FinOps review, not a cloud call)
Tag-all on fixture CUR      →  91% coverage (target 90%)
All savings recs selected   →  $412.8k → $324.8k  ·  $2.58 → $2.03 / 1k txns
```

Optional: `opa test policy/` if [OPA](https://www.openpolicyagent.org/docs/latest/#running-opa) is installed. CI installs it; locally it is skipped with a hint.

## Layout

```
configs/finops.yaml     # monthly spend, teams, thresholds
data/untagged.yaml      # CUR-shaped untagged inventory
data/recommendations.yaml
data/plans/             # terraform plan JSON fixtures
policy/                 # Rego (OPA) — same rules as the HTML lab
src/agentthree_aws_finops/
web/index.html          # original simulation
.github/workflows/      # pytest + demo + opa test
```

## License

[MIT](./LICENSE) — Copyright (c) 2026 AgentThree / Nicholas Gulrajani.
