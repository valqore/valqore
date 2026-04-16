terraform {
  required_version = ">= 1.0"
  backend "local" {}
}

provider "google" {
  project = "my-project-id"
  region  = "us-central1"
}

resource "google_container_cluster" "primary" {
  name     = "gke-prod"
  location = "us-central1"

  initial_node_count = 3

  # Legacy ABAC enabled - should use RBAC
  enable_legacy_abac = true

  # No network policy
  network_policy {
    enabled = false
  }

  # Master authorized networks not configured
  # Private cluster not enabled

  node_config {
    machine_type = "n1-standard-8"
    disk_size_gb = 200

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform", # overly broad
    ]

    metadata = {
      disable-legacy-endpoints = "false" # should be true
    }
  }
}

resource "google_sql_database_instance" "main" {
  name             = "sql-prod"
  database_version = "POSTGRES_15"
  region           = "us-central1"

  settings {
    tier = "db-custom-4-16384"

    ip_configuration {
      ipv4_enabled    = true # public IP
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0"
      }
    }

    backup_configuration {
      enabled = false
    }
  }

  deletion_protection = false
}

resource "google_storage_bucket" "data" {
  name     = "my-project-data-bucket"
  location = "US"

  uniform_bucket_level_access = false # ACLs instead of IAM
}

resource "google_compute_firewall" "allow_all" {
  name    = "allow-all-inbound"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  source_ranges = ["0.0.0.0/0"]
}
