# Enterprise RAG — Use Case Value Proposition

**One-liner:** Enterprise RAG as a **permissioned, cited, abstaining** knowledge agent — not a chatbot over a vector DB.

**Billing:** Non-billable portfolio demo. Runs entirely locally — no LLM API keys, no cloud vector database, no model downloads.

---

## What this use case is selling

Most “RAG demos” prove retrieval + an LLM. This one proves the **control plane** enterprises actually care about:

| Capability | Why it matters |
|------------|----------------|
| **Access-aware answers** | Same question, different people → different outcomes. Alice (HR, confidential) sees the stipend; Bob (Engineering, internal) is refused. Confidential policy never enters unauthorized context. |
| **Grounded claims** | Every answered claim cites `doc_id` + section + excerpt. No free-form invention of policy. |
| **Fail closed** | No evidence, thin evidence, or insufficient clearance → **refuse**. Never fabricate. Unknown document classifications deny (no fail-open). |
| **Evaluable** | Offline YAML fixtures score faithfulness / citation / ACL correctness (target **100%**). |
| **Honest scope** | Local hybrid search + extractive grounding today; production maps to managed search + hosted LLM — **without pretending cloud is running**. |

---

## Problem → solution

### Problem
Enterprises cannot put a generic chatbot on HR / security / finance policies. Risks include:

- **Leakage** — answers that ignore clearance, department, or role
- **Hallucination** — invented policy text with no source
- **No audit trail** — claims without citations
- **False confidence** — answering when the corpus has no evidence

### Solution (this demo)
An agent that:

1. **Ingests** policy markdown with ACL metadata  
2. **Retrieves** with hybrid search (vector + BM25 + RRF)  
3. **Filters** by principal clearance · department · roles  
4. **Grounds** extractively with mandatory citations — or **abstains**

```text
 Markdown policies  →  Ingest/chunk  →  Hybrid (vector + BM25 + RRF)
                                              │
 Principal ───────────────────────────────────┼──► ACL filter
                                              ▼
                                    Ground with citations
                                    or refuse (fail closed)
```

---

## Demo story (60 seconds)

| # | Principal | Question | Expected outcome |
|---|-----------|----------|------------------|
| 1 | **Alice** (HR, confidential) | Monthly home-office stipend? | **Answer** + cite `POL-HR-001` (`$75`) |
| 2 | **Bob** (Eng, internal) | *Same question* | **Refuse** — confidential HR filtered by ACL |
| 3 | **Eve** (Contractor, public) | How to report ethics concerns? | **Answer** + cite `POL-PUB-003` |
| 4 | **Alice** | Aquarium cleaning schedule? | **Refuse** — no corpus evidence (will not fabricate) |

Then open **Evaluation** → offline fixtures at **100%**.

### What the React console makes visible
Without a UI, this reads as “a Python script.” The Live Ask console turns it into an interview story:

- Switch principal → see **answer vs refuse** on one screen  
- Citation table under grounded answers  
- `refusal_reason` when abstaining  
- Evaluation tab for faithfulness / citation / ACL score  
- Engineering tab for local → production mappings  

---

## Value by audience

| Audience | Takeaway |
|----------|----------|
| **Hiring / interview** | You understand enterprise RAG beyond embeddings: ACL, citations, abstention, eval. |
| **Security / compliance** | Fail-closed retrieval; denials are explicit and testable; no silent over-sharing. |
| **Product / leadership** | Knowledge assistant that is trustworthy under policy constraints, not “helpful at all costs.” |
| **Engineering** | Clear control flow + documented production analogues (OpenSearch / Azure AI Search / Vertex, hosted LLM grounding). |

---

## What is implemented vs documented

| Area | Status | Notes |
|------|--------|-------|
| Ingest / chunk / hybrid retrieve | **Implemented (local)** | Deterministic hashing embeddings — no model download |
| ACL filter | **Implemented (local)** | Clearance · dept · roles; unknown classifications deny |
| Grounded answers + citations | **Implemented (local)** | Extractive sentences from authorized chunks |
| Refuse-to-fabricate | **Implemented (local)** | Score + lexical overlap gates |
| Offline RAG evaluation | **Implemented** | YAML fixtures + pytest / API / UI |
| React Live Ask console | **Implemented (local)** | Vite + FastAPI; zero billable surface |
| Managed vector DB / cloud search | **Not deployed** | Documented analogues only |
| Hosted LLM grounding | **Not deployed** | Extractive grounder simulates cite/abstain policy |

---

## How to run (zero cost)

```bash
# Terminal 1 — API
cd agentthree-enterprise-rag
source .venv/bin/activate   # after: pip install -e ".[dev]"
./scripts/run_ui.sh

# Terminal 2 — React UI
cd web && yarn install && yarn dev
# open http://127.0.0.1:5173 → Live ask → four presets
```

CLI-only: `./scripts/run_demo.sh`

See also: [DEMO.md](DEMO.md), [README.md](README.md), [docs/architecture.md](docs/architecture.md).

---

## Design principles

1. **Fail closed** — insufficient authorized evidence ⇒ refusal; unknown classifications denied.  
2. **Citations are mandatory** on every answered claim.  
3. **ACL after retrieve** — denials are explicit and testable.  
4. **Honest scope** — local hashing/BM25 simulate enterprise search; production analogues are documented, not pretended.  
5. **Zero billable surface** — no API keys, no cloud apply, no model downloads required for the demo.
