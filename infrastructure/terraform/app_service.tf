# Define predictable URLs to avoid circular dependencies
locals {
  contract_hostname     = "${var.project_name}-datapact-contract.azurewebsites.net"
  notification_hostname = "${var.project_name}-datapact-notification.azurewebsites.net"
  frontend_hostname     = "${var.project_name}-datapact-frontend.azurewebsites.net"
}

# DataPact's own App Service Plan
resource "azurerm_service_plan" "datapact" {
  name                = "${var.project_name}-datapact-plan"
  resource_group_name = azurerm_resource_group.datapact.name
  location            = azurerm_resource_group.datapact.location
  os_type             = "Linux"
  sku_name            = "B1"

  lifecycle {
    prevent_destroy = true
  }
}

# Contract Service
resource "azurerm_linux_web_app" "contract" {
  name                = "${var.project_name}-datapact-contract"
  resource_group_name = azurerm_resource_group.datapact.name
  location            = azurerm_resource_group.datapact.location
  service_plan_id     = azurerm_service_plan.datapact.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
      docker_image_name        = "datapact/contract-service:latest"
      docker_registry_username = data.azurerm_container_registry.existing.admin_username
      docker_registry_password = data.azurerm_container_registry.existing.admin_password
    }
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${data.azurerm_postgresql_flexible_server.existing.fqdn}:5432/datapact_contracts?sslmode=require"
    "NOTIFICATION_SERVICE_URL"            = "https://${local.notification_hostname}"
    "CORS_ORIGINS"                        = "[\"https://${local.frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# Dictionary Service
