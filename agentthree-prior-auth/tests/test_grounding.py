"""Citation filter + demo CDS grounding (no-fault must stay clean)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentthree.domain import cds_evaluate, evaluate_policy, extract_entities  # noqa: E402
from agentthree.gemini_steps import (  # noqa: E402
    apply_citation_filter,
    build_citation_allowlist,
    synthesize_with_gemini,
)
from mcp_servers.clinical import server as clinical  # noqa: E402

CASES = json.loads((ROOT / "evaluation" / "cases.json").read_text())


def test_inject_uncited_increments_unsupported_by_one():
    allowed = ["GL-ACR-LBP v.subacute-radiculopathy", "GL-ACP-2017 rec 3", "POL-AHP-RAD-014 §5"]
    recs = [
        {
            "t": "MRI is appropriate after conservative care.",
            "conf": 0.88,
            "cite": ["GL-ACR-LBP v.subacute-radiculopathy", "GL-ACP-2017 rec 3"],
        },
        {
            "t": "Document PT discharge summary.",
            "conf": 0.71,
            "cite": ["POL-AHP-RAD-014 §5"],
        },
    ]
    cleaned, grounding, bad = apply_citation_filter(recs, allowed, inject_uncited=True)
    assert grounding["unsupported"] == 1
    assert any("UNCITED-DRILL-999" in (r.get("cite") or []) for r in bad)
    assert len(cleaned) == 2


def test_clean_pass_has_zero_unsupported():
    allowed = ["GL-A", "GL-B"]
    recs = [{"t": "ok", "conf": 0.9, "cite": ["GL-A"]}]
    cleaned, grounding, bad = apply_citation_filter(recs, allowed, inject_uncited=False)
    assert grounding["unsupported"] == 0
    assert bad == []
    assert len(cleaned) == 1


def test_allowlist_aliases_pol_and_bare_policy_ids():
    guidelines = {"hits": [{"id": "GL-ACP-2017 rec 3"}]}
    policy = {"hits": [{"chunk": "AHP-RAD-014 §5", "text": "PT notes"}]}
    allowed = build_citation_allowlist(guidelines, policy)
    assert "GL-ACP-2017 rec 3" in allowed
    assert "AHP-RAD-014 §5" in allowed
    assert "POL-AHP-RAD-014 §5" in allowed


def _mcp_hits_for_outcome(outcome: str) -> tuple[dict, dict]:
    if outcome == "urgent":
        q = "imaging lumbar radiculopathy cauda equina urgent expedited"
    else:
        q = "imaging lumbar radiculopathy conservative therapy physical therapy"
    guidelines = clinical.guideline_search(
        query=q, sources=["ACR AC", "ACP"], mode="vector+graph", topK=12
    )
    policy = clinical.policy_search(
        query="lumbar spine MRI 72148 coverage criteria",
        payer="AHP",
        mode="hybrid",
        topK=5,
    )
    return guidelines, policy


def test_no_fault_demo_cds_keeps_all_recs_and_zero_unsupported():
    """Regression: clean Live Run cases must not drop fixture recommendations."""
    for case in CASES:
        x = extract_entities(case["note"], case["icd"])
        pol = evaluate_policy(x)
        assert pol["outcome"] == case["expected_outcome"], case["id"]
        expected = cds_evaluate(x, pol)
        guidelines, policy = _mcp_hits_for_outcome(pol["outcome"])
        cds = asyncio.run(
            synthesize_with_gemini(x, pol, guidelines, policy_hits=policy, inject_uncited=False)
        )[0]
        assert cds["grounding"]["unsupported"] == 0, (
            case["id"],
            cds["grounding"],
            build_citation_allowlist(guidelines, policy),
        )
        assert len(cds["recs"]) == len(expected["recs"]), (
            case["id"],
            [r["t"] for r in expected["recs"]],
            [r["t"] for r in cds["recs"]],
        )


def test_grounding_fail_inject_reports_exactly_one_unsupported():
    case = next(c for c in CASES if c["expected_outcome"] == "meets")
    x = extract_entities(case["note"], case["icd"])
    pol = evaluate_policy(x)
    guidelines, policy = _mcp_hits_for_outcome(pol["outcome"])
    draft = asyncio.run(
        synthesize_with_gemini(x, pol, guidelines, policy_hits=policy, inject_uncited=True)
    )[0]
    assert draft["grounding"]["unsupported"] == 1, draft["grounding"]
