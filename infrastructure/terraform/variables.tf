variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "azuretestdata"
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "eastus"
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "db_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "pgadmin"
}

variable "db_admin_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true
}

variable "datapact_email_domain" {
  description = "Email domain for DataPact notifications (must be verified in ACS)"
  type        = string
  default     = "yourdomain.com"
}
