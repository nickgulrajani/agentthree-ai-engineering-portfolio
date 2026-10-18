# MCP tool authorization: deny by default, least privilege, row-level filtering.
package agentthree.mcp

import rego.v1

ents := data.entitlements

default allow := false

agent := object.get(ents.agents, input.token.sub, null)

scopes := split(object.get(input.token, "scope", ""), " ")

deny contains "token audience does not match this MCP resource" if {
	input.token.aud != input.resource
}

deny contains "token expired" if {
	input.now >= input.token.exp
}

deny contains "agent has no data entitlements" if {
	agent == null
}

deny contains sprintf("tool %q is not exposed", [input.tool]) if {
	not ents.tool_scopes[input.tool]
}

deny contains sprintf("missing scope %q", [ents.tool_scopes[input.tool]]) if {
	not ents.tool_scopes[input.tool] in scopes
}

deny contains sprintf("dataset %q not entitled", [input.args.dataset]) if {
	agent != null
	input.tool == "query_records"
	not input.args.dataset in agent.datasets
}

deny contains sprintf("purpose %q not entitled", [object.get(input.args, "purpose", "")]) if {
	agent != null
	input.tool == "query_records"
	not object.get(input.args, "purpose", "") in agent.purposes
}

# Agent-to-agent delegation is re-checked here (defense in depth): the
# delegating agent must be allowed to delegate to this agent for this purpose.
deny contains "delegation chain too deep" if {
	d := input.token.delegation
	count(d.chain) > ents.max_delegation_depth
}

deny contains sprintf("%q may not delegate to %q", [d.from, input.token.sub]) if {
	d := input.token.delegation
	not input.token.sub in object.get(ents.a2a, d.from, {"may_delegate_to": []}).may_delegate_to
}

deny contains sprintf("%q may not delegate purpose %q", [d.from, object.get(input.args, "purpose", "")]) if {
	d := input.token.delegation
	input.tool == "query_records"
	not object.get(input.args, "purpose", "") in object.get(ents.a2a, d.from, {"purposes": []}).purposes
}

allow if count(deny) == 0

permitted_classifications contains c if {
	allow
	some c, rank in ents.classification_rank
	rank <= ents.classification_rank[agent.max_classification]
}

default permitted_datasets := []

permitted_datasets := agent.datasets if {
	allow
	agent != null
}

decision := {
	"allow": allow,
	"reasons": deny,
	"permitted_classifications": permitted_classifications,
	"permitted_datasets": permitted_datasets,
}
