"""
Unit tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError
import sys
from pathlib import Path

# Add parent directory to path to import models
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.models import CLIConfig, TaskResult


class TestCLIConfig:
    """Test suite for CLIConfig Pydantic model."""
    
    def test_valid_config_minimal(self):
        """Test creating config with minimal required fields."""
        config = CLIConfig(task="test-task")
        assert config.task == "test-task"
        assert config.text is None
        assert config.model_name == "default"
        assert config.parameters == {}
        assert config.verbose is False
        assert config.output_format == "json"
    
    def test_valid_config_full(self):
        """Test creating config with all fields."""
        config = CLIConfig(
            task="sentiment-analysis",
            text="Hello world",
            model_name="bert-base",
            parameters={"max_length": 512, "batch_size": 32},
            verbose=True,
            output_format="csv"
        )
        assert config.task == "sentiment-analysis"
        assert config.text == "Hello world"
        assert config.model_name == "bert-base"
        assert config.parameters["max_length"] == 512
        assert config.verbose is True
        assert config.output_format == "csv"
    
    def test_task_validation_empty(self):
        """Test that empty task raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CLIConfig(task="")
        assert "Task cannot be empty" in str(exc_info.value)
    
    def test_task_validation_whitespace(self):
        """Test that whitespace-only task raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CLIConfig(task="   ")
        assert "Task cannot be empty" in str(exc_info.value)
    
    def test_task_normalization(self):
        """Test that task is normalized to lowercase and stripped."""
        config = CLIConfig(task="  TEST-Task  ")
        assert config.task == "test-task"
    
    def test_invalid_output_format(self):
        """Test that invalid output format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            CLIConfig(task="test", output_format="invalid")
        assert "Output format must be one of" in str(exc_info.value)
    
    def test_valid_output_formats(self):
        """Test all valid output formats."""
        for fmt in ["json", "csv", "txt", "xml"]:
            config = CLIConfig(task="test", output_format=fmt)
            assert config.output_format == fmt
    
    def test_json_serialization(self):
        """Test that config can be serialized to JSON."""
        config = CLIConfig(
            task="test",
            text="hello",
            parameters={"key": "value"}
        )
        json_data = config.model_dump_json()
        assert isinstance(json_data, str)
        assert "test" in json_data
    
    def test_dict_conversion(self):
        """Test that config can be converted to dict."""
        config = CLIConfig(task="test", verbose=True)
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["task"] == "test"
        assert config_dict["verbose"] is True


class TestTaskResult:
    """Test suite for TaskResult Pydantic model."""
    
    def test_valid_result_success(self):
        """Test creating successful task result."""
        result = TaskResult(
            task="test",
            status="success",
            result={"output": "test data"},
            metadata={"time": 1.5}
        )
        assert result.task == "test"
        assert result.status == "success"
        assert result.result["output"] == "test data"
        assert result.error_message is None
    
    def test_valid_result_error(self):
        """Test creating error task result."""
        result = TaskResult(
            task="test",
            status="error",
            error_message="Something went wrong"
        )
        assert result.status == "error"
        assert result.error_message == "Something went wrong"
        assert result.result is None
    
    def test_invalid_status(self):
        """Test that invalid status raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TaskResult(task="test", status="invalid")
        assert "status" in str(exc_info.value).lower()
    
    def test_valid_statuses(self):
        """Test all valid status values."""
        for status in ["success", "error", "pending"]:
            result = TaskResult(task="test", status=status)
            assert result.status == status
    
    def test_metadata_default(self):
        """Test that metadata defaults to empty dict."""
        result = TaskResult(task="test", status="success")
        assert result.metadata == {}
    
    def test_json_serialization(self):
        """Test that result can be serialized to JSON."""
        result = TaskResult(
            task="test",
            status="success",
            result={"data": 123}
        )
        json_data = result.model_dump_json()
        assert isinstance(json_data, str)
        assert "success" in json_data


@pytest.mark.parametrize("task,expected", [
    ("Test", "test"),
    ("UPPER", "upper"),
    ("  spaced  ", "spaced"),
    ("Mixed-Case", "mixed-case"),
])
def test_task_normalization_parametrized(task, expected):
    """Parametrized test for task normalization."""
    config = CLIConfig(task=task)
    assert config.task == expected

