# Architecture (local vs production mapping)

This repo is a **reference build you can run offline**. Names like Bedrock, Vertex, and Azure OpenAI in the HTML lab are the **production mapping**, not live calls.

```
Browser HTML (web/index.html)     Python CLI / pytest
        │                                    │
        ├─ simulated agent graph ────────────┤  same rules
        ├─ BM25 over LP-* corpus ────────────┤
        ├─ prequal tool (DSCR, credit) ──────┤
        └─ eval gate ≥90% ───────────────────┘

Optional: paste Anthropic key in the HTML only.
Python never reads that key. make verify never bills.
```

Production (not in this repo): LangGraph on a checkpointer, model gateway as the only egress, private endpoints for PII, Terraform for the landing zone, evals in GitHub Actions before promote.
