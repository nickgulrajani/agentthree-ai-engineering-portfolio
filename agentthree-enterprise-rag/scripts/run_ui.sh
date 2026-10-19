#!/usr/bin/env bash
# Start API + print instructions for the React console (local, zero cost).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -U pip
  pip install -e ".[dev]"
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> AgentThree Enterprise RAG UI (local, zero API / cloud cost)"
echo "    API:  http://127.0.0.1:8765"
echo "    UI:   cd web && yarn install && yarn dev  →  http://127.0.0.1:5173"
echo
exec agentthree-rag serve --host 127.0.0.1 --port 8765
