output "elastic_agent_instance_id" {
  description = "ID of the EC2 instance running Elastic Agent for CloudWatch Logs"
  value       = aws_instance.elastic_agent_cloudwatch.id
}

output "elastic_agent_public_ip" {
  description = "Public IP address of the EC2 instance running Elastic Agent for CloudWatch Logs"
  value       = aws_instance.elastic_agent_cloudwatch.public_ip
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket created for logs"
  value       = aws_s3_bucket.log_bucket.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket created for logs"
  value       = aws_s3_bucket.log_bucket.arn
}

output "sqs_queue_url" {
  description = "URL of the SQS queue created for S3 notifications"
  value       = aws_sqs_queue.s3_notifications.id
}

output "lambda_function_name" {
  description = "Name of the Lambda function created for logging"
  value       = aws_lambda_function.log_generator.function_name
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group for Lambda function"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "elastic_agent_cloudwatch_config_example" {
  description = "Example Elastic Agent configuration for AWS CloudWatch logs"
  value       = <<-EOT
    - type: aws-cloudwatch
      log_group_name_prefix: /aws/lambda/${aws_lambda_function.log_generator.function_name}
      scan_frequency: 1m
      region: ${var.aws_region}
  EOT
}