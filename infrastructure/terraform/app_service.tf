resource "azurerm_service_plan" "main" {
  name                = "${var.project_name}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "backend" {
  name                = "${var.project_name}-backend"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "backend:latest"
      docker_registry_username = azurerm_container_registry.main.admin_username
      docker_registry_password = azurerm_container_registry.main.admin_password
    }
  }

  app_settings = {
    "DATABASE_URL"                        = "postgresql+asyncpg://${var.db_admin_username}:${var.db_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/test_database"
    "DATABASE_SSL"                        = "true"
    "WEBSITES_PORT"                       = "8000"
    "DOCKER_ENABLE_CI"                    = "true"
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
  }
}

resource "azurerm_linux_web_app" "frontend" {
  name                = "${var.project_name}-frontend"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_registry_url      = "https://${azurerm_container_registry.main.login_server}"
      docker_image_name        = "frontend:latest"
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
