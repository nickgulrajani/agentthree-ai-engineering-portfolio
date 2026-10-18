"""MCP clinical tool contract smoke tests (no live server process)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp_servers.clinical import server as clinical  # noqa: E402


def test_fhir_read_patient():
    out = clinical.fhir_read("Patient", "demo-7781")
    assert "error" not in out
    assert out.get("resourceType") == "Patient" or out.get("id") == "demo-7781"


def test_policy_search_returns_ahp_rad_014():
    out = clinical.policy_search(query="lumbar MRI CPT 72148")
    assert out.get("hits")
    assert str(out.get("policyId", "")).upper().startswith("AHP") or "ahp" in str(out).lower()


def test_rxnorm_local_fallback():
    out = clinical.rxnorm_normalize("naproxen")
    assert out.get("rxcui") == "7258" or "7258" in str(out)


def test_eligibility_happy_path():
    out = clinical.check_eligibility(
        member="AHP-0042-7781",
        serviceCode="72148",
        dateOfService="2026-01-15",
    )
    assert "error" not in out


def test_set_fault_drives_policy_missing_and_clears():
    armed = clinical.set_fault("policy_missing")
    assert armed["fault"] == "policy_missing"
    empty = clinical.policy_search(query="lumbar MRI CPT 72148")
    assert empty.get("hits") == []
    cleared = clinical.set_fault("none")
    assert cleared["fault"] == "none"
    restored = clinical.policy_search(query="lumbar MRI CPT 72148")
    assert restored.get("hits")
