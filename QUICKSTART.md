# Quick Start Guide

This is a quick reference for getting started with this Bedrock Guardrails example.

## 🚀 Quick Start (5 minutes)

### Step 1: Deploy Infrastructure (2 min)
```bash
cd terraform
terraform init
terraform apply -auto-approve
```

Save the outputs - you'll need them!

### Step 2: Configure Python (2 min)
```bash
cd ..
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with Terraform outputs:
- Set `GUARDRAIL_ID`
- Set `GUARDRAIL_VERSION`
- Set `INFERENCE_PROFILE_ID`

### Step 3: Run Example (1 min)
```bash
python bedrock_example.py
```

## 📋 Prerequisites Checklist

Before you start, make sure you have:

- [ ] AWS Account with admin or appropriate IAM permissions
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Terraform >= 1.0 installed
- [ ] Python >= 3.8 installed
- [ ] **Bedrock Model Access Granted** (see below)

### Grant Bedrock Model Access

**This is crucial!** You must request access to Claude Sonnet 4.5:

1. Log into AWS Console
2. Navigate to: **Amazon Bedrock** → **Model Access**
3. Click **"Manage model access"** or **"Request model access"**
4. Find and check: **Claude 3.5 Sonnet** (Anthropic)
5. Click **"Request model access"** or **"Save changes"**
6. Wait for approval (usually instant, can take a few minutes)

## 🎯 What This Example Does

### Guardrail Features Demonstrated

✅ **Content Filtering**: Blocks inappropriate content (hate, violence, etc.)
✅ **Topic Blocking**: Prevents financial/medical advice
✅ **PII Protection**: Anonymizes/blocks sensitive information
✅ **Word Filtering**: Blocks profanity and custom words
✅ **Streaming Responses**: Real-time token generation

### Example Scenarios

The script demonstrates:
1. Safe query (normal response)
2. PII detection (blocked/anonymized)
3. Streaming response (token-by-token output)

## 🔧 Troubleshooting

### "Access Denied" Error
→ Grant Bedrock model access (see above)
→ Check AWS credentials: `aws sts get-caller-identity`

### "Model Not Found"
→ Verify you requested access to Claude Sonnet 4.5
→ Check region is eu-west-1

### "Guardrail Not Found"
→ Run `terraform output` and verify IDs in `.env`
→ Ensure Terraform apply succeeded

### Terraform Errors
→ Check AWS credentials
→ Ensure you have IAM permissions for Bedrock and IAM role creation

## 💰 Cost Estimate

**First 1000 queries (approximately):**
- Bedrock API: ~$0.15 (varies by token count)
- Guardrails: ~$0.05 (additional per-token charge)
- Total: **~$0.20** for testing

**Note**: No infrastructure costs (no EC2, no persistent resources)

## 🧹 Cleanup

When finished testing:

```bash
cd terraform
terraform destroy -auto-approve
```

This removes all AWS resources and stops charges.

## 📚 Next Steps

1. **Customize Guardrails**: Edit `terraform/bedrock.tf`
   - Adjust filter strengths (HIGH/MEDIUM/LOW)
   - Add custom topics to block
   - Modify PII handling rules

2. **Integrate into Your App**: Use `BedrockGuardrailClient` class
   ```python
   from bedrock_example import BedrockGuardrailClient
   client = BedrockGuardrailClient(...)
   result = client.invoke_model("Your prompt here")
   ```

3. **Advanced Usage**: Check main README.md for:
   - Custom parameters (temperature, max_tokens, etc.)
   - Error handling strategies
   - Production best practices

## 📞 Getting Help

- **AWS Documentation**: https://docs.aws.amazon.com/bedrock/
- **Issues**: Open an issue in this repository
- **AWS Support**: For account-specific questions

---

**Ready to start?** Jump to Step 1 above! 🎉
