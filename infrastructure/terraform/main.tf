terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "azurerm" {
  features {}
  subscription_id                 = var.subscription_id
  resource_provider_registrations = "none"
}

# DataPact's own resource group
resource "azurerm_resource_group" "datapact" {
  name     = "${var.project_name}-datapact-rg"
  location = var.location

  lifecycle {
    prevent_destroy = true
  }
}
