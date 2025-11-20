"""
Examples demonstrating the LLM Caller functionality.

This module shows how to use the LLMCaller class for both local and cloud-based LLM calls.
"""

from src.llm import LLMCaller


def example_local_usage():
    """Example using local Ollama models."""
    print("=" * 60)
    print("Example 1: Using Local Models (Ollama)")
    print("=" * 60)
    
    # Initialize with local mode (default)
    llm = LLMCaller(local=True)
    
    # List available local models
    print(f"\nAvailable local models: {llm.list_available_providers()}")
    
    # Make a simple call
    prompt = "What is the capital of France?"
    print(f"\nPrompt: {prompt}")
    
    try:
        response = llm.call(
            prompt=prompt,
            temperature=0.7,
            max_tokens=100
        )
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is installed and running: https://ollama.ai")
    
    print("\n")


def example_cloud_usage():
    """Example using cloud providers (OpenAI, Claude, Gemini)."""
    print("=" * 60)
    print("Example 2: Using Cloud Providers")
    print("=" * 60)
    
    try:
        # Initialize with cloud mode
        llm = LLMCaller(local=False)
        
        # List available cloud providers
        print(f"\nAvailable cloud providers: {llm.list_available_providers()}")
        
        # Make a call with system prompt
        prompt = "Explain quantum computing in one sentence."
        system_prompt = "You are a helpful assistant that provides concise explanations."
        
        print(f"\nSystem Prompt: {system_prompt}")
        print(f"User Prompt: {prompt}")
        
        response = llm.call(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=100
        )
        print(f"Response: {response}")
        
    except RuntimeError as e:
        print(f"Error: {e}")
        print("\nTo use cloud providers:")
        print("1. Copy .env.example to .env")
        print("2. Add at least one API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)")
    
    print("\n")


def example_preferred_provider():
    """Example specifying a preferred cloud provider."""
    print("=" * 60)
    print("Example 3: Using Preferred Cloud Provider")
    print("=" * 60)
    
    try:
        # Initialize with preferred provider
        llm = LLMCaller(local=False, preferred_provider="openai")
        
        prompt = "Write a haiku about coding."
        print(f"\nPrompt: {prompt}")
        
        response = llm.call(
            prompt=prompt,
            temperature=0.9,
            max_tokens=50
        )
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")


def example_switching_modes():
    """Example switching between local and cloud modes."""
    print("=" * 60)
    print("Example 4: Switching Between Local and Cloud Modes")
    print("=" * 60)
    
    # Start with local mode
    llm = LLMCaller(local=True)
    print(f"\nInitial mode: Local")
    print(f"Available: {llm.list_available_providers()}")
    
    try:
        # Switch to cloud mode
        llm.switch_mode(local=False)
        print(f"\nAfter switch: Cloud")
        print(f"Available: {llm.list_available_providers()}")
        
        # Switch back to local
        llm.switch_mode(local=True)
        print(f"\nAfter switch: Local")
        print(f"Available: {llm.list_available_providers()}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")


def example_advanced_options():
    """Example using advanced options and model-specific parameters."""
    print("=" * 60)
    print("Example 5: Advanced Options")
    print("=" * 60)
    
    try:
        # Initialize with cloud mode
        llm = LLMCaller(local=False)
        
        prompt = "Generate three creative names for a tech startup."
        
        print(f"\nPrompt: {prompt}")
        
        # For OpenAI, you can specify the model
        response = llm.call(
            prompt=prompt,
            temperature=0.9,
            max_tokens=150,
            model="gpt-4o-mini"  # Model-specific parameter
        )
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Caller Examples")
    print("=" * 60 + "\n")
    
    # Run examples
    example_local_usage()
    example_cloud_usage()
    example_preferred_provider()
    example_switching_modes()
    example_advanced_options()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)

