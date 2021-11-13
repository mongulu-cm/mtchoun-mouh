terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.40.0"
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

terraform {
  required_version = ">= 0.15"

  backend "s3" {
    bucket = "terraform-state-mongulu"
    key    = "mtchoun-mouh/terraform.tfstate"
    region = "eu-central-1"
    //encrypt = true
  }
}
