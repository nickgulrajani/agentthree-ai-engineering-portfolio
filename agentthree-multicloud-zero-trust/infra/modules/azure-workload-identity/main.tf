# Azure: AKS workload identity -> user-assigned managed identity with a federated credential (no secrets).
terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
  }
}

variable "location" {
  type    = string
  default = "eastus"
}
variable "issuer_url" { type = string }
variable "audience" { type = string }
variable "workloads" {
  type = map(object({ subject = string }))
}

resource "azurerm_resource_group" "agents" {
  name     = "rg-agentthree-zero-trust"
  location = var.location
}

resource "azurerm_user_assigned_identity" "agent" {
  for_each            = var.workloads
  name                = "id-agentthree-${each.key}"
  location            = azurerm_resource_group.agents.location
  resource_group_name = azurerm_resource_group.agents.name
}

resource "azurerm_federated_identity_credential" "agent" {
  for_each                  = var.workloads
  name                      = "fic-${each.key}"
  user_assigned_identity_id = azurerm_user_assigned_identity.agent[each.key].id
  issuer                    = var.issuer_url
  subject                   = each.value.subject
  audience                  = [var.audience]
}

# Central audit sink for agent decisions (Sentinel-ready).
resource "azurerm_log_analytics_workspace" "audit" {
  name                = "law-agentthree-audit"
  location            = azurerm_resource_group.agents.location
  resource_group_name = azurerm_resource_group.agents.name
  sku                 = "PerGB2018"
  retention_in_days   = 90
}

output "client_ids" { value = { for k, i in azurerm_user_assigned_identity.agent : k => i.client_id } }
output "federated_subjects" { value = { for k, f in azurerm_federated_identity_credential.agent : k => f.subject } }
