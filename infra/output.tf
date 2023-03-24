output "stage_url" {
  value = aws_api_gateway_deployment.test.invoke_url
}

output "website_url" {
  value = join("", ["http://", aws_s3_bucket.website.website_endpoint])
}

output "register_table" {
  value = aws_dynamodb_table.Register.name
}
