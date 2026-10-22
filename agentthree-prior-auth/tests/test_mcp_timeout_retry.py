"""MCP policy_search timeout drill: two failures, then retry succeeds."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp_servers.clinical import server as clinical  # noqa: E402

MEETS_NOTE = json.loads((ROOT / "evaluation" / "cases.json").read_text())[0]["note"]


@pytest.fixture(autouse=True)
def _clear_mcp_fault():
    clinical.set_fault("none")
    yield
    clinical.set_fault("none")


def test_policy_search_times_out_twice_then_retry_succeeds():
    armed = clinical.set_fault("mcp_timeout")
    assert armed["fault"] == "mcp_timeout"

    with pytest.raises(TimeoutError, match="timed out"):
        clinical.policy_search(query="lumbar MRI CPT 72148")
    with pytest.raises(TimeoutError, match="timed out"):
        clinical.policy_search(query="lumbar MRI CPT 72148")

    recovered = clinical.policy_search(query="lumbar MRI CPT 72148")
    assert recovered.get("hits")
    assert str(recovered.get("policyId", "")).upper().startswith("AHP")

    clinical.set_fault("none")
    restored = clinical.policy_search(query="lumbar MRI CPT 72148")
    assert restored.get("hits")


def test_set_fault_resets_timeout_counter_for_a_fresh_retry_cycle():
    clinical.set_fault("mcp_timeout")
    with pytest.raises(TimeoutError):
        clinical.policy_search(query="lumbar MRI CPT 72148")

    rearmed = clinical.set_fault("mcp_timeout")
    assert rearmed["fault"] == "mcp_timeout"
    with pytest.raises(TimeoutError, match="timed out"):
        clinical.policy_search(query="lumbar MRI CPT 72148")
    with pytest.raises(TimeoutError, match="timed out"):
        clinical.policy_search(query="lumbar MRI CPT 72148")
    recovered = clinical.policy_search(query="lumbar MRI CPT 72148")
    assert recovered.get("hits")


def _mcp_ok(structured: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], int]:
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/call"}
    res = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": "(structured result below)"}],
            "structuredContent": structured,
            "isError": False,
        },
    }
    return req, res, 10


def _mcp_err(message: str, dur: int = 5000) -> tuple[dict[str, Any], dict[str, Any], int]:
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/call"}
    res = {"jsonrpc": "2.0", "id": 1, "error": {"code": -32603, "message": message}}
    return req, res, dur


def test_pipeline_retries_policy_search_after_mcp_timeouts(monkeypatch):
    policy_calls = {"n": 0}

    async def fake_call_tool(name: str, arguments: dict[str, Any], url: str | None = None):
        if name == "policy_search":
            policy_calls["n"] += 1
            if policy_calls["n"] <= 2:
                return _mcp_err("Request timed out after 5000 ms")
            return _mcp_ok(
                {
                    "hits": [
                        {
                            "chunk": "AHP-RAD-014 §5",
                            "score": 0.91,
                            "text": "Lumbar MRI CPT 72148 after 6 weeks conservative care.",
                        }
                    ],
                    "policyId": "AHP-RAD-014",
                    "policyVersion": "2024.1",
                }
            )
        if name == "set_fault":
            return _mcp_ok({"ok": True, "fault": arguments.get("fault", "none")})
        if name == "fhir_read":
            return _mcp_ok({"resourceType": "Patient", "id": "demo-7781"})
        if name == "fhir_search":
            return _mcp_ok({"total": 0, "entry": []})
        if name == "rxnorm_normalize":
            return _mcp_ok({"rxcui": "7258", "name": "naproxen", "source": "local-fallback"})
        if name == "check_eligibility":
            return _mcp_ok(
                {
                    "active": True,
                    "paRequired": True,
                    "member": arguments.get("member"),
                    "serviceCode": arguments.get("serviceCode"),
                }
            )
        if name == "guideline_search":
            return _mcp_ok(
                {
                    "hits": [
                        {
                            "id": "GL-ACP-2017 rec 3",
                            "score": 0.88,
                            "text": "Imaging after conservative therapy.",
                        }
                    ]
                }
            )
        return _mcp_ok({})

    async def no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr("agentthree.pipeline.call_tool", fake_call_tool)
    monkeypatch.setattr("agentthree.pipeline.DEMO_MODE", True)
    monkeypatch.setattr("agentthree.pipeline.GOOGLE_API_KEY", "")
    monkeypatch.setattr("agentthree.gemini_steps.DEMO_MODE", True)
    monkeypatch.setattr("agentthree.gemini_steps.GOOGLE_API_KEY", "")
    monkeypatch.setattr("agentthree.pipeline.asyncio.sleep", no_sleep)

    from agentthree.pipeline import run_case

    result = asyncio.run(
        run_case(
            patient_name="Jordan Rivera (fictional)",
            dob="1968-03-14",
            member="AHP-0042-7781",
            payer="Acme Health Plan (fictional)",
            cpt="72148",
            icd="M54.16",
            note=MEETS_NOTE,
            fault="mcp_timeout",
        )
    )

    assert policy_calls["n"] == 3
    policy_tools = [t for t in result["tools"] if t["tool"] == "policy_search"]
    assert len(policy_tools) == 3
    assert policy_tools[0]["error"] is True
    assert policy_tools[1]["error"] is True
    assert policy_tools[2]["error"] is False
    assert policy_tools[0]["attempt"] == 1
    assert policy_tools[1]["attempt"] == 2
    assert policy_tools[2]["attempt"] == 3

    retries = [e for e in result["events"] if e["kind"] == "retry"]
    assert retries
    assert any("policy_search" in (e.get("title") or "") for e in retries)

    timeout_faults = [f for f in result["faults"] if f.get("type") == "mcp_timeout"]
    assert timeout_faults
    assert timeout_faults[0]["recovered"] is True
    assert timeout_faults[0]["escalated"] is False
    assert "retry" in timeout_faults[0]["handling"]
    assert result["pol"]["outcome"] == "meets"
