resource "aws_s3_bucket" "images" {
  bucket = (terraform.workspace == "default") ? var.IMAGES_BUCKET_NAME : "${terraform.workspace}-${var.IMAGES_BUCKET_NAME}"

  tags = merge({
    "Name" = "images"
  }, local.terratag_added_main)

  force_destroy = true
}

data "aws_iam_policy_document" "override" {
  statement {
    sid = "PublicReadForGetBucketObjects"
    principals {
      identifiers = ["AWS"]
      type        = "*"
    }

    actions = ["s3:GetObject"]
    resources = [(terraform.workspace == "default") ? "arn:aws:s3:::${var.WEBSITE_BUCKET_NAME}/*" : "arn:aws:s3:::${terraform.workspace}-${var.WEBSITE_BUCKET_NAME}/*"
    ]
  }
}


# Use https://registry.terraform.io/modules/cloudmaniac/static-website/aws/0.9.2 when we will buy domain name
resource "aws_s3_bucket" "website" {
  bucket = (terraform.workspace == "default") ? var.WEBSITE_BUCKET_NAME : "${terraform.workspace}-${var.WEBSITE_BUCKET_NAME}"
  acl    = "public-read"

  force_destroy = true
  tags = merge({
    "Name" = "Website"
  }, local.terratag_added_main)

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST", "GET"]
    allowed_origins = ["*"]
  }

  policy = data.aws_iam_policy_document.override.json

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_dynamodb_table" "Users" {
  name           = (terraform.workspace == "default") ? var.table_user : "${terraform.workspace}-${var.table_user}"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "UserName"

  point_in_time_recovery {
    enabled = (terraform.workspace == "default") ? true : false
  }

  attribute {
    name = "UserName"
    type = "S"
  }
  tags = local.terratag_added_main
}

resource "aws_dynamodb_table" "Link_table" {
  name           = (terraform.workspace == "default") ? var.table_links : "${terraform.workspace}-${var.table_links}"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "link"

  point_in_time_recovery {
    enabled = (terraform.workspace == "default") ? true : false
  }

  attribute {
    name = "link"
    type = "S"
  }
  tags = local.terratag_added_main
}

resource "aws_dynamodb_table" "Register" {
  name           = (terraform.workspace == "default") ? var.table_registers : "${terraform.workspace}-${var.table_registers}"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "Name"

  point_in_time_recovery {
    enabled = (terraform.workspace == "default") ? true : false
  }

  attribute {
    name = "Name"
    type = "S"
  }
  tags = local.terratag_added_main
}

data "aws_iam_role" "role" {
  name = "website-deployer"
}

data "aws_caller_identity" "current" {}

//Inspire from https://medium.com/craftsmenltd/invoke-aws-lambda-from-aws-step-functions-with-terraform-30b4098d9c1f
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "api/lambda.zip"
  source_dir  = "api/"
}


resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.method.http_method}${aws_api_gateway_resource.resource.path}"
}

resource "aws_lambda_function" "lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = (terraform.workspace == "default") ? "user_registration_consulcam" : "${terraform.workspace}-user_registration_consulcam"
  role             = data.aws_iam_role.role.arn
  handler          = "lambda.register_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.8"
  timeout          = 10

  environment {

    variables = {
      REGION          = var.region
      BUCKET_NAME     = (terraform.workspace == "default") ? var.IMAGES_BUCKET_NAME : "${terraform.workspace}-${var.IMAGES_BUCKET_NAME}"
      USERS_TABLE     = (terraform.workspace == "default") ? var.table_user : "${terraform.workspace}-${var.table_user}"
      LINKS_TABLE     = (terraform.workspace == "default") ? var.table_links : "${terraform.workspace}-${var.table_links}"
      REGISTERS_TABLE = (terraform.workspace == "default") ? var.table_registers : "${terraform.workspace}-${var.table_registers}"
      MAINTAINER_MAIL = var.MAINTAINER_MAIL
      API_KEY         = var.API_KEY
      SENTRY_DNS      = var.SENTRY_DNS
      ENV             = (terraform.workspace == "default") ? "production" : "${terraform.workspace}"
    }
  }

  tags = local.terratag_added_main
}

