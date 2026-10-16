# DELIBERATELY INSECURE fixture — intended to FAIL Checkov and block deployment.
# Never apply this configuration. Used only for policy-gate demos.
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  access_key                  = "mock"
  secret_key                  = "mock"
}

# CKV_AWS_18 / CKV_AWS_19 / CKV_AWS_21 / CKV2_AWS_6 style findings:
# public ACL, no encryption, no versioning, no public access block.
resource "aws_s3_bucket" "public_data" {
  bucket = "agentthree-devsecops-INSECURE-public"
  acl    = "public-read"
}

resource "aws_security_group" "wide_open" {
  name        = "agentthree-insecure-wide-open"
  description = "Deliberately open SG for Checkov demo — DO NOT APPLY"

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
