# AgentThree Prior Auth — Use Case & Value Proposition

**One-liner:** Three specialized agents assemble clinical evidence, match payer criteria, and hand a cited recommendation to a human — over real A2A + MCP protocols — for lumbar MRI prior authorization (CPT 72148).

**Repo:** [nickgulrajani/agentthree-prior-auth](https://github.com/nickgulrajani/agentthree-prior-auth)  
**Lab:** [agentthree.ai/solutions/agentic-ai](https://agentthree.ai/solutions/agentic-ai)

> Fictional patients, payer, and policy — **not for clinical use**.

---

## Value proposition

| Stakeholder | What they get |
|-------------|----------------|
| **Health systems / PA ops** | Faster, more complete PA packets; fewer “missing documentation” loops; every claim cited |
| **Payers / UM** | Criterion-by-criterion matching against versioned policy; auditable trail; agents cannot deny |
| **Clinicians** | HITL gate — Approve / Request info / Escalate — no consequential decision without a human |
| **Engineering / AI leaders** | Working reference for **Google ADK · A2A · MCP · Gemini** with eval harness and fault drills |
| **Interview / portfolio** | Local demo you can prove is real (tool calls, Agent Cards, audit seal, golden-case scores) |

**Core claim:** Prior authorization is multi-system criteria work, not a chatbot. Agents + protocols + grounding + human review beat a single LLM prompt.

---

## The problem

1. **Fragmented evidence** — Facts sit across EHR, meds, payer policy, and guidelines. Staff assemble them by hand; requests stall on missing docs.
2. **Policy matching is checklist work** — Diagnosis, conservative therapy, exam findings, prior imaging — each needs cited evidence (e.g. AHP-RAD-014 §3.x).
3. **Regulatory clock** — CMS-0057-F sets PA timeframes and FHIR Prior Auth APIs. Speed without traceability is a liability.

A single chat model that “reads the note” does not produce an auditable, criterion-linked, human-sealed decision.

---

## The use case

**Scenario:** Prior authorization for **MRI lumbar spine without contrast**  
**CPT:** `72148` · **ICD-10 example:** `M54.16` (lumbar radiculopathy)  
**Payer policy (synthetic):** AHP-RAD-014  
**Patient (fictional):** Jordan Rivera  

### Happy path

1. Provider submits clinical note + coding (EHR / portal / Da Vinci PAS–shaped request).
2. **Clinical Intake** extracts entities, normalizes to FHIR R4 / RxNorm, flags documentation gaps.
3. **Prior Authorization** checks eligibility, retrieves policy criteria, matches criterion by criterion → `meets` | `pend` | `urgent`.
4. **Clinical Decision Support** retrieves guidelines, synthesizes cited recommendations, runs grounding guardrail.
5. **HITL gate** — human seals Approve / Request info / Escalate.
6. **Audit ledger** — SHA-256 hash-chained events for the case.

### Alternate outcomes (same agents)

| Outcome | When |
|---------|------|
| `meets` | ≥6 weeks conservative therapy + neuro/radicular findings; no blocking prior MRI |
| `pend` | Incomplete PT / meds docs, or prior lumbar MRI in window without interval change |
| `urgent` | Red flags (e.g. saddle numbness, urinary retention) → escalate |

---

## Solution architecture (what you show)

```
Provider → Clinical Intake → Prior Auth → CDS → HITL (human)
                ↓               ↓         ↓
              MCP tools (FHIR · RxNorm · policy · eligibility · guidelines)
                ↓
         Synthetic demo data + Gemini (live or fixtures)
                ↓
         SHA-256 hash-chained audit + OTel-shaped spans
```

| Layer | Technology | Role |
|-------|------------|------|
| Agents | Google ADK `LlmAgent`s | Intake · Prior Auth · CDS |
| Agent ↔ agent | **A2A** JSON-RPC `message/send` | Shared `contextId`; Agent Cards on `:9001–9003` |
| Agent ↔ tools | **MCP** (FastMCP, streamable HTTP) | No direct DB/EHR access from agents |
| Models | Gemini (`gemini-2.0-flash`) via AI Studio | Extract / match / synthesize (or fixtures) |
| API | FastAPI + SSE | Live run stream, decision seal |
| UI | **React (Vite)** + classic HTML | Overview · Live run · Evaluation · Engineering · Build status |
| Eval | `evaluation/` golden cases | Outcome accuracy baseline |

Full diagram: [`docs/architecture.md`](docs/architecture.md)

---

## What’s real vs synthetic (honest framing)

| Real (local software) | Synthetic / optional |
|------------------------|----------------------|
| FastAPI pipeline + SSE | Clinical data (demo FHIR patients) |
| MCP tool server + tool calls | Payer policy text (AHP-RAD-014) |
| A2A HTTP `message/send` + Agent Cards (`START_A2A=true`) | Production EHR / payer APIs |
| HITL gate, double-seal `409`, hash-chained audit | Cloud Run / GKE / Vertex (not deployed by default) |
| Fault drills (`set_fault`, `grounding_fail`) | Live Gemini only when `DEMO_MODE=false` + AI Studio key |

**Interview one-liner:**  
“This is a live local agent stack — real MCP, A2A, and audit — with fixture-backed or free-tier Gemini. Clinical data is synthetic so the demo costs nothing and never touches PHI.”

---

## Differentiation (why this isn’t “just an LLM demo”)

1. **Three specialized agents**, not one mega-prompt  
2. **Protocols you can open in the browser** — MCP inspector + A2A payloads + Agent Card URLs  
3. **Grounding** — CDS claims must cite; `grounding_fail` shows block → regenerate  
4. **Agents cannot deny** — adverse paths go to humans  
5. **Tamper-evident audit** — seal once; second seal → HTTP `409`  
6. **Measured** — golden cases with published outcome accuracy  
7. **Resilience** — MCP timeout / outage / missing policy drills  

---

## Evaluation metrics (published)

Deterministic offline scorer (`evaluation/run_eval.py`) — no Gemini required.  
UI: **Evaluation** tab · API: `GET /api/evaluation` · File: [`evaluation/published_results.json`](evaluation/published_results.json)

| Case ID | Expected | Actual | Pass |
|---------|----------|--------|------|
| `meets-criteria` | `meets` | `meets` | ✓ |
| `missing-documentation` | `pend` | `pend` | ✓ |
| `red-flag-urgent` | `urgent` | `urgent` | ✓ |
| `meets-pt-words` | `meets` | `meets` | ✓ |
| `pend-prior-imaging` | `pend` | `pend` | ✓ |

| Metric | Result |
|--------|--------|
| **Outcome accuracy** | **5 / 5 (100%)** |
| Golden cases | 5 synthetic CPT `72148` scenarios |
| Pytest | 21 passed (domain · MCP · eval · grounding) |

Reproduce:

```bash
.venv/bin/python -m evaluation.run_eval
.venv/bin/python -m pytest tests/ -q
```

---

## Cost / billing modes

| Mode | `.env` | Cost | What still runs |
|------|--------|------|-----------------|
| Offline demo | `DEMO_MODE=true`, Vertex `FALSE` | **$0** | MCP, A2A, UI, audit, note→outcome logic |
| Free live Gemini | `DEMO_MODE=false` + AI Studio key, Vertex `FALSE` | **$0** within free rate limits | Same + live model calls |
| Vertex / paid | `GOOGLE_GENAI_USE_VERTEXAI=TRUE` | **Can bill GCP** | Don’t use for demos |

Always keep: `GOOGLE_GENAI_USE_VERTEXAI=FALSE`  
Recommended demo: `START_A2A=true` so Agent Cards on ports 9001–9003 are live.

---

## Demo script (prove it’s real in ~5 minutes)

1. **Edit the note live** — add “completed 6 weeks of physical therapy…” → moves toward `meets`; add “urinary retention and saddle numbness” → `urgent`. Canned output can’t do that cleanly.  
2. **MCP tools tab** — show FHIR lookup, RxNorm (e.g. naproxen), policy check + timings.  
3. **A2A messages tab** — JSON-RPC `message/send` with the same `contextId` as the header.  
4. **Terminal logs** — backend/MCP lines appear as you submit.  
5. **Agent Card** — open `http://127.0.0.1:9001/.well-known/agent-card.json` (with `START_A2A=true`).  
6. **Fault drill** — `grounding_fail`: uncited claim blocked, then regenerated.  
7. **Seal decision** — show hash-chained audit entry; seal again → **409**.  
8. **Evaluation tab** — show **100%** outcome accuracy on five golden cases.

---

## UI map (React @ http://127.0.0.1:5173)

| Tab | Story |
|-----|--------|
| **Overview** | Problem + architecture SVG (ADK · A2A · MCP · HITL · audit) |
| **Live run** | Agents lighting up · MCP / A2A inspector · HITL gate |
| **Evaluation** | Golden-case outcome accuracy |
| **Engineering** | Capability cards |
| **Build status** | Built vs deferred (Cloud Run / Confidential Computing deferred) |

Classic HTML: `http://127.0.0.1:8000/classic`

---

## How to run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DEMO_MODE / key / START_A2A as needed

# Terminal 1
.venv/bin/python -m agentthree

# Terminal 2
cd web && npm install && npm run dev
```

Open **http://127.0.0.1:5173**

---

## Talking points (short)

- “Three ADK agents coordinate over **A2A**; they reach clinical systems only through **MCP**.”  
- “Recommendation is grounded and **human-sealed** — agents never issue a denial.”  
- “You can inspect every tool call and every `message/send`, plus a hash-chained audit ledger.”  
- “We score five golden cases at **100% outcome accuracy** offline — no cloud required.”  
- “Demo runs at **$0** on fixtures or AI Studio free tier; Vertex stays off.”  

---

## Limitations & next increments (say this first if asked)

| Honest limit | Next increment |
|--------------|----------------|
| Synthetic FHIR / policy, not a live EHR | Wire to sandbox FHIR / Da Vinci PAS |
| Single CPT scenario (72148) | Expand policy pack + case library |
| Eval focuses on outcome accuracy | Add grounding / latency / completeness metrics |
| Local deploy only | Optional Cloud Run / GKE |
| Gemini optional / free-tier | Production model routing + observability |

---

## Key file map

| Path | Purpose |
|------|---------|
| `agents/` | ADK agents (intake · prior auth · CDS) |
| `mcp_servers/clinical/` | MCP tools + `set_fault` |
| `agentthree/` | Pipeline, API, Gemini steps, audit |
| `web/` | React Live Run UI |
| `data/` | Demo FHIR + policy |
| `evaluation/` | Golden cases + published metrics |
| `docs/architecture.md` | Architecture detail |
| `.env.example` | Free-tier / `$0` demo config |
| `Use_Case_Value_Prop.md` | This document |

---

## 10-minute demo narrative (script)

Use this as a spoken arc. Keep the browser on **http://127.0.0.1:5173** and a terminal with backend logs visible.

| Min | Tab / action | What you say |
|-----|----------------|--------------|
| 0–1 | **Overview** | “Prior auth fails because evidence is fragmented and policy is a checklist. A chatbot can’t own that. We use three specialized agents.” |
| 1–2 | Architecture SVG | “Intake extracts and normalizes. Prior Auth matches AHP-RAD-014 criterion by criterion. CDS cites guidelines. A human always seals. Agents talk over **A2A**; tools only via **MCP**.” |
| 2–5 | **Live run** — happy path | Submit Jordan Rivera / meets preset. Point at agents lighting up. Open **MCP** tab (FHIR, RxNorm, policy). Open **A2A** tab (`message/send` + shared `contextId`). |
| 5–6 | Edit note / second run | Delete PT weeks or add red flags. “Outcome changes with the note — not a canned video.” |
| 6–7 | Fault or grounding | Run `grounding_fail` or MCP fault. “Failures are real server-side drills, then recovery.” |
| 7–8 | HITL + seal | Approve as fictional MD. Show audit entry. Try seal again → **409**. |
| 8–9 | Agent Card (optional) | Open `:9001/.well-known/agent-card.json`. “These are real A2A servers, not mocks in the UI only.” |
| 9–10 | **Evaluation** | “Five golden cases, **100%** outcome accuracy, offline scorer — reproducible without cloud spend.” |

**Close:** “Synthetic data, real agent stack. Ready to wire to sandbox FHIR / Da Vinci next.”

---

## Persona pitches (30 seconds each)

### Hiring manager / AI engineering lead
“I built a local multi-agent prior-auth system on Google ADK with A2A handoffs and MCP tools, a React Live Run console, fault drills, hash-chained audit, and a golden-case eval at 100% outcome accuracy. You can watch every tool call and Agent Card in a live demo.”

### Clinical / UM operations
“Staff assemble PA packets by hand and bounce on missing docs. This stack extracts evidence, matches payer criteria with citations, and stops for a clinician before anything consequential. Agents never deny — they recommend and escalate.”

### Payer / compliance-minded stakeholder
“Every criterion status is explicit (`met` / `not` / `waive`), CDS claims are grounded, and the seal is hash-chained. Second seal returns 409. That is the shape of auditable automation under CMS-0057-F pressure — demonstrated locally on synthetic data.”

### Platform / architecture interviewer
“Separation of concerns: A2A for agent-to-agent task lifecycle and shared `contextId`; MCP for tool access so agents never own the data plane. Optional AI Studio Gemini; `DEMO_MODE` keeps the same MCP/A2A paths for $0 demos.”

---

## Business value (directional — not a ROI claim)

Use carefully; these are **industry-problem framing**, not measured savings from this demo.

| Pain today | How this use case addresses it |
|------------|--------------------------------|
| High touch time per PA | Agents pre-assemble evidence + criteria table for the reviewer |
| Missing-documentation loops | Intake surfaces gaps before submission quality collapses |
| Inconsistent policy application | Criterion-level match against versioned policy text |
| Audit / appeal pain | Hash-chained ledger of tools, messages, model steps, human decision |
| “Black box AI” distrust | MCP/A2A inspectors + citations + HITL |

**What this repo proves (measurable here):** outcome accuracy on golden cases, reproducible tests, inspectable protocol traffic — not production cycle-time reduction.

---

## Security, privacy & compliance posture (demo)

| Topic | Stance in this demo |
|-------|---------------------|
| PHI | **Synthetic / fictional only** |
| Clinical use | **Not for clinical use** |
| Denial authority | Agents **cannot deny**; human gate required |
| Audit | SHA-256 hash-chained ledger per case |
| Model path | Prefer AI Studio free tier; Vertex **off** by default |
| Network | Localhost services; no Cloud Run required |
| Grounding | Unsupported / uncited claims filtered (`grounding_fail` drill) |

Production would add: real IdP, PHI minimization, BAA, env isolation, Confidential Computing (listed as deferred on Build status).

---

## Protocol cheat sheet

### A2A (agent → agent)
- JSON-RPC method: `message/send`
- Shared: `contextId` (case), task states → `input-required` for HITL
- Agent Cards: `http://127.0.0.1:9001|9002|9003/.well-known/agent-card.json` when `START_A2A=true`
- UI: Live run → **A2A messages**

### MCP (agent → tools)
- Streamable HTTP clinical server (`MCP_PORT`, default 8080)
- Example tools: FHIR search, RxNorm normalize, policy search, eligibility, guidelines, `set_fault`
- UI: Live run → **MCP tool calls**

### HITL + audit
- Actions: Approve · Request info · Escalate  
- Seal twice → HTTP `409`  
- Ledger: hash-chained events for the case  

---

## Environment quick reference

```bash
# $0 offline (fixtures; MCP + A2A still real)
DEMO_MODE=true
GOOGLE_GENAI_USE_VERTEXAI=FALSE
START_A2A=true

# Free live Gemini (AI Studio key; still avoid Vertex)
DEMO_MODE=false
GOOGLE_API_KEY=<ai-studio-key>
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GEMINI_MODEL=gemini-2.0-flash
START_A2A=true
```

Ports: API `8000` · MCP `8080` · A2A `9001–9003` · React `5173`

---

## Interviewer Q&A (anticipated)

**Q: Is this production?**  
A: No — local reference implementation with synthetic clinical data. Protocols and orchestration are real; EHR/payer integrations and cloud deploy are next increments.

**Q: Why three agents instead of one?**  
A: Different jobs and blast radii — extraction, coverage matching, and cited decision support. Clear A2A handoffs and independent Agent Cards.

**Q: How do you prevent hallucinated medical claims?**  
A: CDS grounding counts claims/cited/unsupported; uncited content is blocked. Demo drill `grounding_fail` shows inject → block → regenerate. Plus human seal.

**Q: How do you know it works?**  
A: Five golden cases scored offline at 100% outcome accuracy; 21 pytest; Live Run inspectors for MCP/A2A; Evaluation tab in the UI.

**Q: Will this cost money in a demo?**  
A: Not if `DEMO_MODE=true`, or AI Studio free tier with Vertex false. Keep Vertex disabled.

**Q: Where’s the React app?**  
A: `web/` (Vite + React 19). Classic HTML remains at `/classic` for comparison.

**Q: What would you ship next?**  
A: Sandbox FHIR / Da Vinci PAS, broader CPT/policy pack, richer eval metrics (grounding, latency), then optional Cloud Run.

---

## Related docs in-repo

| Doc | Use when |
|-----|----------|
| [`README.md`](README.md) | Quick start, status table, eval table |
| [`docs/architecture.md`](docs/architecture.md) | Protocol and layer detail |
| [`evaluation/README.md`](evaluation/README.md) | How to re-score golden cases |
| [`web/README.md`](web/README.md) | React FE only |
| [`.env.example`](.env.example) | Copy-paste env for demos |

---

## Bottom line

**Use case:** End-to-end prior authorization for lumbar MRI with multi-agent evidence assembly, policy matching, grounded CDS, and human review.

**Value:** Faster, more complete, auditable PA decisions — demonstrated with industry agent protocols (ADK / A2A / MCP), measurable eval results, and a local demo you can prove is real without cloud billing.

**Proof in one breath:** Edit the note → outcome changes; open MCP and A2A tabs; seal once (audit) and twice (409); show Evaluation **5/5**.
