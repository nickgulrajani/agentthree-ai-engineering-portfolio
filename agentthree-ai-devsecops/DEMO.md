# 60-second demo script

Goal: show production engineering discipline — gates that **block**, not just architecture diagrams.

## Setup (once)

```bash
cd agentthree-ai-devsecops
chmod +x scripts/run-gates.sh
make setup
```

## 1. Green path (~15s)

```bash
make pass
```

Expect: pytest green → Checkov clean on `infra/secure` → grounding PASS → dry-run deploy → health OK.

## 2. Insecure Terraform blocks deploy (~10s)

```bash
./scripts/run-gates.sh fail-checkov
```

Expect: Checkov fails on public S3 / open security group → script exits non-zero **before** a trusted promotion.

Talking point: *“Same pipeline. Policy-as-code stops the bad change. We never `terraform apply`.”*

## 3. Failed grounding blocks promotion (~10s)

```bash
./scripts/run-gates.sh fail-eval
```

Expect: `grounding 0.82 < 0.90` (and related checks) → FAIL → deploy never runs.

Talking point: *“Model governance is a release gate, same as SAST.”*

## 4. Bad canary → rollback procedure (~10s)

```bash
./scripts/run-gates.sh fail-health
```

Expect: deploy dry-run succeeds, health fails at 8.1% error rate, `artifacts/rollback-result.json` shows restore to `rev-001`.

## Optional: GitHub Actions

- Push / PR runs quality · IaC · evaluation · Trivy (no deploy gate — approval defaults to false).
- **Actions → AI DevSecOps Pipeline → Run workflow** to exercise deploy dry-run + health/rollback.
- Choose scenario: `pass` / `fail-checkov` / `fail-eval` / `fail-health`
- Set **`approve_prod=true`** when you want the deploy dry-run to pass (default is `false` — the approval gate blocks).

To add a real human approval gate (still $0): repo **Settings → Environments → production → Required reviewers**, then add `environment: production` to the `deploy-dry-run` job.

## Pair with the simulator

Open the HTML lab and run matching scenarios (`Terraform Checkov policy violation`, `Agent evaluation below threshold`, `Production health check fails → rollback`) so architecture and evidence sit side by side.
