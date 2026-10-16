"""MCP contract tests — schema, allowlist, deny-by-default authorization."""

from agentthree_devsecops.mcp_contract import (
    FORBIDDEN_TOOL_NAMES,
    MCP_TOOL_CATALOG,
    authorize_tool_call,
    validate_catalog,
    validate_tool_schema,
)


def test_catalog_passes_contract():
    assert validate_catalog() == []


def test_forbidden_tool_rejected():
    bad = {
        "name": "shell_exec",
        "inputSchema": {"type": "object", "properties": {}},
        "required_scopes": ["admin"],
    }
    errors = validate_tool_schema(bad)
    assert any("forbidden" in e for e in errors)
    assert "shell_exec" in FORBIDDEN_TOOL_NAMES


def test_missing_scopes_rejected():
    bad = {
        "name": "fhir_patient_lookup",
        "inputSchema": {"type": "object", "properties": {}},
        "required_scopes": [],
    }
    errors = validate_tool_schema(bad)
    assert any("required_scopes" in e for e in errors)


def test_authorize_deny_by_default():
    assert authorize_tool_call("fhir_patient_lookup", ["patient:read"]) is True
    assert authorize_tool_call("fhir_patient_lookup", ["policy:evaluate"]) is False
    assert authorize_tool_call("unknown_tool", ["admin"]) is False


def test_catalog_has_expected_tools():
    names = {t["name"] for t in MCP_TOOL_CATALOG}
    assert "fhir_patient_lookup" in names
    assert "policy_evaluate" in names
