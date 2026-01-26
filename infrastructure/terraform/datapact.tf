# Define predictable URLs to avoid circular dependencies
locals {
  datapact_contract_hostname     = "${var.project_name}-datapact-contract.azurewebsites.net"
  datapact_notification_hostname = "${var.project_name}-datapact-notification.azurewebsites.net"
  datapact_frontend_hostname     = "${var.project_name}-datapact-frontend.azurewebsites.net"
}

# DataPact Contract Service
resource "azurerm_linux_web_app" "datapact_contract" {
  name                = "${var.project_name}-datapact-contract"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/contract-service:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/datapact_contracts?sslmode=require"
    "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/0"
    "NOTIFICATION_SERVICE_URL"            = "https://${local.datapact_notification_hostname}"
    "CORS_ORIGINS"                        = "[\"https://${local.datapact_frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# DataPact Dictionary Service
resource "azurerm_linux_web_app" "datapact_dictionary" {
  name                = "${var.project_name}-datapact-dictionary"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/dictionary-service:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
  }

  app_settings = {
    "CONTRACT_SERVICE_URL"                = "https://${local.datapact_contract_hostname}"
    "CORS_ORIGINS"                        = "[\"https://${local.datapact_frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# DataPact Notification Service
resource "azurerm_linux_web_app" "datapact_notification" {
  name                = "${var.project_name}-datapact-notification"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/notification-service:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/datapact_notifications?sslmode=require"
    "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/1"
    "CONTRACT_SERVICE_URL"                = "https://${local.datapact_contract_hostname}"
    "FRONTEND_URL"                        = "https://${local.datapact_frontend_hostname}"
    "EMAIL_PROVIDER"                      = "azure"
    "ACS_CONNECTION_STRING"               = azurerm_communication_service.datapact.primary_connection_string
    "ACS_SENDER_ADDRESS"                  = "DoNotReply@${var.datapact_email_domain}"
    "CORS_ORIGINS"                        = "[\"https://${local.datapact_frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# DataPact Template Data Service
resource "azurerm_linux_web_app" "datapact_template" {
  name                = "${var.project_name}-datapact-template"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/template-data-service:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/datapact_template_data?sslmode=require"
    "CONTRACT_SERVICE_URL"                = "https://${local.datapact_contract_hostname}"
    "CORS_ORIGINS"                        = "[\"https://${local.datapact_frontend_hostname}\"]"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# DataPact Frontend
resource "azurerm_linux_web_app" "datapact_frontend" {
  name                = "${var.project_name}-datapact-frontend"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/frontend:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
  }

  app_settings = {
    "WEBSITES_PORT"                       = "80"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

# Celery Workers
resource "azurerm_linux_web_app" "datapact_compliance_worker" {
  name                = "${var.project_name}-datapact-compliance-worker"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/compliance-monitor:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
    app_command_line = "celery -A compliance_monitor.celery_app worker --loglevel=info -Q compliance"
  }

  app_settings = {
    "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/0"
    "CONTRACT_SERVICE_URL"                = "https://${local.datapact_contract_hostname}"
    "NOTIFICATION_SERVICE_URL"            = "https://${local.datapact_notification_hostname}"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

resource "azurerm_linux_web_app" "datapact_compliance_beat" {
  name                = "${var.project_name}-datapact-compliance-beat"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/compliance-monitor:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
    app_command_line = "celery -A compliance_monitor.celery_app beat --loglevel=info"
  }

  app_settings = {
    "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/0"
    "CONTRACT_SERVICE_URL"                = "https://${local.datapact_contract_hostname}"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

resource "azurerm_linux_web_app" "datapact_notification_worker" {
  name                = "${var.project_name}-datapact-notification-worker"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "datapact/notification-service:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
    app_command_line = "celery -A notification_service.celery_app worker --loglevel=info -Q notifications"
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/datapact_notifications?sslmode=require"
    "REDIS_URL"                           = "rediss://:${azurerm_redis_cache.datapact.primary_access_key}@${azurerm_redis_cache.datapact.hostname}:6380/1"
    "CONTRACT_SERVICE_URL"                = "https://${local.datapact_contract_hostname}"
    "EMAIL_PROVIDER"                      = "azure"
    "ACS_CONNECTION_STRING"               = azurerm_communication_service.datapact.primary_connection_string
    "ACS_SENDER_ADDRESS"                  = "DoNotReply@${var.datapact_email_domain}"
    "ENVIRONMENT"                         = "production"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}
