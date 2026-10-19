# 60-second demo

## Option A — React console (recommended for interviews)

```bash
# Terminal 1
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
agentthree-rag serve

# Terminal 2
cd web && yarn install && yarn dev
```

Open http://127.0.0.1:5173 → **Live ask** → click the four presets in order.

## Option B — CLI only

```bash
./scripts/run_demo.sh
```

## What you should see

1. **Alice (HR, confidential)** asks about the remote-work stipend → grounded answer citing `POL-HR-001` with `$75`.
2. **Bob (Engineering, internal)** asks the same question → **refusal** (HR confidential doc filtered by ACL).
3. **Eve (Contractor, public)** asks how to report ethics concerns → answer citing `POL-PUB-003`.
4. **Alice** asks about an aquarium cleaning schedule → **refusal** (no corpus evidence; will not fabricate).

Then **Evaluation** tab (or CLI `agentthree-rag eval`) prints `score=100%` and pytest goes green.

**Billing:** none — local hashing embeddings, extractive grounding, no LLM/cloud APIs.

## Manual CLI commands

```bash
agentthree-rag principals
agentthree-rag ask -p alice_hr "What is the monthly home-office stipend for fully remote employees?"
agentthree-rag ask -p bob_eng "What is the monthly home-office stipend for fully remote employees?"
agentthree-rag eval
agentthree-rag serve
```
