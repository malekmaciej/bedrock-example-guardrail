# AWS Bedrock with Guardrails - Example Repository

This repository demonstrates how to use Amazon Bedrock with Guardrails, featuring:
- **Claude Sonnet 4.5** model integration (Python example)
- **Mistral Large 3** model integration (Bash/AWS CLI example)
- **Guardrails** for content filtering and safety
- **Custom Inference Profile** for the eu-west-1 region
- **Infrastructure as Code** using Terraform
- **Python SDK** and **AWS CLI** implementation with examples

## Features

### Guardrail Capabilities
- **Content Filtering**: Hate speech, violence, sexual content, insults, misconduct, and prompt attacks
- **Topic Blocking**: Financial advice and medical diagnosis topics
- **PII Protection**: Blocks/anonymizes emails, phone numbers, credit cards, names, and addresses
- **Word Filtering**: Custom word lists and profanity filtering

### Custom Inference Profile
- Dedicated inference profile for eu-west-1 region
- Optimized for Claude Sonnet 4.5 model
- Consistent performance and routing

## Prerequisites

Before you begin, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Terraform** >= 1.0 installed
4. **Python** >= 3.8 installed
5. **Bedrock Model Access**: Request access to Claude Sonnet 4.5 in AWS Console

### Required AWS Permissions

Your AWS credentials need permissions for:
- `bedrock:*` - Bedrock service operations
- `iam:CreateRole`, `iam:AttachRolePolicy` - IAM role creation
- `ec2:DescribeRegions` - Region validation

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/malekmaciej/bedrock-example-guardrail.git
cd bedrock-example-guardrail
```

### 2. Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the planned changes
terraform plan

# Apply the configuration
terraform apply
```

After deployment, Terraform will output important values:
- `guardrail_id` - Use this in your Python code
- `guardrail_version` - Version of the guardrail
- `inference_profile_id` - Custom profile ARN
- `region` - Deployment region

### 3. Configure Python Environment

```bash
# Return to repository root
cd ..

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
```

Edit `.env` and add the values from Terraform outputs:
```bash
GUARDRAIL_ID=<guardrail_id from terraform output>
GUARDRAIL_VERSION=<guardrail_version from terraform output>
INFERENCE_PROFILE_ID=<inference_profile_id from terraform output>
```

### 4. Run the Examples

**Python Example (Claude Sonnet 4.5):**
```bash
python bedrock_example.py
```

**Bash Example (Mistral Large 3):**
```bash
./mistral_example.sh
```

## Project Structure

```
.
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── bedrock_example.py       # Python example with Claude Sonnet 4.5
├── mistral_example.sh       # Bash script example with Mistral Large 3
└── terraform/               # Terraform configuration
    ├── main.tf              # Provider configuration
    ├── variables.tf         # Input variables
    ├── outputs.tf           # Output values
    └── bedrock.tf           # Bedrock resources
```

## Python Usage Examples

### Basic Usage

```python
from bedrock_example import BedrockGuardrailClient

# Initialize client
client = BedrockGuardrailClient(
    region="eu-west-1",
    guardrail_id="your-guardrail-id",
    guardrail_version="1"
)

# Make a request
result = client.invoke_model("What is machine learning?")

if result["success"]:
    print(result["response"])
else:
    print(f"Error: {result['message']}")
```

### Streaming Response

```python
# Get streaming response
for chunk in client.invoke_model_streaming("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Custom Parameters

```python
result = client.invoke_model(
    prompt="Explain quantum computing",
    max_tokens=1000,
    temperature=0.5,
    top_p=0.9
)
```

## Mistral Model Example (Bash Script)

In addition to the Python example using Claude Sonnet 4.5, this repository includes a Bash script that demonstrates using the **Mistral Large 3** model (675B parameters) with AWS CLI.

### Running the Mistral Example

```bash
# Make sure AWS CLI is installed and configured
aws --version

# Optional: Install jq for better JSON parsing
sudo apt-get install jq  # On Ubuntu/Debian
# or
brew install jq          # On macOS

