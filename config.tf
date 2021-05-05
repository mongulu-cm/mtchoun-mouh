terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.8.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "terraform-state" {
    bucket = "terraform-state-mongulu"

    lifecycle {
        prevent_destroy = true
    }



    versioning {
        enabled = true
    }

//    server_side_encryption_configuration {
//        rule {
//            apply_server_side_encryption_by_default { aws_s3_bucket.terraform-state aws_dynamodb_table.terraform-locks
//                sse_algorithm = "AES256"
//            }
//        }
//    }
}

resource "aws_dynamodb_table" "terraform-locks" {
    name         = "terraform-locks-mtchoun-mouh"
    billing_mode = "PROVISIONED"
    hash_key     = "LockID"
    read_capacity  = 1
    write_capacity = 1

    attribute {
        name = "LockID"
        type = "S"
    }
}

terraform {
  required_version = ">= 0.13"

  backend "s3" {
    bucket = "terraform-state-mongulu"
    key = "mtchoun-mouh/terraform.tfstate"
    region = "eu-central-1"
    dynamodb_table = "terraform-locks-mtchoun-mouh"
    //encrypt = true
  }
}
