"""
Unit tests for CLI functionality.
"""

import json
import pytest
from pathlib import Path
import sys
import tempfile

# Add parent directory to path to import cli
sys.path.insert(0, str(Path(__file__).parent.parent))
from cli import load_json_config


class TestLoadJsonConfig:
    """Test suite for load_json_config function."""
    
    def test_load_json_string(self):
        """Test loading configuration from JSON string."""
        json_string = '{"task": "test", "value": 123}'
        result = load_json_config(json_string)
        assert result == {"task": "test", "value": 123}
    
    def test_load_json_file(self, tmp_path):
        """Test loading configuration from JSON file."""
        # Create temporary JSON file
        config_file = tmp_path / "test_config.json"
        test_data = {"task": "sentiment-analysis", "text": "Hello world"}
        config_file.write_text(json.dumps(test_data))
        
        # Load from file
        result = load_json_config(str(config_file))
        assert result == test_data
    
    def test_invalid_json_string(self):
        """Test that invalid JSON string raises ValueError."""
        with pytest.raises(ValueError):
            load_json_config("{invalid json}")
    
    def test_nonexistent_file(self):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_json_config("nonexistent_file.json")
    
    def test_empty_json_object(self):
        """Test loading empty JSON object."""
        result = load_json_config('{}')
        assert result == {}
    
    def test_nested_json_structure(self):
        """Test loading nested JSON structure."""
        nested_json = '{"level1": {"level2": {"level3": "value"}}}'
        result = load_json_config(nested_json)
        assert result["level1"]["level2"]["level3"] == "value"
    
    @pytest.mark.parametrize("json_input,expected", [
        ('{"a": 1}', {"a": 1}),
        ('{"b": "text"}', {"b": "text"}),
        ('{"c": true}', {"c": True}),
        ('{"d": null}', {"d": None}),
        ('{"e": [1, 2, 3]}', {"e": [1, 2, 3]}),
    ])
    def test_various_json_types(self, json_input, expected):
        """Test loading various JSON data types."""
        result = load_json_config(json_input)
        assert result == expected


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI application."""
    
    def test_config_example_file_exists(self):
        """Test that example config file exists."""
        config_path = Path(__file__).parent.parent / "config.example.json"
        assert config_path.exists(), "config.example.json should exist"
    
    def test_load_example_config(self):
        """Test loading the example configuration file."""
        config_path = Path(__file__).parent.parent / "config.example.json"
        if config_path.exists():
            result = load_json_config(str(config_path))
            assert isinstance(result, dict)

