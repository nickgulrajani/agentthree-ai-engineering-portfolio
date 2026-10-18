"""Citation filter must catch injected uncited claims (grounding_fail drill)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentthree.gemini_steps import apply_citation_filter  # noqa: E402


def test_inject_uncited_increments_unsupported():
    allowed = ["GL-ACR-LBP v.subacute-radiculopathy", "GL-ACP-2017 rec 3"]
    recs = [
        {
            "t": "MRI is appropriate after conservative care.",
            "conf": 0.88,
            "cite": ["GL-ACR-LBP v.subacute-radiculopathy"],
        }
    ]
    cleaned, grounding, bad = apply_citation_filter(recs, allowed, inject_uncited=True)
    assert grounding["unsupported"] >= 1
    assert any("UNCITED-DRILL-999" in (r.get("cite") or []) for r in bad)
    assert cleaned  # good cites still pass
    assert all(
        all(c in allowed for c in (r.get("cite") or [])) for r in cleaned
    )


def test_clean_pass_has_zero_unsupported():
    allowed = ["GL-A", "GL-B"]
    recs = [{"t": "ok", "conf": 0.9, "cite": ["GL-A"]}]
    cleaned, grounding, bad = apply_citation_filter(recs, allowed, inject_uncited=False)
    assert grounding["unsupported"] == 0
    assert bad == []
    assert len(cleaned) == 1
