# Bedrock Guardrail
resource "aws_bedrock_guardrail" "example_guardrail" {
  name                      = var.guardrail_name
  description               = "Example guardrail for Bedrock with content filtering"
  blocked_input_messaging   = "Sorry, your input contains inappropriate content."
  blocked_outputs_messaging = "Sorry, I cannot provide that information."

  # Content Policy Configuration
  content_policy_config {
    # Filter for hate speech
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "HATE"
    }

    # Filter for violence
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "VIOLENCE"
    }

    # Filter for sexual content
    filters_config {
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
      type            = "SEXUAL"
    }

    # Filter for insults
    filters_config {
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
      type            = "INSULTS"
    }

    # Filter for misconduct
    filters_config {
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
      type            = "MISCONDUCT"
    }

    # Filter for prompt attacks
    filters_config {
      input_strength  = "HIGH"
      output_strength = "NONE"
      type            = "PROMPT_ATTACK"
    }
  }

  # Topic Policy Configuration - Block certain topics
  topic_policy_config {
    topics_config {
      name       = "Financial Advice"
      definition = "Topics related to investment advice, stock recommendations, or financial planning"
      examples   = ["Should I invest in stocks?", "What stocks should I buy?"]
      type       = "DENY"
    }

    topics_config {
      name       = "Medical Diagnosis"
      definition = "Topics related to diagnosing medical conditions or prescribing treatments"
      examples   = ["Do I have cancer?", "What medication should I take?"]
      type       = "DENY"
    }
  }

  # Sensitive Information Filters
  sensitive_information_policy_config {
    # PII entities to redact
    pii_entities_config {
      action = "BLOCK"
      type   = "EMAIL"
    }

    pii_entities_config {
      action = "BLOCK"
      type   = "PHONE"
    }

    pii_entities_config {
      action = "BLOCK"
      type   = "CREDIT_DEBIT_CARD_NUMBER"
    }

    pii_entities_config {
      action = "ANONYMIZE"
      type   = "NAME"
    }

    pii_entities_config {
      action = "ANONYMIZE"
      type   = "ADDRESS"
    }
  }

  # Word Policy Configuration - Block specific words or phrases
  word_policy_config {
    words_config {
      text = "badword"
    }

    managed_word_lists_config {
      type = "PROFANITY"
    }
  }

  tags = {
    Name        = var.guardrail_name
    Environment = "example"
    ManagedBy   = "Terraform"
  }
}

# Create a version of the guardrail
resource "aws_bedrock_guardrail_version" "example_version" {
  guardrail_arn = aws_bedrock_guardrail.example_guardrail.guardrail_arn
  description   = "Production version of example guardrail"
}

# Custom Inference Profile for eu-west-1 region
resource "aws_bedrock_custom_model_inference_profile" "example_profile" {
  inference_profile_name = var.inference_profile_name
  description            = "Custom inference profile for Sonnet 4.5 in eu-west-1"
  model_source           = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.model_id}"

  tags = {
    Name        = var.inference_profile_name
    Environment = "example"
    ManagedBy   = "Terraform"
  }
}

# IAM Role for Bedrock access (if needed for applications)
resource "aws_iam_role" "bedrock_execution_role" {
  name               = "bedrock-guardrail-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "bedrock-guardrail-execution-role"
    Environment = "example"
    ManagedBy   = "Terraform"
  }
}

# IAM Policy for Bedrock access
resource "aws_iam_role_policy" "bedrock_execution_policy" {
  name = "bedrock-guardrail-execution-policy"
  role = aws_iam_role.bedrock_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ApplyGuardrail"
        ]
        Resource = "*"
      }
    ]
  })
}
