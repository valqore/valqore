terraform {
  required_version = ">= 1.0"
  backend "local" {}
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "rg-webapp-prod"
  location = "East US"
}

resource "azurerm_service_plan" "main" {
  name                = "plan-webapp"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "P2v3"
}

resource "azurerm_linux_web_app" "api" {
  name                = "webapp-api-prod"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    always_on        = true
    ftps_state       = "AllAllowed"
    http2_enabled    = false
    minimum_tls_version = "1.0"
  }

  app_settings = {
    "DB_PASSWORD"     = "prod-password-123"
    "API_SECRET_KEY"  = "sk-prod-abc123xyz"
  }
}

resource "azurerm_mssql_server" "main" {
  name                         = "sql-webapp-prod"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd123!"

  public_network_access_enabled = true
}

resource "azurerm_mssql_database" "main" {
  name      = "db-webapp"
  server_id = azurerm_mssql_server.main.id
  sku_name  = "S3"
}

resource "azurerm_storage_account" "data" {
  name                     = "stwebappprod"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  allow_nested_items_to_be_public = true
  min_tls_version                 = "TLS1_0"
}
