#!/usr/bin/env bash
# One-command local pipeline. Never applies cloud infrastructure. Exit non-zero on gate failure.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:-pass}"          # pass | fail-checkov | fail-eval | fail-health
SKIP_TRIVY="${SKIP_TRIVY:-0}"
SKIP_TERRAFORM="${SKIP_TERRAFORM:-0}"

RED=$'\033[31m'
GRN=$'\033[32m'
YLW=$'\033[33m'
RST=$'\033[0m'

step() { echo; echo "${YLW}==> $*${RST}"; }
ok()   { echo "${GRN}PASS${RST} $*"; }
fail() { echo "${RED}FAIL${RST} $*"; exit 1; }

if [[ ! -d .venv ]]; then
  step "Creating venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt
pip install -q -e .

step "pytest (unit + MCP contracts + evaluation gate tests)"
pytest -q

TF_DIR="infra/secure"
EVAL_FIXTURE="evaluation/fixtures/pass_grounding.json"
ERROR_RATE="0.0"
APPROVE=1

case "$MODE" in
  pass) ;;
  fail-checkov)
    TF_DIR="infra/insecure"
    ;;
  fail-eval)
    EVAL_FIXTURE="evaluation/fixtures/fail_grounding.json"
    ;;
  fail-health)
    ERROR_RATE="0.081"
    ;;
  *)
    echo "Usage: $0 [pass|fail-checkov|fail-eval|fail-health]"
    exit 2
    ;;
esac

step "Terraform fmt/validate ($TF_DIR)"
if [[ "$SKIP_TERRAFORM" == "1" ]]; then
  echo "skipped (SKIP_TERRAFORM=1)"
elif command -v terraform >/dev/null 2>&1; then
  terraform -chdir="$TF_DIR" init -backend=false -input=false >/dev/null
  terraform -chdir="$TF_DIR" fmt -check -recursive
  terraform -chdir="$TF_DIR" validate
  ok "terraform validate"
else
  echo "terraform not installed — skipping validate (Checkov still scans .tf)"
fi

step "Checkov ($TF_DIR)"
if checkov -d "$TF_DIR" --config-file .checkov.yaml --quiet; then
  ok "Checkov clean on $TF_DIR"
else
  fail "Checkov policy violations in $TF_DIR — deployment blocked"
fi

step "Agent evaluation ($EVAL_FIXTURE)"
if python -m agentthree_devsecops.evaluation --fixture "$EVAL_FIXTURE"; then
  ok "evaluation thresholds met"
else
  fail "evaluation below threshold — deployment blocked"
fi

step "Container scan (Trivy filesystem / Dockerfile)"
if [[ "$SKIP_TRIVY" == "1" ]]; then
  echo "skipped (SKIP_TRIVY=1)"
elif command -v trivy >/dev/null 2>&1; then
  mkdir -p artifacts
  trivy fs --severity CRITICAL,HIGH --exit-code 0 --format table \
    --skip-dirs .venv --skip-dirs .git --skip-dirs .terraform \
    -o artifacts/trivy.txt .
  ok "Trivy scan complete (see artifacts/trivy.txt)"
else
  echo "trivy not installed — skipping (CI installs it; local optional)"
fi

step "Deploy dry-run + approval"
if [[ "$APPROVE" == "1" ]]; then
  export PROD_APPROVED=true
fi
python -m agentthree_devsecops.deploy_dry_run --target prod --require-approval

step "Health / rollback dry-run (error_rate=$ERROR_RATE)"
if python -m agentthree_devsecops.rollback --error-rate "$ERROR_RATE"; then
  ok "health OK"
else
  fail "health check failed — rollback simulated (see artifacts/rollback-result.json)"
fi

echo
echo "${GRN}All gates passed (mode=$MODE). No cloud resources were created.${RST}"
