# Agent-to-agent trust: a callee only accepts tasks from verified callers that
# are explicitly allowed to delegate to it, for an allowed purpose.
package agentthree.a2a

import rego.v1

ents := data.entitlements

default allow := false

caller := object.get(ents.a2a, input.caller.sub, null)

deny contains "caller token not addressed to this agent" if {
	input.caller.aud != concat("", ["agent://", input.callee])
}

deny contains "caller token expired" if {
	input.now >= input.caller.exp
}

deny contains "caller lacks a2a:delegate scope" if {
	not "a2a:delegate" in split(object.get(input.caller, "scope", ""), " ")
}

deny contains sprintf("%q is not trusted to delegate", [input.caller.sub]) if {
	caller == null
}

deny contains sprintf("%q may not delegate to %q", [input.caller.sub, input.callee]) if {
	caller != null
	not input.callee in caller.may_delegate_to
}

deny contains sprintf("purpose %q not allowed for %q", [input.task.purpose, input.caller.sub]) if {
	caller != null
	not input.task.purpose in caller.purposes
}

allow if count(deny) == 0

decision := {"allow": allow, "reasons": deny}
