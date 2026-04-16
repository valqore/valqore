terraform {
  required_version = ">= 1.0"
  backend "local" {}
}

provider "aws" {
  region = "us-east-1"
}

# Database - publicly accessible, no encryption
resource "aws_db_instance" "store" {
  engine              = "postgres"
  engine_version      = "14.9"
  instance_class      = "db.r5.2xlarge"
  allocated_storage   = 500
  storage_encrypted   = false
  publicly_accessible = true
  skip_final_snapshot = true

  tags = {
    Name = "store-db"
  }
}

# S3 for product images - no versioning, no encryption
resource "aws_s3_bucket" "product_images" {
  bucket = "acme-product-images"
}

# S3 for customer PII exports
resource "aws_s3_bucket" "customer_data" {
  bucket = "acme-customer-exports"
}

# CDN distribution
resource "aws_cloudfront_distribution" "cdn" {
  enabled = true

  origin {
    domain_name = aws_s3_bucket.product_images.bucket_regional_domain_name
    origin_id   = "s3-images"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-images"

    viewer_protocol_policy = "allow-all" # HTTP allowed

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# Wide open security group
resource "aws_security_group" "app" {
  name        = "ecommerce-app"
  description = "App security group"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
