# AgentThree · Enterprise RAG & Knowledge Architecture

**Signature technical specialization:** enterprise knowledge retrieval with hybrid search, metadata ACLs, grounded citations, and refusal-to-fabricate.

An AI agent answers a policy question using **only authorized documents**, returns **citations**, and **refuses** when evidence is insufficient.

Companion browser lab: [RAG Engineering · Module 04](https://agentthree.ai/ai-engineering-lab/rag-engineering)

> **Non-billable portfolio demo.** Runs entirely locally — no LLM API keys, no cloud vector database, no model downloads. Production mappings are documented in [docs/architecture.md](docs/architecture.md).

---

## Status

**Last verified:** 2026-10-18 · suite green via [`make verify`](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio#verify-everything) in the [AI Engineering Portfolio](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio) monorepo ([CI](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio/actions/workflows/verify.yml)).


## Implementation status

| Area | Status | Notes |
|------|--------|-------|
| Ingest / chunk / hybrid retrieve (vector + BM25 + RRF) | **Implemented (local)** | Deterministic hashing embeddings — no model download |
| ACL filter (clearance · dept · roles) | **Implemented (local)** | Fail-closed after retrieve; **unknown classifications deny** (no fail-open on missing rank) |
| Grounded answers + citations | **Implemented (local)** | Extractive sentences from authorized chunks |
| Refuse-to-fabricate | **Implemented (local)** | Score + lexical overlap gates |
| Offline RAG evaluation | **Implemented** | YAML fixtures + `pytest` / `agentthree-rag eval` (8 pytest cases) |
| React Live Ask console | **Implemented (local)** | Vite FE + FastAPI; principal switch, presets, citations, eval tab |
| Managed vector DB / cloud search | **Not deployed** | Documented analogues only (OpenSearch, Azure AI Search, Vertex) |
| Hosted LLM grounding | **Not deployed** | Local extractive grounder simulates citation/abstain policy |

**Simulated vs cloud:** Retrieval, ACL, grounding, and eval are fully runnable offline. Enterprise search / IdP / managed embeddings are **documented mappings**, not live cloud services.

Architecture diagram: [docs/architecture.md](docs/architecture.md)

---

## Key Points

```text
Alice (HR, confidential)  →  ANSWER + cite POL-HR-001 ($75 stipend)
Bob  (Eng, internal)      →  REFUSE  (ACL filtered confidential HR doc)
Eve  (Contractor, public) →  ANSWER + cite POL-PUB-003 (ethics hotline)
Any principal             →  REFUSE  when the corpus has no evidence
```

Plus offline RAG evaluation: faithfulness / citation / ACL fixtures at **100%**.

## Architecture (local)

```text
 Markdown policies  →  Ingest/chunk  →  Hybrid (vector + BM25 + RRF)
                                              │
 Principal ───────────────────────────────────┼──► ACL filter
                                              ▼
                                    Ground with citations
                                    or refuse (fail closed)
```

| Capability | How (free) |
|------------|------------|
| Document ingestion | Markdown + YAML frontmatter |
| Embeddings | Deterministic hashing vectors (no API) |
| Vector search | In-memory cosine |
| Hybrid keyword | BM25 + reciprocal rank fusion |
| Access controls | Clearance · department · roles |
| Grounded answers | Extractive sentences from authorized chunks |
| Citations | `doc_id` + section + excerpt |
| RAG evaluation | Offline YAML fixtures + pytest |

## Quick start (local, free)

### React console (interview demo)

```bash
cd agentthree-enterprise-rag
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Terminal 1 — API (http://127.0.0.1:8765)
./scripts/run_ui.sh
# or: agentthree-rag serve

# Terminal 2 — Vite UI
cd web && yarn install && yarn dev
# open http://127.0.0.1:5173 → Live ask → run the four presets
```

Optional: `cd web && yarn build` then restart the API so `/` serves the React bundle.

### CLI walkthrough

```bash
cd agentthree-enterprise-rag
chmod +x scripts/run_demo.sh
./scripts/run_demo.sh
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
agentthree-rag demo
agentthree-rag eval
pytest -q
```

### Reproducible tests

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
agentthree-rag eval
```

Expected: pytest green; offline eval reports **100%** on faithfulness / citation / ACL fixtures (Alice answer, Bob ACL refuse, Eve public answer, fabrication refuse).

## Repository layout

| Path | Purpose |
|------|---------|
| `src/agentthree_enterprise_rag/` | Ingest, embeddings, hybrid search, ACL, grounding, eval, FastAPI, CLI |
| `web/` | React Live Ask console (Vite) — Overview / Ask / Eval / Engineering |
| `data/policies/` | Sample enterprise policy corpus with ACL metadata |
| `configs/acl_policy.yaml` | Demo principals and clearance ranks |
| `evaluation/fixtures/` | Offline RAG eval cases |
| `docs/architecture.md` | Control flow + production mapping |
| `tests/` | Proof: authorized answer, ACL deny, fabrication refuse, API |

## Documentation

- [Use case value proposition](Use_Case_Value_Prop.md)
- [Architecture](docs/architecture.md)
- [60-second demo](DEMO.md)

## Design principles

1. **Fail closed** — insufficient authorized evidence ⇒ refusal, never invented policy; unknown doc classifications are denied.
2. **Citations are mandatory** on every answered claim.
3. **ACL after retrieve** — denials are explicit and testable.
4. **Honest scope** — local hashing/BM25 simulate enterprise search; production analogues are documented, not pretended.

## License

MIT — see [LICENSE](LICENSE).
