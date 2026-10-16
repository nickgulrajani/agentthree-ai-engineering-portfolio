"""MCP tool contract definitions and validators (no live MCP server required)."""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

# Canonical allowlisted tools for the healthcare agent gateway.
MCP_TOOL_CATALOG: list[dict[str, Any]] = [
    {
        "name": "fhir_patient_lookup",
        "description": "Fetch a patient record when the caller has patient-level authorization",
        "inputSchema": {
            "type": "object",
            "required": ["patient_id", "principal"],
            "properties": {
                "patient_id": {"type": "string", "minLength": 1},
                "principal": {
                    "type": "object",
                    "required": ["id", "scopes"],
                    "properties": {
                        "id": {"type": "string"},
                        "scopes": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "additionalProperties": False,
        },
        "required_scopes": ["patient:read"],
    },
    {
        "name": "policy_evaluate",
        "description": "Evaluate prior-auth policy against structured clinical entities",
        "inputSchema": {
            "type": "object",
            "required": ["cpt", "icd", "entities"],
            "properties": {
                "cpt": {"type": "string"},
                "icd": {"type": "string"},
                "entities": {"type": "object"},
            },
            "additionalProperties": False,
        },
        "required_scopes": ["policy:evaluate"],
    },
]

FORBIDDEN_TOOL_NAMES = {
    "shell_exec",
    "raw_sql",
    "exfiltrate_phi",
    "disable_audit",
}


def validate_tool_schema(tool: dict[str, Any]) -> list[str]:
    """Return human-readable contract violations for a single tool definition."""
    errors: list[str] = []
    name = tool.get("name")
    if not name or not isinstance(name, str):
        errors.append("tool missing name")
        return errors
    if name in FORBIDDEN_TOOL_NAMES:
        errors.append(f"forbidden tool registered: {name}")
    if "inputSchema" not in tool:
        errors.append(f"{name}: missing inputSchema")
    else:
        try:
            Draft202012Validator.check_schema(tool["inputSchema"])
        except Exception as exc:  # noqa: BLE001 — surface schema errors as contract fails
            errors.append(f"{name}: invalid inputSchema ({exc})")
    scopes = tool.get("required_scopes") or []
    if not scopes:
        errors.append(f"{name}: required_scopes must be non-empty (deny-by-default)")
    return errors


def authorize_tool_call(tool_name: str, principal_scopes: list[str]) -> bool:
    """Deny-by-default authorization against the allowlisted catalog."""
    for tool in MCP_TOOL_CATALOG:
        if tool["name"] == tool_name:
            needed = set(tool["required_scopes"])
            return needed.issubset(set(principal_scopes))
    return False


def validate_catalog(catalog: list[dict[str, Any]] | None = None) -> list[str]:
    catalog = catalog if catalog is not None else MCP_TOOL_CATALOG
    findings: list[str] = []
    for tool in catalog:
        findings.extend(validate_tool_schema(tool))
    names = [t.get("name") for t in catalog]
    if len(names) != len(set(names)):
        findings.append("duplicate tool names in catalog")
    return findings
