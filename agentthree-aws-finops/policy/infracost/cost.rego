package infracost

import rego.v1

review_threshold := 1000

warn contains msg if {
	diff := to_number(input.diffTotalMonthlyCost)
	diff > review_threshold
	msg := sprintf("PR adds $%v/month (threshold $%v); FinOps review required", [round(diff), review_threshold])
}

deny contains msg if {
	some project in input.projects
	some r in project.breakdown.resources
	to_number(r.monthlyCost) > 5000
	msg := sprintf("%s costs $%v/month; over $5,000 needs architecture review", [r.name, round(to_number(r.monthlyCost))])
}