resource "azurerm_linux_web_app" "dictionary" {
  name                = "${var.project_name}-datapact-dictionary"
  resource_group_name = azurerm_resource_group.datapact.name
  location            = azurerm_resource_group.datapact.location
  service_plan_id     = azurerm_service_plan.datapact.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
      docker_image_name        = "datapact/dictionary-service:latest"
      docker_registry_username = data.azurerm_container_registry.existing.admin_username
      docker_registry_password = data.azurerm_container_registry.existing.admin_password
    }
  }

  app_settings = {
    "CONTRACT_SERVICE_URL"                = "https://${local.contract_hostname}"
    "CORS_ORIGINS"                        = "[\"https://${local.frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# Notification Service
resource "azurerm_linux_web_app" "notification" {
  name                = "${var.project_name}-datapact-notification"
  resource_group_name = azurerm_resource_group.datapact.name
  location            = azurerm_resource_group.datapact.location
  service_plan_id     = azurerm_service_plan.datapact.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
      docker_image_name        = "datapact/notification-service:latest"
      docker_registry_username = data.azurerm_container_registry.existing.admin_username
      docker_registry_password = data.azurerm_container_registry.existing.admin_password
    }
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${data.azurerm_postgresql_flexible_server.existing.fqdn}:5432/datapact_notifications?sslmode=require"
    "CONTRACT_SERVICE_URL"                = "https://${local.contract_hostname}"
    "FRONTEND_URL"                        = "https://${local.frontend_hostname}"
    "EMAIL_PROVIDER"                      = "azure"
    "ACS_CONNECTION_STRING"               = azurerm_communication_service.datapact.primary_connection_string
    "ACS_SENDER_ADDRESS"                  = "DoNotReply@${var.datapact_email_domain}"
    "CORS_ORIGINS"                        = "[\"https://${local.frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# Template Data Service
resource "azurerm_linux_web_app" "template" {
  name                = "${var.project_name}-datapact-template"
  resource_group_name = azurerm_resource_group.datapact.name
  location            = azurerm_resource_group.datapact.location
  service_plan_id     = azurerm_service_plan.datapact.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
      docker_image_name        = "datapact/template-data-service:latest"
      docker_registry_username = data.azurerm_container_registry.existing.admin_username
      docker_registry_password = data.azurerm_container_registry.existing.admin_password
    }
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${data.azurerm_postgresql_flexible_server.existing.fqdn}:5432/datapact_template_data?sslmode=require"
    "CONTRACT_SERVICE_URL"                = "https://${local.contract_hostname}"
    "CORS_ORIGINS"                        = "[\"https://${local.frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# Frontend
resource "azurerm_linux_web_app" "frontend" {
  name                = "${var.project_name}-datapact-frontend"
  resource_group_name = azurerm_resource_group.datapact.name
  location            = azurerm_resource_group.datapact.location
  service_plan_id     = azurerm_service_plan.datapact.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
      docker_image_name        = "datapact/frontend:latest"
      docker_registry_username = data.azurerm_container_registry.existing.admin_username
      docker_registry_password = data.azurerm_container_registry.existing.admin_password
    }
  }

  app_settings = {
    "WEBSITES_PORT"                       = "80"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# Celery Workers - Disabled for now (requires Redis which takes 15 min to provision)
# Uncomment when compliance monitoring is needed
#
# resource "azurerm_linux_web_app" "compliance_worker" {
#   name                = "${var.project_name}-datapact-compliance-worker"
#   resource_group_name = azurerm_resource_group.datapact.name
#   location            = azurerm_resource_group.datapact.location
#   service_plan_id     = azurerm_service_plan.datapact.id
#
#   site_config {
#     application_stack {
#       docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
#       docker_image_name        = "datapact/compliance-monitor:latest"
#       docker_registry_username = data.azurerm_container_registry.existing.admin_username
#       docker_registry_password = data.azurerm_container_registry.existing.admin_password
#     }
#     app_command_line = "celery -A compliance_monitor.celery_app worker --loglevel=info -Q compliance"
#   }
#
#   app_settings = {
#     "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/0"
#     "CONTRACT_SERVICE_URL"                = "https://${local.contract_hostname}"
#     "NOTIFICATION_SERVICE_URL"            = "https://${local.notification_hostname}"
#     "ENVIRONMENT"                         = "production"
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
#   }
# }
#
# resource "azurerm_linux_web_app" "compliance_beat" {
#   name                = "${var.project_name}-datapact-compliance-beat"
#   resource_group_name = azurerm_resource_group.datapact.name
#   location            = azurerm_resource_group.datapact.location
#   service_plan_id     = azurerm_service_plan.datapact.id
#
#   site_config {
#     application_stack {
#       docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
#       docker_image_name        = "datapact/compliance-monitor:latest"
#       docker_registry_username = data.azurerm_container_registry.existing.admin_username
#       docker_registry_password = data.azurerm_container_registry.existing.admin_password
#     }
#     app_command_line = "celery -A compliance_monitor.celery_app beat --loglevel=info"
#   }
#
#   app_settings = {
#     "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/0"
#     "CONTRACT_SERVICE_URL"                = "https://${local.contract_hostname}"
#     "ENVIRONMENT"                         = "production"
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
#   }
# }
#
# resource "azurerm_linux_web_app" "notification_worker" {
#   name                = "${var.project_name}-datapact-notification-worker"
#   resource_group_name = azurerm_resource_group.datapact.name
#   location            = azurerm_resource_group.datapact.location
#   service_plan_id     = azurerm_service_plan.datapact.id
#
#   site_config {
#     application_stack {
#       docker_registry_url      = "https://${data.azurerm_container_registry.existing.login_server}"
#       docker_image_name        = "datapact/notification-service:latest"
#       docker_registry_username = data.azurerm_container_registry.existing.admin_username
#       docker_registry_password = data.azurerm_container_registry.existing.admin_password
#     }
#     app_command_line = "celery -A notification_service.celery_app worker --loglevel=info -Q notifications"
#   }
#
#   app_settings = {
#     "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${data.azurerm_postgresql_flexible_server.existing.fqdn}:5432/datapact_notifications?sslmode=require"
#     "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/1"
#     "CONTRACT_SERVICE_URL"                = "https://${local.contract_hostname}"
#     "EMAIL_PROVIDER"                      = "azure"
#     "ACS_CONNECTION_STRING"               = azurerm_communication_service.datapact.primary_connection_string
#     "ACS_SENDER_ADDRESS"                  = "DoNotReply@${var.datapact_email_domain}"
#     "ENVIRONMENT"                         = "production"
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
#   }
# }
