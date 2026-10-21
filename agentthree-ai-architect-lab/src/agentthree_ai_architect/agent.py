from __future__ import annotations

import re
from typing import Any

from agentthree_ai_architect.guardrails import (
    PROTECTED,
    is_injection,
    mentions_protected,
    redact_pii,
)
from agentthree_ai_architect.policy import bm25, chunk_docs
from agentthree_ai_architect.prequal import prequalify

PREQUAL_RE = re.compile(r"prequal|qualify|requesting|apply", re.I)

HITL_THRESHOLD = 250_000


def _sim_draft(state: dict[str, Any]) -> str:
    if state["intent"] == "policy":
        lines = [f"• {c.text} [{c.id}]" for c in state["chunks"][:2]]
        return "Here is what our lending policy says:\n" + "\n".join(lines)
    tool = state["tool"]
    if tool["decision"] == "INCOMPLETE":
        return (
            f"To prequalify you I still need: {', '.join(tool['missing'])}. "
            "See eligibility rules [LP-101] and cash-flow rules [LP-103]."
        )
    lines = [f"Prequalification result: {tool['decision']}"]
    for check in tool["checks"]:
        lines.append(
            f"• {check['label']}: {check['value']} → {check['status'].upper()} [{check['policy']}]"
        )
    if tool["decision"] != "PREQUALIFIED" and state["revisions"] >= 1:
        lines.append(
            "Principal reasons (adverse action notice): "
            + "; ".join(tool["reasons"])
            + " [LP-106]"
        )
    if tool["decision"] != "NOT PREQUALIFIED":
        lines.append(
            "Next step: upload 2 years of tax returns and 6 months of bank statements [LP-105]. "
            "Decision within 5 business days of complete documents [LP-108]."
        )
    return "\n".join(lines)


def run_agent(text: str, *, no_critic: bool = False) -> dict[str, Any]:
    """Simulated agent graph. Never calls a model or a cloud API."""
    redacted, pii_found = redact_pii(text)
    state: dict[str, Any] = {
        "input": text,
        "redacted": redacted,
        "pii_found": pii_found,
        "blocked": is_injection(text),
        "intent": None,
        "chunks": [],
        "tool": None,
        "draft": "",
        "revisions": 0,
        "critic": None,
        "needs_human": False,
        "human": None,
        "final": "",
        "citations": [],
        "features_used": [],
        "spans": [],
    }
    if state["blocked"]:
        state["final"] = (
            "This request was blocked by the input guardrail (possible prompt injection) "
            "and logged for security review. I can help with lending-policy questions or a prequalification."
        )
        state["spans"] = [{"node": "guard"}, {"node": "respond"}]
        return state

    state["spans"].append({"node": "guard"})
    state["intent"] = "prequal" if PREQUAL_RE.search(redacted) else "policy"
    query = (
        "eligibility revenue credit score DSCR loan amount documents adverse action"
        if state["intent"] == "prequal"
        else redacted
    )
    k = 4 if state["intent"] == "prequal" else 3
    state["chunks"] = bm25(query, chunk_docs(60, 0), k)
    state["spans"] += [{"node": "planner"}, {"node": "retrieve"}]

    if state["intent"] == "prequal":
        state["tool"] = prequalify(redacted)
        state["features_used"] = [
            "years_in_business",
            "annual_revenue",
            "credit_score",
            "requested_amount",
            "dscr",
        ]
    state["spans"].append({"node": "tools"})

    while True:
        state["draft"] = _sim_draft(state)
        state["spans"].append({"node": "draft"})
        issues: list[str] = []
        if not no_critic:
            if not re.search(r"\[LP-\d{3}\]", state["draft"]):
                issues.append("Missing policy citation")
            tool = state["tool"]
            if (
                tool
                and tool["decision"] in {"NOT PREQUALIFIED", "CONDITIONAL"}
                and "LP-106" not in state["draft"]
            ):
                issues.append(
                    "Adverse action reasons required under ECOA/Reg B; cite LP-106"
                )
            if mentions_protected(state["draft"]):
                issues.append("Response references a protected attribute")
            state["needs_human"] = bool(tool and tool.get("amount", 0) > HITL_THRESHOLD)
        state["critic"] = {"pass": not issues, "issues": issues}
        state["citations"] = list(dict.fromkeys(re.findall(r"LP-\d{3}", state["draft"])))
        state["spans"].append({"node": "critic"})
        if issues and state["revisions"] < 2 and not no_critic:
            state["revisions"] += 1
            continue
        break

    if state["needs_human"]:
        state["human"] = "queued for underwriter"
        state["spans"].append({"node": "human_review"})

    extra = ""
    if state["human"]:
        extra += f"\n\nUnderwriter review: {state['human']}."
    if state["critic"] and not state["critic"]["pass"]:
        extra += "\n\nReleased after max revisions with reviewer flags: " + "; ".join(
            state["critic"]["issues"]
        )
    state["final"] = state["draft"] + extra
    state["spans"].append({"node": "respond"})
    return state


def protected_features_used(state: dict[str, Any]) -> bool:
    return any(f in PROTECTED for f in state.get("features_used", []))
