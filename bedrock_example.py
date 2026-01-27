#!/usr/bin/env python3
"""
Example script demonstrating AWS Bedrock usage with Guardrails and custom inference profile.
This script uses Claude Sonnet 4.5 model with guardrails to ensure safe and appropriate responses.
"""

import json
import os
import boto3
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BedrockGuardrailClient:
    """Client for interacting with AWS Bedrock using Guardrails."""
    
    def __init__(
        self,
        region: str = "eu-west-1",
        guardrail_id: Optional[str] = None,
        guardrail_version: Optional[str] = None,
        inference_profile_id: Optional[str] = None
    ):
        """
        Initialize the Bedrock client with guardrails.
        
        Args:
            region: AWS region (default: eu-west-1)
            guardrail_id: ID of the guardrail to use
            guardrail_version: Version of the guardrail
            inference_profile_id: Custom inference profile ID
        """
        self.region = region
        self.guardrail_id = guardrail_id or os.getenv("GUARDRAIL_ID")
        self.guardrail_version = guardrail_version or os.getenv("GUARDRAIL_VERSION", "1")
        self.inference_profile_id = inference_profile_id or os.getenv("INFERENCE_PROFILE_ID")
        
        # Initialize Bedrock Runtime client
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region
        )
        
        # Default model ID for Sonnet 4.5
        self.model_id = "anthropic.claude-sonnet-4-20250514-v1:0"
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """
        Invoke the Bedrock model with guardrails.
        
        Args:
            prompt: The user prompt/question
            max_tokens: Maximum tokens in the response
            temperature: Temperature for response randomness (0-1)
            top_p: Top-p sampling parameter
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Prepare the request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Prepare the API call parameters
        api_params = {
            "modelId": self.inference_profile_id if self.inference_profile_id else self.model_id,
            "body": json.dumps(request_body),
            "contentType": "application/json",
            "accept": "application/json"
        }
        
        # Add guardrail configuration if available
        if self.guardrail_id:
            api_params["guardrailIdentifier"] = self.guardrail_id
            api_params["guardrailVersion"] = self.guardrail_version
        
        try:
            # Invoke the model
            response = self.bedrock_runtime.invoke_model(**api_params)
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the text response
            text_response = response_body.get("content", [{}])[0].get("text", "")
            
            return {
                "success": True,
                "response": text_response,
                "stop_reason": response_body.get("stop_reason"),
                "usage": response_body.get("usage"),
                "model_id": response_body.get("model"),
                "guardrail_applied": self.guardrail_id is not None
            }
            
        except Exception as e:
            error_message = str(e)
            # Check if this is a guardrail intervention
            if "GuardrailIntervened" in error_message or "guardrail" in error_message.lower():
                return {
                    "success": False,
                    "error": "Guardrail intervention",
                    "message": "The request was blocked by guardrails. Please rephrase your question.",
                    "details": error_message
                }
            else:
                return {
                    "success": False,
                    "error": "API error",
                    "message": error_message
                }
    
    def invoke_model_streaming(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ):
        """
        Invoke the Bedrock model with streaming response.
        
        Args:
            prompt: The user prompt/question
            max_tokens: Maximum tokens in the response
            temperature: Temperature for response randomness (0-1)
            top_p: Top-p sampling parameter
            
        Yields:
            Response chunks as they arrive
        """
        # Prepare the request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Prepare the API call parameters
        api_params = {
            "modelId": self.inference_profile_id if self.inference_profile_id else self.model_id,
            "body": json.dumps(request_body),
            "contentType": "application/json",
            "accept": "application/json"
        }
        
        # Add guardrail configuration if available
        if self.guardrail_id:
            api_params["guardrailIdentifier"] = self.guardrail_id
            api_params["guardrailVersion"] = self.guardrail_version
        
        try:
            # Invoke the model with streaming
            response = self.bedrock_runtime.invoke_model_with_response_stream(**api_params)
            
            # Process the stream
            for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                
                if chunk.get("type") == "content_block_delta":
                    delta = chunk.get("delta", {})
                    if delta.get("type") == "text_delta":
                        yield delta.get("text", "")
                        
        except Exception as e:
            error_message = str(e)
            if "GuardrailIntervened" in error_message or "guardrail" in error_message.lower():
                yield "\n[ERROR: Request blocked by guardrails. Please rephrase your question.]\n"
            else:
                yield f"\n[ERROR: {error_message}]\n"


def main():
    """Main function demonstrating usage of the Bedrock Guardrail Client."""
    
    print("=" * 80)
    print("AWS Bedrock with Guardrails - Example Usage")
    print("=" * 80)
    print()
    
    # Initialize the client
    client = BedrockGuardrailClient(
        region="eu-west-1"
    )
    
    # Check if guardrail is configured
    if client.guardrail_id:
        print(f"✓ Guardrail ID: {client.guardrail_id}")
        print(f"✓ Guardrail Version: {client.guardrail_version}")
    else:
        print("⚠ Warning: No guardrail configured. Set GUARDRAIL_ID in .env file")
    
    if client.inference_profile_id:
        print(f"✓ Custom Inference Profile: {client.inference_profile_id}")
    else:
        print(f"✓ Using default model: {client.model_id}")
    
    print()
    print("-" * 80)
    
    # Example 1: Safe query
    print("\nExample 1: Safe Query")
    print("-" * 80)
    prompt1 = "What is the capital of France?"
    print(f"Prompt: {prompt1}")
    print()
    
    result1 = client.invoke_model(prompt1)
    
    if result1["success"]:
        print(f"Response: {result1['response']}")
        print(f"\nMetadata:")
        print(f"  - Stop Reason: {result1['stop_reason']}")
        print(f"  - Guardrail Applied: {result1['guardrail_applied']}")
        if result1.get("usage"):
            print(f"  - Input Tokens: {result1['usage'].get('input_tokens')}")
            print(f"  - Output Tokens: {result1['usage'].get('output_tokens')}")
    else:
        print(f"Error: {result1['message']}")
    
    print()
    print("-" * 80)
    
    # Example 2: Query that might trigger guardrails (PII)
    print("\nExample 2: Query with PII (should be blocked/anonymized)")
    print("-" * 80)
    prompt2 = "My email is john.doe@example.com and my phone is 555-1234. Can you help me?"
    print(f"Prompt: {prompt2}")
    print()
    
    result2 = client.invoke_model(prompt2)
    
    if result2["success"]:
        print(f"Response: {result2['response']}")
    else:
        print(f"Blocked: {result2['message']}")
        if result2.get("details"):
            print(f"Details: {result2['details']}")
    
    print()
    print("-" * 80)
    
    # Example 3: Streaming response
    print("\nExample 3: Streaming Response")
    print("-" * 80)
    prompt3 = "Write a short poem about technology."
    print(f"Prompt: {prompt3}")
    print("\nStreaming Response:")
    print()
    
    for chunk in client.invoke_model_streaming(prompt3):
        print(chunk, end="", flush=True)
    
    print()
    print()
    print("=" * 80)
    print("Examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