resource "aws_lambda_function" "scan" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = (terraform.workspace == "default") ? "scan_user_consulcam" : "${terraform.workspace}-scan_user_consulcam"
  role             = data.aws_iam_role.role.arn
  handler          = "lambda.scan_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.8"
  timeout          = 900

  environment {
    variables = {
      REGION          = var.region
      BUCKET_NAME     = (terraform.workspace == "default") ? var.IMAGES_BUCKET_NAME : "${terraform.workspace}-${var.IMAGES_BUCKET_NAME}"
      USERS_TABLE     = (terraform.workspace == "default") ? var.table_user : "${terraform.workspace}-${var.table_user}"
      LINKS_TABLE     = (terraform.workspace == "default") ? var.table_links : "${terraform.workspace}-${var.table_links}"
      REGISTERS_TABLE = (terraform.workspace == "default") ? var.table_registers : "${terraform.workspace}-${var.table_registers}"
      MAINTAINER_MAIL = var.MAINTAINER_MAIL
      API_KEY         = var.API_KEY
      SENTRY_DNS      = var.SENTRY_DNS
      ENV             = (terraform.workspace == "default") ? "production" : "${terraform.workspace}"

    }
  }

  tags = local.terratag_added_main
}

resource "aws_api_gateway_rest_api" "api" {
  name        = (terraform.workspace == "default") ? "user registration" : "${terraform.workspace}-user registration"
  description = "Allow to register user for sending notifications later"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
  tags = local.terratag_added_main
}


resource "aws_api_gateway_resource" "resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "register"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.resource.id
  http_method             = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda.invoke_arn

}

resource "aws_api_gateway_method_response" "method_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.resource.id
  http_method = aws_api_gateway_method.method.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = false,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
  depends_on = [aws_api_gateway_method.method]
}


resource "aws_api_gateway_deployment" "test" {
  depends_on  = [aws_api_gateway_integration.integration]
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = (terraform.workspace == "default") ? var.stage_name : "${terraform.workspace}-${var.stage_name}"
}

locals {

  url = join("/", [aws_api_gateway_deployment.test.invoke_url, aws_api_gateway_resource.resource.path_part])

  index_page = templatefile("templates/index.tmpl", {
    url     = local.url
    contact = var.MAINTAINER_MAIL
  })

  # If your backend is not Terraform Cloud, the value is ${terraform.workspace}
  # otherwise the value retrieved is that of the TFC_WORKSPACE_NAME with trimprefix
  workspace = var.TFC_WORKSPACE_NAME != "" ? trimprefix("${var.TFC_WORKSPACE_NAME}", "mtchoun-mouh-") : "${terraform.workspace}"

}

resource "local_file" "index_page" {
  content  = local.index_page
  filename = "../html/index.html"
}


# Inspired from https://frama.link/GFCHrjEL
module "cors" {
  source  = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.api.id
  api_resource_id = aws_api_gateway_resource.resource.id
}

resource "aws_cloudwatch_event_rule" "scheduler" {
  name                = (terraform.workspace == "default") ? "trigger_user_scan" : "${terraform.workspace}-trigger_user_scan"
  description         = "extract image - verify passport is out - send notifications"
  schedule_expression = "cron(0 8 ? * MON-FRI *)" #https://crontab.guru/#0_8_*_*_1-5
  tags                = local.terratag_added_main
}

resource "aws_cloudwatch_event_target" "target" {
  rule      = aws_cloudwatch_event_rule.scheduler.name
  target_id = "lambda"
  arn       = aws_lambda_function.scan.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scan.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduler.arn
}

locals {
  terratag_added_main = { "environment" = "master", "project" = "mtchoun-mouh" }
}
