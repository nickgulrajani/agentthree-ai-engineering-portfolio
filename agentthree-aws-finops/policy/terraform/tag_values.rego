package terraform.tag_values

import rego.v1

allowed_env := {"prod", "staging", "dev", "loadtest"}

deny contains msg if {
	some rc in input.resource_changes
	"create" in rc.change.actions
	env := rc.change.after.tags_all.Environment
	not env in allowed_env
	msg := sprintf("%s has Environment=%q; allowed: %v", [rc.address, env, allowed_env])
}

deny contains msg if {
	some rc in input.resource_changes
	"create" in rc.change.actions
	cc := rc.change.after.tags_all.CostCenter
	not regex.match(`^CC-[0-9]{4}$`, cc)
	msg := sprintf("%s has CostCenter=%q; expected format CC-1234", [rc.address, cc])
}
