terraform {
  required_version = ">= 1.5"

  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t4g.medium" # Graviton (ARM) for cost + carbon savings

  root_block_device {
    volume_size = 50
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required" # IMDSv2
  }

  tags = {
    Name        = "web-server"
    team        = "platform"
    cost-center = "engineering"
    environment = "production"
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "mycompany-app-data"

  tags = {
    team        = "platform"
    cost-center = "engineering"
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow HTTPS inbound only"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "HTTPS from internal network"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  tags = {
    team = "platform"
  }
}

resource "aws_db_instance" "main" {
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.r6g.large" # Graviton
  allocated_storage    = 100
  storage_encrypted    = true
  publicly_accessible  = false
  multi_az             = true
  skip_final_snapshot  = false
  deletion_protection  = true

  db_subnet_group_name   = "private-subnets"
  vpc_security_group_ids = [aws_security_group.web.id]

  tags = {
    team        = "platform"
    cost-center = "engineering"
    environment = "production"
  }
}
