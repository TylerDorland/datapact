resource "azurerm_communication_service" "datapact" {
  name                = "${var.project_name}-datapact-comm"
  resource_group_name = azurerm_resource_group.datapact.name
  data_location       = "United States"
}

# Note: Email domain verification must be done manually in Azure Portal
# after the Communication Service is created
