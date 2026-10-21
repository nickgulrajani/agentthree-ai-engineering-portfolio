from __future__ import annotations

import re
from typing import Any


def _num(s: str | None) -> float | None:
    if not s:
        return None
    return float(s.replace(",", ""))


def prequalify(text: str) -> dict[str, Any]:
    """Deterministic prequalification — numbers come from code, never an LLM."""

    def grab(pattern: str) -> float | None:
        m = re.search(pattern, text, re.I)
        return _num(m.group(1)) if m else None

    fields = {
        "years": grab(r"(\d+)\s*years?"),
        "revenue": grab(r"revenue\s*(?:of\s*)?\$?([\d,]+)"),
        "credit": grab(r"credit(?:\s*score)?\s*(?:of\s*)?(\d{3})"),
        "amount": grab(r"requesting\s*\$?([\d,]+)"),
        "noi": grab(r"NOI\s*\$?([\d,]+)"),
        "ds": grab(r"debt service\s*\$?([\d,]+)"),
    }
    missing = [k for k, v in fields.items() if v is None]
    if missing:
        return {
            "decision": "INCOMPLETE",
            "missing": missing,
            "checks": [],
            "reasons": [],
            "amount": fields["amount"] or 0,
            "inputs": fields,
            "dscr": None,
        }

    dscr = fields["noi"] / fields["ds"]
    checks: list[dict[str, str]] = []
    reasons: list[str] = []

    def add(label: str, value: str, status: str, policy: str, reason: str | None) -> None:
        checks.append(
            {"label": label, "value": value, "status": status, "policy": policy}
        )
        if status != "pass" and reason:
            reasons.append(reason)

    years, revenue, credit, amount = (
        fields["years"],
        fields["revenue"],
        fields["credit"],
        fields["amount"],
    )
    add(
        "Time in business",
        f"{int(years)} yrs",
        "pass" if years >= 2 else "fail",
        "LP-101",
        None if years >= 2 else "Insufficient time in business",
    )
    add(
        "Annual revenue",
        f"${revenue:,.0f}",
        "pass" if revenue >= 100_000 else "fail",
        "LP-101",
        None if revenue >= 100_000 else "Revenue below minimum",
    )
    if credit >= 650:
        credit_status, credit_reason = "pass", None
    elif credit >= 620:
        credit_status, credit_reason = (
            "conditional",
            "Credit score in conditional range; collateral required",
        )
    else:
        credit_status, credit_reason = "fail", "Credit score below minimum"
    add("Credit score", str(int(credit)), credit_status, "LP-104", credit_reason)
    add(
        "Requested amount",
        f"${amount:,.0f}",
        "pass" if 10_000 <= amount <= 500_000 else "fail",
        "LP-102",
        None if 10_000 <= amount <= 500_000 else "Requested amount outside program limits",
    )
    add(
        "DSCR",
        f"{dscr:.2f}",
        "pass" if dscr >= 1.25 else "fail",
        "LP-103",
        None if dscr >= 1.25 else f"Insufficient cash flow: DSCR {dscr:.2f} below 1.25",
    )

    if any(c["status"] == "fail" for c in checks):
        decision = "NOT PREQUALIFIED"
    elif any(c["status"] == "conditional" for c in checks):
        decision = "CONDITIONAL"
    else:
        decision = "PREQUALIFIED"
    return {
        "decision": decision,
        "checks": checks,
        "reasons": reasons,
        "amount": amount,
        "dscr": round(dscr, 2),
        "inputs": fields,
        "missing": [],
    }
