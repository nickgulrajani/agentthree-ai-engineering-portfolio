# `terraform test` with mock providers: no credentials, no API calls, no cost.

mock_provider "aws" {
  mock_data "aws_iam_policy_document" {
    defaults = { json = "{}" }
  }
  mock_resource "aws_kms_key" {
    defaults = { arn = "arn:aws:kms:us-east-1:111122223333:key/00000000-0000-0000-0000-000000000000" }
  }
  mock_resource "aws_iam_openid_connect_provider" {
    defaults = { arn = "arn:aws:iam::111122223333:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/AGENTTHREE" }
  }
}
mock_provider "azurerm" {
  mock_resource "azurerm_user_assigned_identity" {
    defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-agentthree-zero-trust/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id-agentthree-orchestrator" }
  }
}
mock_provider "google" {
  mock_resource "google_service_account" {
    defaults = { name = "projects/agentthree-demo/serviceAccounts/agentthree-marketing-agent@agentthree-demo.iam.gserviceaccount.com" }
  }
}

run "aws_roles_are_bound_to_exact_subjects" {
  command = apply

  assert {
    condition     = length(module.aws.role_arns) == 1 && contains(keys(module.aws.role_arns), "claims-agent")
    error_message = "Only AWS workloads from trust.json may get an IAM role."
  }
  assert {
    condition = jsondecode(output.aws_trust_policies["claims-agent"]).Statement[0].Condition.StringEquals == {
      "oidc.eks.us-east-1.amazonaws.com/id/AGENTTHREE:sub" = "system:serviceaccount:agents:claims-agent"
      "oidc.eks.us-east-1.amazonaws.com/id/AGENTTHREE:aud" = "sts.amazonaws.com"
    }
    error_message = "IAM trust policy must pin both the service-account subject and audience."
  }
  assert {
    condition     = module.aws.session_seconds <= 900
    error_message = "Agents must request short-lived (<=15 min) STS sessions."
  }
}

run "azure_federation_has_no_secrets_and_exact_subject" {
  command = apply

  assert {
    condition     = output.azure_federated_subjects["orchestrator"] == "system:serviceaccount:agents:orchestrator"
    error_message = "Azure federated credential must pin the orchestrator's service-account subject."
  }
}

run "gcp_pool_rejects_unregistered_subjects" {
  command = apply

  assert {
    condition     = strcontains(output.gcp_attribute_condition, "'system:serviceaccount:marketing:marketing-agent'")
    error_message = "GCP attribute condition must allow-list registered subjects only."
  }
  assert {
    condition     = !strcontains(output.gcp_attribute_condition, "claims-agent")
    error_message = "AWS-hosted agents must not be federatable in GCP."
  }
}
