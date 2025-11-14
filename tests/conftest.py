"""
Pytest configuration and shared fixtures.

This file is automatically discovered by pytest and provides
shared fixtures and configuration for all tests.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_config():
    """Provide a sample configuration dictionary."""
    return {
        "task": "sentiment-analysis",
        "text": "This is a test",
        "model_name": "test-model",
        "parameters": {"max_length": 256},
        "verbose": False,
        "output_format": "json"
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    """Create a temporary configuration file."""
    config_file = tmp_path / "test_config.json"
    config_file.write_text(json.dumps(sample_config))
    return config_file


@pytest.fixture
def temp_output_file(tmp_path):
    """Provide a temporary output file path."""
    return tmp_path / "output.json"


@pytest.fixture
def sample_task_result():
    """Provide a sample task result dictionary."""
    return {
        "task": "test-task",
        "status": "success",
        "result": {"value": 42},
        "error_message": None,
        "metadata": {"processing_time": 0.1}
    }


# Pytest hooks for custom behavior
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

