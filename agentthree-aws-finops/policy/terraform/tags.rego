package terraform.tags

import rego.v1

required := {"CostCenter", "Owner", "Environment", "Application"}

# tags_all merges resource tags with provider default_tags
deny contains msg if {
	some rc in input.resource_changes
	"create" in rc.change.actions
	"tags" in object.keys(rc.change.after)
	tags := object.get(rc.change.after, "tags_all", {})
	missing := required - {k | some k, _ in tags}
	count(missing) > 0
	msg := sprintf("%s is missing required tags: %v", [rc.address, missing])
}
