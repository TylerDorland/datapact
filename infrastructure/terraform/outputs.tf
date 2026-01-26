output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "backend_url" {
  value = "https://${azurerm_linux_web_app.backend.default_hostname}"
}

output "frontend_url" {
  value = "https://${azurerm_linux_web_app.frontend.default_hostname}"
}

output "postgresql_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

# DataPact Outputs
output "datapact_contract_url" {
  value = "https://${azurerm_linux_web_app.datapact_contract.default_hostname}"
}

output "datapact_frontend_url" {
  value = "https://${azurerm_linux_web_app.datapact_frontend.default_hostname}"
}

output "datapact_redis_hostname" {
  value = azurerm_redis_cache.datapact.hostname
}
