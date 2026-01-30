# Reference existing PostgreSQL server (in the other resource group)
data "azurerm_postgresql_flexible_server" "existing" {
  name                = var.existing_postgres_server_name
  resource_group_name = var.existing_resource_group
}

# Reference existing Container Registry
data "azurerm_container_registry" "existing" {
  name                = var.existing_acr_name
  resource_group_name = var.existing_resource_group
}
