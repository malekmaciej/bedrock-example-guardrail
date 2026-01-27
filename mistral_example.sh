#!/bin/bash

################################################################################
# Mistral Example Script - AWS Bedrock with Guardrails
# 
# This script demonstrates how to use the AWS CLI to invoke Mistral Large 3
# model with guardrails for content filtering and safety.
#
# Prerequisites:
#   - AWS CLI installed and configured
#   - Valid AWS credentials with Bedrock permissions
#   - Guardrail deployed (via Terraform or manually)
#   - Access to Mistral models in AWS Bedrock
#
# Usage:
#   ./mistral_example.sh
################################################################################

# Exit on error
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Configuration - can be overridden via environment variables
AWS_REGION="${AWS_REGION:-eu-west-1}"
GUARDRAIL_ID="${GUARDRAIL_ID:-}"
GUARDRAIL_VERSION="${GUARDRAIL_VERSION:-1}"
MODEL_ID="${MODEL_ID:-mistral.mistral-large-3-675b-instruct}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Temporary files for request/response
REQUEST_FILE=$(mktemp /tmp/mistral_request.XXXXXX.json)
RESPONSE_FILE=$(mktemp /tmp/mistral_response.XXXXXX.json)

# Cleanup temporary files on exit
trap "rm -f $REQUEST_FILE $RESPONSE_FILE" EXIT

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo ""
    echo "================================================================================"
    echo "$1"
    echo "================================================================================"
    echo ""
}

