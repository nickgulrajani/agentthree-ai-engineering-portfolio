# Architecture — simulated vs AWS

This lab proves the **control plane** of FinOps for an illustrative card issuer: see spend, allocate it, gate untagged deploys, then project savings.

Nothing here creates, starts, stops, or bills an AWS resource.

## What runs locally

```
Fixture CUR  →  tag coverage + showback  →  policy gate on plan JSON  →  savings math
     │                    │                         │                      │
 data/*.yaml         engine.py                  policy.py              optimize.py
```

Companion UI: `web/index.html` (the original simulation). CLI: `agentthree-finops demo`.

## What production would use (not deployed)

| Lab step | Simulated here | AWS / OSS analogue |
|----------|----------------|--------------------|
| 01 See | `configs/finops.yaml` monthly/service/trend | CUR 2.0, Athena, Cost Explorer |
| 02 Allocate | `data/untagged.yaml` + tag apply | Resource Groups Tagging API, cost allocation tags |
| 03 Guard | Python + `policy/**/*.rego` | OPA/Conftest on `terraform plan -json` |
| 04 Enforce | `data/plans/*.json` + GitHub Actions | GitHub Actions + Infracost + OIDC (no stored keys) |
| 05 Optimize | `data/recommendations.yaml` | Compute Optimizer, Cloud Custodian (dry-run first) |

## What never happens in this repo

- `terraform apply`
- AWS CLI / boto3 / Cost Explorer API
- Lambda, EventBridge, or Cloud Custodian against a live account
- Savings Plans or Reserved Instance **purchases**

Optional `opa test policy/` runs the same Rego the HTML lab shows. Python tests always run so the demo stays $0 even without OPA installed.
