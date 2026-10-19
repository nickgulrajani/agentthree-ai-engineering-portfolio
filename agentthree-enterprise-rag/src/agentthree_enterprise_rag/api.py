"""Local FastAPI gateway for the Enterprise RAG React console (zero cloud cost)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__
from .agent import KnowledgeAgent
from .evaluation import run_evaluation
from .ingest import load_documents

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICIES = ROOT / "data" / "policies"
DEFAULT_ACL = ROOT / "configs" / "acl_policy.yaml"
DEFAULT_EVAL = ROOT / "evaluation" / "fixtures" / "rag_cases.yaml"
DEFAULT_PORT = 8765

_agent: KnowledgeAgent | None = None


def get_agent() -> KnowledgeAgent:
    global _agent
    if _agent is None:
        _agent = KnowledgeAgent(DEFAULT_POLICIES, DEFAULT_ACL)
    return _agent


app = FastAPI(
    title="AgentThree Enterprise RAG API",
    version=__version__,
    description="Local hybrid retrieval with ACL + grounded citations. Zero API cost.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    principal_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


@app.get("/api/health")
def health() -> dict[str, Any]:
    agent = get_agent()
    return {
        "ok": True,
        "version": __version__,
        "project": "agentthree-enterprise-rag",
        "chunkCount": agent.chunk_count,
        "zeroCost": True,
        "billableSurface": False,
        "embeddings": "hashing-local",
        "grounding": "extractive-local",
        "message": "Local only — no LLM API keys, no cloud vector DB, no model downloads.",
    }


@app.get("/api/principals")
def principals() -> dict[str, Any]:
    agent = get_agent()
    rows = [
        {
            "principalId": p.principal_id,
            "displayName": p.display_name,
            "department": p.department,
            "clearance": p.clearance,
            "roles": p.roles,
        }
        for p in agent.acl.list_principals()
    ]
    return {"principals": rows}


@app.get("/api/corpus")
def corpus() -> dict[str, Any]:
    chunks = load_documents(DEFAULT_POLICIES)
    docs: dict[str, dict[str, Any]] = {}
    for c in chunks:
        if c.doc_id not in docs:
            docs[c.doc_id] = {
                "docId": c.doc_id,
                "title": c.title,
                "classification": c.classification,
                "allowedDepartments": c.allowed_departments,
                "allowedRoles": c.allowed_roles,
                "source": c.source,
                "chunkCount": 0,
            }
        docs[c.doc_id]["chunkCount"] += 1
    return {"documents": list(docs.values()), "chunkCount": len(chunks)}


@app.post("/api/ask")
def ask(body: AskRequest) -> dict[str, Any]:
    agent = get_agent()
    try:
        principal = agent.describe_principal(body.principal_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc

    result = agent.ask(body.principal_id, body.question)
    return {
        "principal": {
            "principalId": principal.principal_id,
            "displayName": principal.display_name,
            "department": principal.department,
            "clearance": principal.clearance,
            "roles": principal.roles,
        },
        "question": result.question,
        "answered": result.answered,
        "answer": result.answer,
        "refusalReason": result.refusal_reason or None,
        "evidenceCount": result.evidence_count,
        "topScore": result.top_score,
        "citations": [
            {
                "docId": c.doc_id,
                "title": c.title,
                "section": c.section,
                "chunkId": c.chunk_id,
                "classification": c.classification,
                "source": c.source,
                "excerpt": c.excerpt,
            }
            for c in result.citations
        ],
    }


@app.get("/api/evaluation")
def evaluation() -> dict[str, Any]:
    agent = get_agent()
    report = run_evaluation(agent, DEFAULT_EVAL)
    return {
        "score": report.score,
        "passed": report.passed,
        "failed": report.failed,
        "total": report.total,
        "ok": report.ok,
        "zeroCost": True,
        "results": [
            {
                "caseId": r.case_id,
                "passed": r.passed,
                "checks": r.checks,
                "detail": r.detail,
            }
            for r in report.results
        ],
    }


@app.get("/")
def index():
    react_index = ROOT / "web" / "dist" / "index.html"
    if react_index.exists():
        return FileResponse(react_index)
    return HTMLResponse(
        "<!doctype html><html><body style='font-family:system-ui;background:#08090c;"
        "color:#f2f6ff;padding:2rem'>"
        "<h1>AgentThree Enterprise RAG</h1>"
        "<p>API is up. For the React console run:</p>"
        "<pre style='background:#151a25;padding:1rem;border-radius:8px'>"
        "cd web && yarn install && yarn dev\n"
        "# open http://127.0.0.1:5173</pre>"
        "<p>Or <code>yarn build</code> then restart this server to serve "
        "<code>web/dist</code> here.</p>"
        "</body></html>"
    )


_react_assets = ROOT / "web" / "dist" / "assets"
if _react_assets.is_dir():
    app.mount("/assets", StaticFiles(directory=_react_assets), name="react-assets")


def main(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    import uvicorn

    uvicorn.run(
        "agentthree_enterprise_rag.api:app",
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
