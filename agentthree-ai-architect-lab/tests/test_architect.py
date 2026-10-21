from agentthree_ai_architect.agent import run_agent
from agentthree_ai_architect.evals import PRESETS, run_eval_suite
from agentthree_ai_architect.guardrails import is_injection, redact_pii
from agentthree_ai_architect.policy import bm25, chunk_docs
from agentthree_ai_architect.prequal import prequalify
from agentthree_ai_architect.router import RouteRequest, route


def test_strong_applicant_prequalifies():
    tool = prequalify(PRESETS[1])
    assert tool["decision"] == "PREQUALIFIED"
    assert tool["dscr"] >= 1.25


def test_weak_dscr_declines():
    tool = prequalify(PRESETS[3])
    assert tool["decision"] == "NOT PREQUALIFIED"
    assert any("DSCR" in r for r in tool["reasons"])


def test_incomplete_does_not_guess():
    tool = prequalify("Prequalify me, I have been in business 5 years and want $90,000.")
    assert tool["decision"] == "INCOMPLETE"
    assert "credit" in tool["missing"]


def test_pii_redacted():
    redacted, n = redact_pii(PRESETS[2])
    assert n == 2
    assert "123-45-6789" not in redacted
    assert "owner@acme" not in redacted


def test_injection_blocked_skips_draft():
    assert is_injection(PRESETS[4])
    state = run_agent(PRESETS[4])
    assert state["blocked"]
    assert not any(span["node"] == "draft" for span in state["spans"])


def test_hitl_over_250k():
    state = run_agent(
        "Prequalify: 3 years in business, revenue $2,400,000, credit score 688, "
        "requesting $400,000, NOI $210,000, annual debt service $140,000."
    )
    assert state["needs_human"]
    assert state["human"] == "queued for underwriter"


def test_router_keeps_pii_off_public_apis():
    result = route(
        RouteRequest(prompt="simple classify extract", tin=400, tout=200, pii=True)
    )
    assert result["pick"] is not None
    assert result["pick"]["priv"] is True
    public = [r for r in result["rows"] if r["id"] in {"anthropic-api", "openai-api"}]
    assert all(not r["ok"] for r in public)


def test_eval_gate_allows_merge():
    suite = run_eval_suite()
    assert suite["total"] == 10
    assert suite["rate"] >= 0.9
    assert suite["gate"] == "MERGE ALLOWED"


def test_bm25_returns_credit_policy():
    hits = bm25("minimum credit score", chunk_docs(), k=3)
    assert hits
    assert any(h.id == "LP-104" for h in hits)
