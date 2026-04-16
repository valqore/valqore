terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket = "mycompany-tf-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_eks_cluster" "main" {
  name     = "prod-cluster"
  role_arn = "arn:aws:iam::123456789:role/eks-role"

  vpc_config {
    subnet_ids              = ["subnet-abc", "subnet-def"]
    endpoint_public_access  = true
    endpoint_private_access = false
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  tags = {
    Name = "prod-cluster"
  }
}

resource "aws_db_instance" "app" {
  engine              = "postgres"
  engine_version      = "14.9"
  instance_class      = "db.r5.xlarge"
  allocated_storage   = 200
  storage_encrypted   = false
  publicly_accessible = true
  multi_az            = false
  skip_final_snapshot = true

  tags = {
    Name = "app-database"
  }
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "app-cache"
  engine               = "redis"
  node_type            = "cache.r5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
}

resource "aws_s3_bucket" "uploads" {
  bucket = "mycompany-user-uploads"
}

resource "aws_s3_bucket" "backups" {
  bucket = "mycompany-db-backups"
}

resource "aws_security_group" "app" {
  name = "app-sg"

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

resource "aws_iam_user" "deploy" {
  name = "deploy-user"
}

resource "aws_iam_user_policy" "deploy" {
  name = "deploy-admin"
  user = aws_iam_user.deploy.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}
