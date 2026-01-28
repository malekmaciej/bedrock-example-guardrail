#!/usr/bin/env python3
"""
Mistral Example Script - AWS Bedrock with Guardrails

This script demonstrates how to use AWS Bedrock to invoke Mistral Large 3
model with guardrails for content filtering and safety.

Prerequisites:
  - AWS CLI installed and configured
  - Valid AWS credentials with Bedrock permissions
  - Guardrail deployed (via Terraform or manually)
  - Access to Mistral models in AWS Bedrock

Usage:
  python mistral_example.py
"""

import json
import os
import sys
import boto3
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ANSI color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header(text: str) -> None:
    """Print a header with formatting."""
    print()
    print("=" * 80)
    print(text)
    print("=" * 80)
    print()


def print_subheader(text: str) -> None:
    """Print a subheader with formatting."""
    print()
    print("-" * 80)
    print(text)
    print("-" * 80)


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {text}")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.NC} {text}")


class MistralBedrockClient:
    """Client for interacting with Mistral models on AWS Bedrock using Guardrails."""
    
    def __init__(
        self,
        region: str = "eu-west-1",
        guardrail_id: Optional[str] = None,
        guardrail_version: Optional[str] = None,
        model_id: str = "mistral.mistral-large-3-675b-instruct"
    ):
        """
        Initialize the Mistral Bedrock client with guardrails.
        
        Args:
            region: AWS region (default: eu-west-1)
            guardrail_id: ID of the guardrail to use
            guardrail_version: Version of the guardrail
            model_id: Model ID for Mistral
        """
        self.region = region
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
        self.model_id = model_id
        
        # Initialize Bedrock Runtime client
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region
        )
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """
        Invoke the Mistral model with guardrails.
        
        Args:
            prompt: The user prompt/question
            max_tokens: Maximum tokens in the response
            temperature: Temperature for response randomness (0-1)
            top_p: Top-p sampling parameter
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Validate numeric parameters
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            return {
                "success": False,
                "error": "max_tokens must be a positive integer"
            }
        
        # Prepare the request body for Mistral
        request_body = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        # Prepare the API call parameters
        api_params = {
            "modelId": self.model_id,
            "body": json.dumps(request_body),
            "contentType": "application/json",
            "accept": "application/json"
        }
        
        # Add guardrail configuration if available
        if self.guardrail_id:
            api_params["guardrailIdentifier"] = self.guardrail_id
            if self.guardrail_version:
                api_params["guardrailVersion"] = self.guardrail_version
        
        try:
            # Invoke the model
            response = self.bedrock_runtime.invoke_model(**api_params)
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the text response - try multiple possible response structures
            text_response = ""
            if "outputs" in response_body and len(response_body["outputs"]) > 0:
                text_response = response_body["outputs"][0].get("text", "")
            elif "completion" in response_body:
                text_response = response_body.get("completion", "")
            
            return {
                "success": True,
                "response": text_response,
                "stop_reason": response_body.get("stop_reason"),
                "model_id": self.model_id,
                "guardrail_applied": self.guardrail_id is not None,
                "raw_response": response_body
            }
            
        except Exception as e:
            error_message = str(e)
            # Check if this is a guardrail intervention or validation error
            if "GuardrailIntervened" in error_message or "ValidationException" in error_message:
                return {
                    "success": False,
                    "error": "Guardrail intervention or validation failed",
                    "message": "The request was blocked by guardrails or validation failed.",
                    "details": error_message
                }
            else:
                return {
                    "success": False,
                    "error": "API error",
                    "message": f"AWS CLI command failed: {error_message}",
                    "details": error_message
                }
    
    def display_response(self, result: Dict[str, Any]) -> None:
        """Display the response from the model."""
        if result.get("success") and result.get("response"):
            print(result["response"])
        elif not result.get("success"):
            print_error(f"No response or error occurred")
    
    def display_metadata(self, result: Dict[str, Any]) -> None:
        """Display metadata about the response."""
        if result.get("success"):
            print()
            print("Metadata:")
            if result.get("stop_reason"):
                print(f"  - Stop Reason: {result['stop_reason']}")
            print(f"  - Model: {result['model_id']}")
            guardrail_status = "Yes" if result.get("guardrail_applied") else "No"
            if result.get("guardrail_applied") and self.guardrail_id:
                guardrail_status = f"Yes ({self.guardrail_id})"
            print(f"  - Guardrail Applied: {guardrail_status}")


def check_aws_credentials(region: str) -> bool:
    """Check if AWS credentials are properly configured."""
    try:
        sts = boto3.client('sts', region_name=region)
        sts.get_caller_identity()
        return True
    except Exception:
        return False


def main():
    """Main function demonstrating usage of the Mistral Bedrock Client."""
    
    # Configuration - can be overridden via environment variables
    aws_region = os.getenv("AWS_REGION", "eu-west-1")
    guardrail_id = os.getenv("GUARDRAIL_ID")
    guardrail_version = os.getenv("GUARDRAIL_VERSION", "1")
    model_id = os.getenv("MODEL_ID", "mistral.mistral-large-3-675b-instruct")
    
    print_header("AWS Bedrock with Guardrails - Mistral Example")
    
    # Display configuration
    print_info("Configuration:")
    print_success(f"Region: {aws_region}")
    print_success(f"Model: {model_id}")
    
    if guardrail_id:
        print_success(f"Guardrail ID: {guardrail_id}")
        print_success(f"Guardrail Version: {guardrail_version}")
    else:
        print_warning("No guardrail configured. Set GUARDRAIL_ID in .env file")
    
    # Check if AWS credentials are valid
    if not check_aws_credentials(aws_region):
        print_error("AWS credentials not configured or invalid. Run 'aws configure' first.")
        sys.exit(1)
    
    print_success("AWS credentials validated")
    
    # Initialize the client
    client = MistralBedrockClient(
        region=aws_region,
        guardrail_id=guardrail_id,
        guardrail_version=guardrail_version,
        model_id=model_id
    )
    
    # -------------------------------------------------------------------------
    # Example 1: Safe Query
    # -------------------------------------------------------------------------
    print_subheader("Example 1: Safe Query")
    
    prompt1 = "What is the capital of France?"
    print_info(f"Prompt: {prompt1}")
    print()
    
    result1 = client.invoke_model(prompt1, max_tokens=1000, temperature=0.7, top_p=0.9)
    
    if result1["success"]:
        print_success("Response:")
        client.display_response(result1)
        client.display_metadata(result1)
    else:
        print_error("Request failed")
    
    # -------------------------------------------------------------------------
    # Example 2: Query with PII (should be blocked/anonymized)
    # -------------------------------------------------------------------------
    print_subheader("Example 2: Query with PII (should be blocked/anonymized)")
    
    prompt2 = "My email is john.doe@example.com and my phone is (555) 123-4567. Can you help me?"
    print_info(f"Prompt: {prompt2}")
    print()
    
    result2 = client.invoke_model(prompt2, max_tokens=1000, temperature=0.7, top_p=0.9)
    
    if result2["success"]:
        print_success("Response (PII may be filtered):")
        client.display_response(result2)
        client.display_metadata(result2)
    else:
        print_error("Request was blocked by guardrails (expected behavior for PII)")
    
    # -------------------------------------------------------------------------
    # Example 3: Creative Query
    # -------------------------------------------------------------------------
    print_subheader("Example 3: Creative Query")
    
    prompt3 = "Write a short poem about technology and innovation."
    print_info(f"Prompt: {prompt3}")
    print()
    
    result3 = client.invoke_model(prompt3, max_tokens=1500, temperature=0.8, top_p=0.95)
    
    if result3["success"]:
        print_success("Response:")
        client.display_response(result3)
        client.display_metadata(result3)
    else:
        print_error("Request failed")
    
    # -------------------------------------------------------------------------
    # Example 4: Technical Query
    # -------------------------------------------------------------------------
    print_subheader("Example 4: Technical Query")
    
    prompt4 = "Explain the concept of machine learning in simple terms."
    print_info(f"Prompt: {prompt4}")
    print()
    
    result4 = client.invoke_model(prompt4, max_tokens=1000, temperature=0.5, top_p=0.9)
    
    if result4["success"]:
        print_success("Response:")
        client.display_response(result4)
        client.display_metadata(result4)
    else:
        print_error("Request failed")
    
    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print_header("Examples Completed!")
    
    print_info("Notes:")
    print("  • Mistral Large 3 is a powerful 675B parameter model")
    print("  • Guardrails help ensure safe and appropriate responses")
    print("  • Adjust temperature (0.0-1.0) for more creative or focused responses")
    print("  • Check AWS Bedrock documentation for more model options")
    print()
    print_success("Script execution completed successfully!")
    print()


if __name__ == "__main__":
    main()
