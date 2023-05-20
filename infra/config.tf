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

terraform {
  required_version = ">= 0.15"

  backend "remote" {
    hostname = "app.terraform.io"
    organization = "tfc-mongulu-cm"

    workspaces {

       prefix = "mtchoun-mouh-"
       //tags = ["mtchoun-mouh", "aws"]

    }
  }

  //backend "s3" {
    //bucket = "terraform-state-mongulu"
    //key    = "mtchoun-mouh/terraform.tfstate"
    //region = "eu-central-1"
    //encrypt = true
  //}
}
