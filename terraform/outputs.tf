output "guardrail_id" {
  description = "ID of the created Bedrock Guardrail"
  value       = aws_bedrock_guardrail.example_guardrail.guardrail_id
}

output "guardrail_arn" {
  description = "ARN of the created Bedrock Guardrail"
  value       = aws_bedrock_guardrail.example_guardrail.guardrail_arn
}

output "guardrail_version" {
  description = "Version of the Bedrock Guardrail"
  value       = aws_bedrock_guardrail_version.example_version.version
}

output "inference_profile_arn" {
  description = "ARN of the custom inference profile"
  value       = aws_bedrock_custom_model_inference_profile.example_profile.inference_profile_arn
}

output "inference_profile_id" {
  description = "ID of the custom inference profile"
  value       = aws_bedrock_custom_model_inference_profile.example_profile.inference_profile_id
}

output "region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}
