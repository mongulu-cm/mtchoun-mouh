output "stage_url" {
  value = aws_api_gateway_deployment.test.invoke_url
}

output "website_url" {
  value = join("", ["http://", "${terraform.workspace}", "-mtchoun-mouh.mongulu.cm.s3-website.eu-central-1.amazonaws.com"])
}
