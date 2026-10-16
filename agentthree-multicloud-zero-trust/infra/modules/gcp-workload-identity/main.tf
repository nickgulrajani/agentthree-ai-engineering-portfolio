# GCP: Workload Identity Federation pool/provider -> per-agent service account, impersonation bound to one subject.
terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}

variable "project_id" { type = string }
variable "project_number" { type = string }
variable "issuer_url" { type = string }
variable "audience" { type = string }
variable "workloads" {
  type = map(object({ subject = string }))
}

resource "google_iam_workload_identity_pool" "agents" {
  project                   = var.project_id
  workload_identity_pool_id = "agentthree-agents"
  display_name              = "AgentThree agents"
}

resource "google_iam_workload_identity_pool_provider" "oidc" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.agents.workload_identity_pool_id
  workload_identity_pool_provider_id = "agents-oidc"

  attribute_mapping = {
    "google.subject" = "assertion.sub"
  }
  # Only explicitly registered agent subjects can even attempt federation.
  attribute_condition = "assertion.sub in [${join(", ", [for w in var.workloads : "'${w.subject}'"])}]"

  oidc {
    issuer_uri        = var.issuer_url
    allowed_audiences = [var.audience]
  }
}

resource "google_service_account" "agent" {
  for_each     = var.workloads
  project      = var.project_id
  account_id   = "agentthree-${each.key}"
  display_name = "AgentThree ${each.key}"
}

resource "google_service_account_iam_member" "wif" {
  for_each           = var.workloads
  service_account_id = google_service_account.agent[each.key].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principal://iam.googleapis.com/projects/${var.project_number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.agents.workload_identity_pool_id}/subject/${each.value.subject}"
}

output "service_accounts" { value = { for k, s in google_service_account.agent : k => s.email } }
output "attribute_condition" { value = google_iam_workload_identity_pool_provider.oidc.attribute_condition }