# Run the script
./mistral_example.sh
```

### What the Script Demonstrates

The `mistral_example.sh` script shows how to:
- Use AWS CLI to invoke Mistral Large 3 model with guardrails
- Handle different types of queries (safe, PII-containing, creative, technical)
- Parse and display responses from the Bedrock API
- Configure model parameters (temperature, max_tokens, top_p)
- Apply guardrails for content filtering and safety

### Script Features

- **Color-coded output** for better readability
- **Multiple examples** showcasing different query types
- **Error handling** for guardrail interventions
- **Automatic cleanup** of temporary files
- **Environment variable support** from .env file
- **Metadata display** showing model and guardrail information

### Key Differences from Python Example

| Feature | Python (bedrock_example.py) | Bash (mistral_example.sh) |
|---------|----------------------------|---------------------------|
| Model | Claude Sonnet 4.5 | Mistral Large 3 |
| Language | Python 3 with boto3 | Bash with AWS CLI |
| API Format | Messages API | Prompt/Completion API |
| Streaming | Supported | Not included |
| Dependencies | boto3, python-dotenv | AWS CLI, jq (optional) |

## Terraform Configuration

### Variables

Customize your deployment by modifying `terraform/variables.tf` or using a `terraform.tfvars` file:

```hcl
aws_region             = "eu-west-1"
guardrail_name         = "my-custom-guardrail"
inference_profile_name = "my-sonnet-profile"
```

### Outputs

After deployment, retrieve outputs:

```bash
terraform output guardrail_id
terraform output inference_profile_id
```

### Modifying Guardrail Rules

Edit `terraform/bedrock.tf` to customize:
- Content filter strengths (HIGH, MEDIUM, LOW, NONE)
- Blocked topics and definitions
- PII handling (BLOCK, ANONYMIZE)
- Custom word lists

Then reapply:
```bash
terraform apply
```

## Guardrail Examples

### Content That Will Be Blocked

- Hate speech or discriminatory content
- Violent or graphic content
- Requests for financial advice
- Medical diagnosis requests
- Personal information (emails, phone numbers, credit cards)
- Profanity and custom blocked words

### Safe Queries

- General knowledge questions
- Creative writing requests
- Technical explanations
- Data analysis assistance
- Code generation

## Troubleshooting

### Common Issues

**Issue**: "Access denied" errors
- **Solution**: Ensure you have requested Bedrock model access in AWS Console
- Go to: AWS Console → Bedrock → Model Access → Request Access

**Issue**: "Guardrail not found"
- **Solution**: Verify the `GUARDRAIL_ID` in `.env` matches Terraform output
- Check the guardrail exists: `aws bedrock list-guardrails --region eu-west-1`

**Issue**: "Model not found" or "Inference profile not found"
- **Solution**: Ensure resources are created in the correct region (eu-west-1)
- Verify model access is granted for Sonnet 4.5

**Issue**: Terraform apply fails
- **Solution**: Check AWS credentials: `aws sts get-caller-identity`
- Ensure proper IAM permissions
- Verify region availability for Bedrock

### Enable Debug Logging

For more detailed logs in Python:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Cost Considerations

- **Bedrock**: Charged per 1,000 input/output tokens
- **Guardrails**: Additional per-request and per-token charges
- **Inference Profiles**: No additional cost
- See [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) for details

## Cleanup

To avoid ongoing charges, destroy the infrastructure when done:

```bash
cd terraform
terraform destroy
```

This will remove:
- Bedrock Guardrail and version
- Custom Inference Profile
- IAM roles and policies

## Security Best Practices

1. **Never commit** `.env` file with actual credentials
2. **Use IAM roles** instead of long-term credentials when possible
3. **Enable AWS CloudTrail** for API call auditing
4. **Regularly update** guardrail rules based on use cases
5. **Monitor costs** using AWS Cost Explorer
6. **Review logs** for blocked content and adjust filters as needed

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Bedrock Guardrails Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Anthropic Claude Documentation](https://docs.anthropic.com/claude/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for educational and example purposes.

## Support

For issues and questions:
- Open an issue in this repository
- Check AWS Bedrock documentation
- Review AWS Support resources