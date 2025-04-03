variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-northeast-1"
}

variable "aws_profile" {
  description = "AWS profile to use for credentials"
  type        = string
  default     = "elastic-sa"
}

variable "prefix" {
  description = "Prefix to be used for all resources"
  type        = string
  default     = "elastic"
}

variable "ec2_instance_type" {
  description = "EC2 instance type for Elastic Agent"
  type        = string
  default     = "t3.medium"
}

variable "ec2_ami_id" {
  description = "AMI ID for EC2 instances"
  type        = string
  default     = "ami-0599b6e53ca798bb2"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

# Tags
variable "tag_division" {
  description = "Division tag for resources"
  type        = string
  default     = "platform"
}

variable "tag_org" {
  description = "Organization tag for resources"
  type        = string
  default     = "engineering"
}

variable "tag_team" {
  description = "Team tag for resources"
  type        = string
  default     = "observability"
}

variable "tag_project" {
  description = "Project tag for resources"
  type        = string
  default     = "elastic-monitoring"
}

variable "keep_until_date" {
  description = "Keep until date tag for resources"
  type        = string
  default     = "2025-12-31"
}

# S3 and SQS settings
variable "s3_bucket_prefix" {
  description = "Prefix for S3 bucket name"
  type        = string
  default     = "logs"
}

variable "sqs_queue_name" {
  description = "Name of SQS queue for S3 notifications"
  type        = string
  default     = "s3-notifications"
}

variable "lambda_log_level" {
  description = "Log level for Lambda function"
  type        = string
  default     = "INFO"
}

variable "default_tags" {
  description = "AWS default tags for resources"
  type        = map(string)
  default     = {}
}