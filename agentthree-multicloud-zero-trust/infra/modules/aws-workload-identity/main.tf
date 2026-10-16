# AWS: EKS IRSA-style OIDC federation -> per-agent IAM role -> least-privilege DynamoDB access.
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

variable "issuer_url" { type = string }
variable "audience" { type = string }
variable "workloads" {
  description = "name => { subject, datasets }"
  type        = map(object({ subject = string, datasets = list(string) }))
}
variable "session_seconds" {
  description = "Requested STS session length. AWS floor for role max is 3600; agents request this shorter value."
  type        = number
  default     = 900
}

locals {
  issuer_host = replace(var.issuer_url, "https://", "")
}

resource "aws_iam_openid_connect_provider" "agents" {
  url             = var.issuer_url
  client_id_list  = [var.audience]
  thumbprint_list = ["9e99a48a9960b14926bb7f3b02e22da2b0ab7280"]
}

locals {
  # Built in HCL (not a data source) so `terraform test` can assert on the exact conditions.
  trust_policies = {
    for name, w in var.workloads : name => jsonencode({
      Version = "2012-10-17"
      Statement = [{
        Effect    = "Allow"
        Action    = "sts:AssumeRoleWithWebIdentity"
        Principal = { Federated = aws_iam_openid_connect_provider.agents.arn }
        Condition = {
          StringEquals = {
            "${local.issuer_host}:sub" = w.subject
            "${local.issuer_host}:aud" = var.audience
          }
        }
      }]
    })
  }
}

resource "aws_iam_role" "agent" {
  for_each             = var.workloads
  name                 = "agentthree-${each.key}"
  assume_role_policy   = local.trust_policies[each.key]
  max_session_duration = 3600
  tags                 = { agent = each.key, zero_trust = "true" }
}

resource "aws_kms_key" "records" {
  description         = "agentthree records CMK"
  enable_key_rotation = true
}

resource "aws_dynamodb_table" "records" {
  name         = "agentthree-records"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "dataset"
  range_key    = "id"

  attribute {
    name = "dataset"
    type = "S"
  }
  attribute {
    name = "id"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.records.arn
  }
  point_in_time_recovery { enabled = true }
}

# Row-level least privilege: an agent may only Query partitions (datasets) it is entitled to.
data "aws_iam_policy_document" "data_access" {
  for_each = { for k, v in var.workloads : k => v if length(v.datasets) > 0 }

  statement {
    actions   = ["dynamodb:Query", "dynamodb:GetItem"]
    resources = [aws_dynamodb_table.records.arn]
    condition {
      test     = "ForAllValues:StringEquals"
      variable = "dynamodb:LeadingKeys"
      values   = each.value.datasets
    }
  }
}

resource "aws_iam_role_policy" "data_access" {
  for_each = data.aws_iam_policy_document.data_access
  name     = "records-least-privilege"
  role     = aws_iam_role.agent[each.key].id
  policy   = each.value.json
}

output "role_arns" { value = { for k, r in aws_iam_role.agent : k => r.arn } }
output "trust_policies" { value = local.trust_policies }
output "session_seconds" { value = var.session_seconds }
