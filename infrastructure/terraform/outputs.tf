output "resource_group_name" {
  value = azurerm_resource_group.datapact.name
}

output "contract_service_url" {
  value = "https://${azurerm_linux_web_app.contract.default_hostname}"
}

output "dictionary_service_url" {
  value = "https://${azurerm_linux_web_app.dictionary.default_hostname}"
}

output "notification_service_url" {
  value = "https://${azurerm_linux_web_app.notification.default_hostname}"
}

output "template_service_url" {
  value = "https://${azurerm_linux_web_app.template.default_hostname}"
}

output "frontend_url" {
  value = "https://${azurerm_linux_web_app.frontend.default_hostname}"
}

output "communication_service_name" {
  value = azurerm_communication_service.datapact.name
}
