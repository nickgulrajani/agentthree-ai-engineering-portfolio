package agentthree_test

import rego.v1

import data.agentthree.a2a
import data.agentthree.mcp

resource := "https://mcp.agentthree.local/records"

claims_token := {"sub": "claims-agent", "aud": resource, "exp": 1300, "scope": "records:read a2a:accept"}

claims_query := {
	"resource": resource,
	"now": 1000,
	"tool": "query_records",
	"token": claims_token,
	"args": {"dataset": "claims", "purpose": "claims-adjudication"},
}

test_claims_agent_allowed if {
	mcp.allow with input as claims_query
}

test_claims_agent_never_sees_restricted if {
	d := mcp.decision with input as claims_query
	not "restricted" in d.permitted_classifications
	"confidential" in d.permitted_classifications
}

test_marketing_agent_denied_claims if {
	not mcp.allow with input as object.union(claims_query, {"token": object.union(claims_token, {"sub": "marketing-agent"})})
}

test_wrong_purpose_denied if {
	not mcp.allow with input as object.union(claims_query, {"args": {"dataset": "claims", "purpose": "marketing"}})
}

test_expired_token_denied if {
	not mcp.allow with input as object.union(claims_query, {"now": 1300})
}

test_wrong_audience_denied if {
	not mcp.allow with input as object.union(claims_query, {"resource": "https://other.example"})
}

test_missing_scope_denied if {
	not mcp.allow with input as object.union(claims_query, {"token": object.union(claims_token, {"scope": "a2a:accept"})})
}

test_unknown_tool_denied if {
	not mcp.allow with input as object.union(claims_query, {"tool": "delete_records"})
}

test_valid_delegation_allowed if {
	tok := object.union(claims_token, {"delegation": {"from": "orchestrator", "chain": ["orchestrator"]}})
	mcp.allow with input as object.union(claims_query, {"token": tok})
}

test_laundered_delegation_denied if {
	tok := object.union(claims_token, {"delegation": {"from": "marketing-agent", "chain": ["marketing-agent"]}})
	not mcp.allow with input as object.union(claims_query, {"token": tok})
}

test_deep_delegation_denied if {
	tok := object.union(claims_token, {"delegation": {"from": "orchestrator", "chain": ["x", "orchestrator"]}})
	not mcp.allow with input as object.union(claims_query, {"token": tok})
}

a2a_input := {
	"now": 1000,
	"callee": "claims-agent",
	"caller": {"sub": "orchestrator", "aud": "agent://claims-agent", "exp": 1300, "scope": "a2a:delegate"},
	"task": {"purpose": "claims-adjudication"},
}

test_a2a_orchestrator_allowed if {
	a2a.allow with input as a2a_input
}

test_a2a_marketing_denied if {
	not a2a.allow with input as object.union(a2a_input, {"caller": object.union(a2a_input.caller, {"sub": "marketing-agent"})})
}

test_a2a_bad_purpose_denied if {
	not a2a.allow with input as object.union(a2a_input, {"task": {"purpose": "upsell"}})
}

test_a2a_wrong_audience_denied if {
	not a2a.allow with input as object.union(a2a_input, {"caller": object.union(a2a_input.caller, {"aud": "agent://other"})})
}
