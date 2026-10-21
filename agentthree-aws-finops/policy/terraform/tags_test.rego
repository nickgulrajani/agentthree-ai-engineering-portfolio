package terraform.tags_test

import rego.v1
import data.terraform.tags

test_missing_tags_denied if {
	result := tags.deny with input as {"resource_changes": [{
		"address": "aws_s3_bucket.b",
		"change": {"actions": ["create"], "after": {
			"tags": {}, "tags_all": {"Owner": "data-eng"},
		}},
	}]}
	count(result) == 1
}

test_fully_tagged_allowed if {
	result := tags.deny with input as {"resource_changes": [{
		"address": "aws_s3_bucket.b",
		"change": {"actions": ["create"], "after": {"tags": {}, "tags_all": {
			"CostCenter": "CC-2210", "Owner": "data-eng",
			"Environment": "prod", "Application": "exports",
		}}},
	}]}
	count(result) == 0
}
