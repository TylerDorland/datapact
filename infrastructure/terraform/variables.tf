variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "project_name" {
  description = "Project name prefix for resources"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westus2"
}

variable "db_admin_username" {
  description = "PostgreSQL admin username"
  type        = string
}

variable "db_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "datapact_email_domain" {
  description = "Email domain for Azure Communication Services"
  type        = string
  default     = ""
}

# Reference to existing infrastructure
variable "existing_resource_group" {
  description = "Name of the existing resource group containing PostgreSQL and ACR"
  type        = string
}

variable "existing_postgres_server_name" {
  description = "Name of the existing PostgreSQL flexible server"
  type        = string
}

variable "existing_acr_name" {
  description = "Name of the existing Azure Container Registry"
  type        = string
}
