# Multi-cloud zero-trust root. Driven by config/trust.json and policy/entitlements/data.json —
# the same files the local runtime enforces. Validated and tested with mock providers: never applied by default.
terraform {
  required_version = ">= 1.7.0"
}

locals {
  trust        = jsondecode(file("${path.module}/../../../config/trust.json"))
  entitlements = jsondecode(file("${path.module}/../../../policy/entitlements/data.json"))

  workloads_by_cloud = {
    for cloud in ["aws", "azure", "gcp"] : cloud => {
      for name, w in local.trust.workloads : name => {
        subject  = w.subject
        datasets = try(local.entitlements.agents[name].datasets, [])
      } if w.cloud == cloud
    }
  }
}

variable "gcp_project_id" {
  type    = string
  default = "agentthree-demo"
}
variable "gcp_project_number" {
  type    = string
  default = "000000000000"
}

provider "aws" {
  region = "us-east-1"
}
provider "azurerm" {
  features {}
}
provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
}

module "aws" {
  source     = "../../modules/aws-workload-identity"
  issuer_url = local.trust.issuers.aws.issuer
  audience   = local.trust.issuers.aws.audience
  workloads  = local.workloads_by_cloud.aws
}

module "azure" {
  source     = "../../modules/azure-workload-identity"
  issuer_url = local.trust.issuers.azure.issuer
  audience   = local.trust.issuers.azure.audience
  workloads  = { for k, v in local.workloads_by_cloud.azure : k => { subject = v.subject } }
}

module "gcp" {
  source         = "../../modules/gcp-workload-identity"
  project_id     = var.gcp_project_id
  project_number = var.gcp_project_number
  issuer_url     = local.trust.issuers.gcp.issuer
  audience       = local.trust.issuers.gcp.audience
  workloads      = { for k, v in local.workloads_by_cloud.gcp : k => { subject = v.subject } }
}

output "aws_trust_policies" { value = module.aws.trust_policies }
output "azure_federated_subjects" { value = module.azure.federated_subjects }
output "gcp_attribute_condition" { value = module.gcp.attribute_condition }
