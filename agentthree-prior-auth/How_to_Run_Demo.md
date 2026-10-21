# How to run the Prior Authorization demo

Fictional patients, payer, and policy — **not for clinical use**.

Default path is **$0**: `DEMO_MODE=true` uses fixtures. MCP, A2A, the API, and the Live Run UI still run as real local services. No Vertex, Cloud Run, or GKE.

You need Python 3.10+ and (for the React UI) Node.js. You do **not** need a GCP project or AWS account.

---

## 1. Open the project

From the portfolio monorepo:

```bash
cd agentthree-prior-auth
```

Or clone the standalone repo:

```bash
git clone https://github.com/nickgulrajani/agentthree-prior-auth.git
cd agentthree-prior-auth
```

## 2. Install (once)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp -n .env.example .env            # DEMO_MODE=true is the $0 default
```

Always call the backend as `.venv/bin/python -m agentthree`. There is no `./agentthree` file in the project root.

## 3. Tests and evaluation (no Gemini)

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m evaluation.run_eval
```

Expected:

- **21** pytest cases passed (domain, MCP contract, evaluation, grounding)
- Evaluation: **5 / 5 (100%)** outcome accuracy on the golden CPT `72148` cases
- Writes `evaluation/last_results.json` (committed baseline: `evaluation/published_results.json`)

This scorer is deterministic and offline. It does not call Gemini.

## 4. Live Run UI (recommended demo)

**Terminal 1 — backend (MCP + API + optional A2A servers)**

```bash
.venv/bin/python -m agentthree
```

**Terminal 2 — React Live Run**

```bash
cd web
npm install
npm run dev
```

Open **http://127.0.0.1:5173**

| Tab | What you show |
|-----|----------------|
| **Overview** | Architecture (ADK · A2A · MCP · HITL · audit) |
| **Live run** | Agents lighting up + MCP / A2A inspector |
| **Engineering** | Capability cards |
| **Evaluation** | Golden-case outcome accuracy |
| **Build status** | What’s built vs deferred |

Classic HTML: **http://127.0.0.1:8000/classic** (backend must be up).

Happy path in Live run: **Jordan Rivera · CPT `72148` · ICD-10 `M54.16`** → recommend approval → human gate.

Stop with Ctrl+C in each terminal.

## 5. Optional: live Gemini (AI Studio free tier)

Still not Vertex. Keep `GOOGLE_GENAI_USE_VERTEXAI=FALSE`.

1. Get a key at [Google AI Studio](https://aistudio.google.com/apikey)
2. In `.env` set:

```bash
DEMO_MODE=false
GOOGLE_API_KEY=your-ai-studio-api-key-here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

3. Restart `.venv/bin/python -m agentthree`

Within AI Studio free-tier rate limits this stays $0. Leave `DEMO_MODE=true` if you want zero LLM calls.

---

## Cost cheat sheet

| Mode | Cost |
|------|------|
| pytest + `evaluation.run_eval` | $0 |
| Live UI with `DEMO_MODE=true` | $0 (fixtures; MCP + A2A still real) |
| Gemini AI Studio free tier (`DEMO_MODE=false`) | $0 within rate limits |
| Vertex AI / Cloud Run / GKE | **Not used** — not required for the demo |

## What this demo never does (default)

- Call Vertex AI or bill a GCP project
- Deploy to Cloud Run / GKE
- Touch real EHR, payer, or PHI (data in `data/` is synthetic)

Architecture: [docs/architecture.md](docs/architecture.md).
