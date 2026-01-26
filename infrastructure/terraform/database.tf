resource "azurerm_postgresql_flexible_server" "main" {
  name                          = "${var.project_name}-pgserver"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  version                       = "16"
  administrator_login           = var.db_admin_username
  administrator_password        = var.db_admin_password
  storage_mb                    = 32768
  sku_name                      = "B_Standard_B1ms"
  public_network_access_enabled = true

  lifecycle {
    ignore_changes = [
      zone,
      high_availability[0].standby_availability_zone
    ]
  }
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "test_database"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# DataPact Databases
resource "azurerm_postgresql_flexible_server_database" "datapact_contracts" {
  name      = "datapact_contracts"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_database" "datapact_notifications" {
  name      = "datapact_notifications"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_postgresql_flexible_server_database" "datapact_template_data" {
  name      = "datapact_template_data"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}
