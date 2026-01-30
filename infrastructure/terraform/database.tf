# DataPact databases on the existing PostgreSQL server
# Note: These are created in the existing server's resource group

resource "azurerm_postgresql_flexible_server_database" "contracts" {
  name      = "datapact_contracts"
  server_id = data.azurerm_postgresql_flexible_server.existing.id
  charset   = "UTF8"
  collation = "en_US.utf8"

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_postgresql_flexible_server_database" "notifications" {
  name      = "datapact_notifications"
  server_id = data.azurerm_postgresql_flexible_server.existing.id
  charset   = "UTF8"
  collation = "en_US.utf8"

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_postgresql_flexible_server_database" "template_data" {
  name      = "datapact_template_data"
  server_id = data.azurerm_postgresql_flexible_server.existing.id
  charset   = "UTF8"
  collation = "en_US.utf8"

  lifecycle {
    prevent_destroy = true
  }
}
