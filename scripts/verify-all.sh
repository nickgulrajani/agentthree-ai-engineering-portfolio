#!/usr/bin/env bash
# Run the lightweight, reproducible test suite for every project.
# Zero Trust integration tests skip cleanly if OPA is not installed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0

run() {
  local name="$1"
  shift
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo "▶ $name"
  echo "════════════════════════════════════════════════════════"
  if ( "$@"; ); then
    echo "✔ $name"
  else
    echo "✖ $name"
    fail=1
  fi
}

# --- Healthcare Multi-Agent AI (flagship) ---
run "agentthree-prior-auth" bash -lc '
  cd agentthree-prior-auth
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
  .venv/bin/python -m pytest tests/ -q
  .venv/bin/python -m evaluation.run_eval
'

# --- Confidential AI ---
run "agentthree-confidential-ai" bash -lc '
  cd agentthree-confidential-ai
  python3 -m venv .venv
  .venv/bin/pip install -q -e ".[dev]"
  .venv/bin/python -m pytest tests/ -q
'

# --- Multi-Cloud Zero Trust (skips if OPA missing) ---
run "agentthree-multicloud-zero-trust" bash -lc '
  cd agentthree-multicloud-zero-trust
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
  .venv/bin/pip install -q -e .
  if command -v opa >/dev/null 2>&1; then
    opa test policy/ -q
  else
    echo "OPA not on PATH — skipping Rego suite (pytest will skip integration tests)."
  fi
  .venv/bin/python -m pytest tests/ -q
'

# --- Enterprise RAG ---
run "agentthree-enterprise-rag" bash -lc '
  cd agentthree-enterprise-rag
  python3 -m venv .venv
  .venv/bin/pip install -q -e ".[dev]" 2>/dev/null || .venv/bin/pip install -q -r requirements.txt
  .venv/bin/python -m pytest -q
'

# --- AI DevSecOps ---
run "agentthree-ai-devsecops" bash -lc '
  cd agentthree-ai-devsecops
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
  .venv/bin/pip install -q -e .
  .venv/bin/python -m pytest -q
'

echo ""
if [[ "$fail" -ne 0 ]]; then
  echo "✖ verify-all: one or more projects failed"
  exit 1
fi
echo "✔ verify-all: all project test suites passed"
exit 0
