variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "eu-west-1"
}

variable "guardrail_name" {
  description = "Name of the Bedrock Guardrail"
  type        = string
  default     = "example-guardrail"
}

variable "inference_profile_name" {
  description = "Name of the custom inference profile"
  type        = string
  default     = "example-sonnet-profile"
}

variable "model_id" {
  description = "Bedrock model ID for Sonnet 4.5"
  type        = string
  default     = "anthropic.claude-sonnet-4-20250514-v1:0"
}