print_subheader() {
    echo ""
    echo "--------------------------------------------------------------------------------"
    echo "$1"
    echo "--------------------------------------------------------------------------------"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to invoke the model with guardrails
invoke_mistral_model() {
    local prompt="$1"
    local max_tokens="${2:-2000}"
    local temperature="${3:-0.7}"
    local top_p="${4:-0.9}"
    
    # Create request JSON for Mistral
    cat > "$REQUEST_FILE" <<EOF
{
  "prompt": "$prompt",
  "max_tokens": $max_tokens,
  "temperature": $temperature,
  "top_p": $top_p
}
EOF
    
    # Build AWS CLI command
    local cmd="aws bedrock-runtime invoke-model \
        --region $AWS_REGION \
        --model-id $MODEL_ID \
        --body fileb://$REQUEST_FILE \
        --content-type application/json \
        --accept application/json"
    
    # Add guardrail parameters if configured
    if [ -n "$GUARDRAIL_ID" ]; then
        cmd="$cmd --guardrail-identifier $GUARDRAIL_ID"
        if [ -n "$GUARDRAIL_VERSION" ]; then
            cmd="$cmd --guardrail-version $GUARDRAIL_VERSION"
        fi
    fi
    
    cmd="$cmd $RESPONSE_FILE"
    
    # Execute the command
    if eval $cmd 2>&1 | grep -q "GuardrailIntervened\|ValidationException"; then
        print_error "Request was blocked by guardrails or validation failed"
        if [ -f "$RESPONSE_FILE" ]; then
            cat "$RESPONSE_FILE" | jq -r '.' 2>/dev/null || cat "$RESPONSE_FILE"
        fi
        return 1
    else
        return 0
    fi
}

# Function to extract and display response
display_response() {
    if [ -f "$RESPONSE_FILE" ] && [ -s "$RESPONSE_FILE" ]; then
        # Try to parse with jq, fallback to cat if jq fails
        if command -v jq >/dev/null 2>&1; then
            local response_text=$(cat "$RESPONSE_FILE" | jq -r '.outputs[0].text // .completion // empty' 2>/dev/null)
            if [ -n "$response_text" ] && [ "$response_text" != "null" ]; then
                echo "$response_text"
            else
                # Fallback: try different response structures
                cat "$RESPONSE_FILE" | jq -r '. | if .outputs then .outputs[0].text else if .completion then .completion else . end end' 2>/dev/null || cat "$RESPONSE_FILE"
            fi
        else
            cat "$RESPONSE_FILE"
        fi
    else
        print_error "No response file found or empty response"
    fi
}

# Function to display metadata
display_metadata() {
    if [ -f "$RESPONSE_FILE" ] && [ -s "$RESPONSE_FILE" ] && command -v jq >/dev/null 2>&1; then
        echo ""
        echo "Metadata:"
        local stop_reason=$(cat "$RESPONSE_FILE" | jq -r '.stop_reason // empty' 2>/dev/null)
        [ -n "$stop_reason" ] && echo "  - Stop Reason: $stop_reason"
        echo "  - Model: $MODEL_ID"
        echo "  - Guardrail Applied: $([ -n "$GUARDRAIL_ID" ] && echo "Yes ($GUARDRAIL_ID)" || echo "No")"
    fi
}

################################################################################
# Main Script
################################################################################

print_header "AWS Bedrock with Guardrails - Mistral Example"

# Display configuration
print_info "Configuration:"
print_success "Region: $AWS_REGION"
print_success "Model: $MODEL_ID"

if [ -n "$GUARDRAIL_ID" ]; then
    print_success "Guardrail ID: $GUARDRAIL_ID"
    print_success "Guardrail Version: $GUARDRAIL_VERSION"
else
    print_warning "No guardrail configured. Set GUARDRAIL_ID in .env file"
fi

# Check if jq is installed
if ! command -v jq >/dev/null 2>&1; then
    print_warning "jq is not installed. Install it for better JSON parsing (sudo apt-get install jq)"
fi

# Check if AWS CLI is installed
if ! command -v aws >/dev/null 2>&1; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Verify AWS credentials
if ! aws sts get-caller-identity --region "$AWS_REGION" >/dev/null 2>&1; then
    print_error "AWS credentials not configured or invalid. Run 'aws configure' first."
    exit 1
fi

print_success "AWS credentials validated"

################################################################################
# Example 1: Safe Query
################################################################################

print_subheader "Example 1: Safe Query"

PROMPT1="What is the capital of France?"
print_info "Prompt: $PROMPT1"
echo ""

if invoke_mistral_model "$PROMPT1" 1000 0.7 0.9; then
    print_success "Response:"
    display_response
    display_metadata
else
    print_error "Request failed"
fi

################################################################################
# Example 2: Query with PII (should be blocked/anonymized)
################################################################################

print_subheader "Example 2: Query with PII (should be blocked/anonymized)"

PROMPT2="My email is john.doe@example.com and my phone is 555-1234. Can you help me?"
print_info "Prompt: $PROMPT2"
echo ""

if invoke_mistral_model "$PROMPT2" 1000 0.7 0.9; then
    print_success "Response (PII may be filtered):"
    display_response
    display_metadata
else
    print_error "Request was blocked by guardrails (expected behavior for PII)"
fi

################################################################################
# Example 3: Creative Query
################################################################################

print_subheader "Example 3: Creative Query"

PROMPT3="Write a short poem about technology and innovation."
print_info "Prompt: $PROMPT3"
echo ""

if invoke_mistral_model "$PROMPT3" 1500 0.8 0.95; then
    print_success "Response:"
    display_response
    display_metadata
else
    print_error "Request failed"
fi

################################################################################
# Example 4: Technical Query
################################################################################

print_subheader "Example 4: Technical Query"

PROMPT4="Explain the concept of machine learning in simple terms."
print_info "Prompt: $PROMPT4"
echo ""

if invoke_mistral_model "$PROMPT4" 1000 0.5 0.9; then
    print_success "Response:"
    display_response
    display_metadata
else
    print_error "Request failed"
fi

################################################################################
# Summary
################################################################################

print_header "Examples Completed!"

print_info "Notes:"
echo "  • Mistral Large 3 is a powerful 675B parameter model"
echo "  • Guardrails help ensure safe and appropriate responses"
echo "  • Adjust temperature (0.0-1.0) for more creative or focused responses"
echo "  • Check AWS Bedrock documentation for more model options"

print_success "Script execution completed successfully!"
echo ""
