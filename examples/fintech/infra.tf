terraform {
  required_version = ">= 1.0"
  backend "local" {}
}

provider "aws" {
  region = "us-east-1"
}

# Trading database - needs to be fast, but security is missing
resource "aws_db_instance" "trading" {
  engine              = "postgres"
  engine_version      = "15.4"
  instance_class      = "db.r6g.4xlarge"
  allocated_storage   = 1000
  iops                = 10000
  storage_encrypted   = false
  publicly_accessible = true
  multi_az            = false
  skip_final_snapshot = true

  tags = {
    Name = "trading-db"
  }
}

# Audit logs - no encryption, no versioning
resource "aws_s3_bucket" "audit_logs" {
  bucket = "acme-trading-audit-logs"
}

# Customer PII
resource "aws_s3_bucket" "customer_pii" {
  bucket = "acme-trading-customer-data"
}

# ElastiCache for session storage
resource "aws_elasticache_cluster" "sessions" {
  cluster_id           = "trading-sessions"
  engine               = "redis"
  node_type            = "cache.r6g.xlarge"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"

  # No encryption in transit or at rest
}

# Wide open security group
resource "aws_security_group" "trading" {
  name        = "trading-platform"
  description = "Trading platform"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
