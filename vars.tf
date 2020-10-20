variable "website_bucket_name" {
  type = string
}

variable "redirect_bucket_name" {
  type = string
}

variable "images_bucket_name" {
  type = string
}

variable "region" {
  type = string
  default = "eu-central-1"
}

variable "table_user" {
  type = string
  default = "Users"
}

variable "table_links" {
  type = string
  default = "Link_table"
}

variable "table_registers" {
  type = string
  default = "Register"
}

# Passed using .env variable to protect maintainer privacy
variable "maintainer_mail" {
  type = string
}

variable "contact_url" {
  type = string
}

variable "stage_name" {
  type = string
  default = "dev"
}