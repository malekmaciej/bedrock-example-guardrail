# Terraform Configuration for AWS Bedrock with Guardrails

This directory contains Terraform configurations for deploying AWS Bedrock infrastructure with Guardrails and custom inference profiles.

## Resources Created

1. **Bedrock Guardrail** (`aws_bedrock_guardrail`)
   - Content filtering for hate, violence, sexual content, etc.
   - Topic blocking for financial advice and medical diagnosis
   - PII protection (emails, phones, credit cards)
   - Word filtering with profanity lists

2. **Guardrail Version** (`aws_bedrock_guardrail_version`)
   - Versioned guardrail for production use

3. **Custom Inference Profile** (`aws_bedrock_custom_model_inference_profile`)
   - Custom profile for Claude Sonnet 4.5 in eu-west-1

4. **IAM Role and Policy** (`aws_iam_role`, `aws_iam_role_policy`)
   - Execution role for Bedrock operations

## Usage

### Initialize Terraform

```bash
terraform init
```

### Plan Changes

```bash
terraform plan
```

### Apply Configuration

```bash
terraform apply
```

### View Outputs

```bash
terraform output
terraform output -json
```

### Destroy Resources

```bash
terraform destroy
```

## Configuration Files

- `main.tf` - Provider and Terraform configuration
- `variables.tf` - Input variables with defaults
- `outputs.tf` - Output values (IDs, ARNs)
- `bedrock.tf` - Bedrock resources definition

## Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region for deployment | `eu-west-1` | No |
| `guardrail_name` | Name of the guardrail | `example-guardrail` | No |
| `inference_profile_name` | Name of inference profile | `example-sonnet-profile` | No |
| `model_id` | Bedrock model ID | `anthropic.claude-sonnet-4-20250514-v1:0` | No |

## Outputs

| Output | Description |
|--------|-------------|
| `guardrail_id` | ID of the created guardrail |
| `guardrail_arn` | ARN of the guardrail |
| `guardrail_version` | Version number of the guardrail |
| `inference_profile_arn` | ARN of the custom inference profile |
| `inference_profile_id` | ID of the custom inference profile |
| `region` | Deployment region |

## Customization

### Modify Guardrail Filters

Edit `bedrock.tf` to change filter strengths or add new filters:

```hcl
filters_config {
  input_strength  = "HIGH"    # Options: HIGH, MEDIUM, LOW, NONE
  output_strength = "HIGH"
  type            = "HATE"
}
```

### Add Custom Topics

Add new topic blocks to `topic_policy_config`:

```hcl
topics_config {
  name       = "Legal Advice"
  definition = "Topics related to legal advice or interpretation"
  examples   = ["Should I sue?", "What are my legal rights?"]
  type       = "DENY"
}
```

### Modify PII Handling

Change how PII is handled:

```hcl
pii_entities_config {
  action = "BLOCK"      # Options: BLOCK, ANONYMIZE
  type   = "EMAIL"
}
```

## Prerequisites

- AWS CLI configured with valid credentials
- Terraform >= 1.0
- AWS account with Bedrock access
- Permissions for:
  - bedrock:*
  - iam:CreateRole
  - iam:CreatePolicy
  - iam:AttachRolePolicy

## State Management

For production use, configure remote state:

```hcl
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "bedrock-guardrail/terraform.tfstate"
    region = "eu-west-1"
  }
}
```

## Security Considerations

1. Never commit `terraform.tfstate` - contains sensitive information
2. Use `.gitignore` to exclude state files
3. Use remote state with encryption for production
4. Regularly rotate AWS credentials
5. Apply least-privilege IAM policies

## Troubleshooting

**Error: "Access Denied"**
```bash
# Check your AWS credentials
aws sts get-caller-identity

# Verify region
aws configure get region
```

**Error: "Resource already exists"**
```bash
# Import existing resource
terraform import aws_bedrock_guardrail.example_guardrail <guardrail-id>
```

**Error: "Model not available"**
- Ensure Bedrock model access is granted in AWS Console
- Go to: Bedrock → Model Access → Manage Access

## Version Requirements

```hcl
terraform >= 1.0
aws provider ~> 5.0
```

## Additional Resources

- [Terraform AWS Provider - Bedrock Resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/bedrock_guardrail)
- [AWS Bedrock Guardrails Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
