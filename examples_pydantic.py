#!/usr/bin/env python3
"""
Examples demonstrating Pydantic usage in TypeSeed Genesis.

Run this file to see how Pydantic validates data and provides
helpful error messages.
"""

from src.models import CLIConfig, TaskResult
from pydantic import ValidationError
import json


def example_valid_config():
    """Example: Creating a valid configuration."""
    print("=" * 60)
    print("Example 1: Valid Configuration")
    print("=" * 60)
    
    config = CLIConfig(
        task="sentiment-analysis",
        text="I absolutely love this product!",
        model_name="distilbert-base-uncased",
        parameters={"max_length": 512, "batch_size": 32},
        verbose=True,
        output_format="json"
    )
    
    print("✓ Configuration created successfully!")
    print("\nConfiguration as dict:")
    print(json.dumps(config.model_dump(), indent=2))
    print("\n")


def example_minimal_config():
    """Example: Minimal configuration with defaults."""
    print("=" * 60)
    print("Example 2: Minimal Configuration (using defaults)")
    print("=" * 60)
    
    config = CLIConfig(task="text-generation")
    
    print("✓ Configuration created with defaults!")
    print("\nConfiguration:")
    print(json.dumps(config.model_dump(), indent=2))
    print("\n")


def example_task_normalization():
    """Example: Task name normalization."""
    print("=" * 60)
    print("Example 3: Task Name Normalization")
    print("=" * 60)
    
    # Task names are automatically normalized to lowercase and stripped
    config = CLIConfig(task="  SENTIMENT-Analysis  ")
    
    print(f"Original task: '  SENTIMENT-Analysis  '")
    print(f"Normalized task: '{config.task}'")
    print("✓ Task normalized to lowercase and trimmed!")
    print("\n")


def example_invalid_task():
    """Example: Validation error for empty task."""
    print("=" * 60)
    print("Example 4: Validation Error - Empty Task")
    print("=" * 60)
    
    try:
        config = CLIConfig(task="")
    except ValidationError as e:
        print("✗ Validation failed (as expected)!")
        print("\nError details:")
        print(e)
    print("\n")


def example_invalid_output_format():
    """Example: Validation error for invalid output format."""
    print("=" * 60)
    print("Example 5: Validation Error - Invalid Output Format")
    print("=" * 60)
    
    try:
        config = CLIConfig(task="test", output_format="invalid_format")
    except ValidationError as e:
        print("✗ Validation failed (as expected)!")
        print("\nError message:")
        for error in e.errors():
            print(f"  - {error['msg']}")
    print("\n")


def example_task_result_success():
    """Example: Creating a successful task result."""
    print("=" * 60)
    print("Example 6: Task Result - Success")
    print("=" * 60)
    
    result = TaskResult(
        task="sentiment-analysis",
        status="success",
        result={
            "sentiment": "positive",
            "score": 0.95,
            "label": "POSITIVE"
        },
        metadata={
            "processing_time": 0.42,
            "model_version": "1.0.0"
        }
    )
    
    print("✓ Task result created!")
    print("\nResult as JSON:")
    print(result.model_dump_json(indent=2))
    print("\n")


def example_task_result_error():
    """Example: Creating an error task result."""
    print("=" * 60)
    print("Example 7: Task Result - Error")
    print("=" * 60)
    
    result = TaskResult(
        task="text-generation",
        status="error",
        error_message="Model not found",
        metadata={"attempted_model": "gpt-9000"}
    )
    
    print("✓ Error result created!")
    print("\nResult:")
    print(json.dumps(result.model_dump(), indent=2))
    print("\n")


def example_invalid_status():
    """Example: Validation error for invalid status."""
    print("=" * 60)
    print("Example 8: Validation Error - Invalid Status")
    print("=" * 60)
    
    try:
        result = TaskResult(task="test", status="invalid_status")
    except ValidationError as e:
        print("✗ Validation failed (as expected)!")
        print("\nValid statuses are: success, error, pending")
        print(f"Error: {e.errors()[0]['msg']}")
    print("\n")


def example_json_serialization():
    """Example: JSON serialization and deserialization."""
    print("=" * 60)
    print("Example 9: JSON Serialization & Deserialization")
    print("=" * 60)
    
    # Create config
    original = CLIConfig(
        task="translation",
        text="Hello, world!",
        parameters={"source_lang": "en", "target_lang": "es"}
    )
    
    # Serialize to JSON string
    json_str = original.model_dump_json()
    print("Serialized to JSON:")
    print(json_str)
    
    # Deserialize back to object
    data = json.loads(json_str)
    restored = CLIConfig(**data)
    
    print("\n✓ Deserialized back to object!")
    print(f"Task: {restored.task}")
    print(f"Text: {restored.text}")
    print(f"Parameters: {restored.parameters}")
    print("\n")


def example_type_coercion():
    """Example: Automatic type coercion."""
    print("=" * 60)
    print("Example 10: Automatic Type Coercion")
    print("=" * 60)
    
    # Boolean coercion
    config = CLIConfig(
        task="test",
        verbose=1  # Will be coerced to True
    )
    
    print(f"Input verbose: 1 (int)")
    print(f"Stored verbose: {config.verbose} ({type(config.verbose).__name__})")
    print("✓ Automatic type coercion!")
    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "PYDANTIC EXAMPLES - TYPESEED GENESIS" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    examples = [
        example_valid_config,
        example_minimal_config,
        example_task_normalization,
        example_invalid_task,
        example_invalid_output_format,
        example_task_result_success,
        example_task_result_error,
        example_invalid_status,
        example_json_serialization,
        example_type_coercion,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Unexpected error in {example_func.__name__}: {e}")
            print("\n")
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nTip: Check out models.py to see the full model definitions.")
    print("     Check out tests/test_models.py for more usage examples.")
    print("\n")


if __name__ == '__main__':
    main()

