variable "website_bucket_name" {
  type = string
  #  validation {
  #    condition = can(regex(
  #      "^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}.(xn--)?([a-z0-9-]{1,61}|[a-z0-9-]{1,30}.[a-z]{2,})$",
  #    var.website_bucket_name))
  #    error_message = "The website_bucket_name should be a domain name."
  #  }
}

variable "images_bucket_name" {
  type = string
}

variable "region" {
  type    = string
  default = "eu-central-1"
}

variable "table_user" {
  type    = string
  default = "Users"
}

variable "table_links" {
  type    = string
  default = "Link_table"
}

variable "table_registers" {
  type    = string
  default = "Register"
}

# Passed using .env variable to protect maintainer privacy
variable "maintainer_mail" {
  type = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", var.maintainer_mail))
    error_message = "The maintainer_mail should be a mail address."
  }
}

variable "stage_name" {
  type    = string
  default = "dev"
}
