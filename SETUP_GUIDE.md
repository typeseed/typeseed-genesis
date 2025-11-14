# TypeSeed Genesis - Setup Guide

## Quick Reference

### 1️⃣ Initial Setup

```bash
# Clone/navigate to the project directory
cd typeseed-genesis

# Run the automated setup script
./setup_venv.sh

# Or use make
make venv
make install
```

### 2️⃣ Daily Development Workflow

```bash
# Activate virtual environment
source .venv/bin/activate

# Run your code
python cli.py --config config.example.json

# Run tests
make test

# Deactivate when done
deactivate
```

### 3️⃣ Testing Commands

```bash
# Basic test run
pytest

# With verbose output
pytest -v

# With coverage
make test-cov

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::TestLoadJsonConfig::test_load_json_string
```

### 4️⃣ Pydantic Usage

#### Validating Configuration

```python
from src.models import CLIConfig
from pydantic import ValidationError

try:
    config = CLIConfig(
        task="sentiment-analysis",
        text="Test input",
        output_format="json"
    )
    print(config.model_dump_json(indent=2))
except ValidationError as e:
    print(f"Validation error: {e}")
```

#### Creating Task Results

```python
from src.models import TaskResult

result = TaskResult(
    task="my-task",
    status="success",
    result={"output": "data"},
    metadata={"time": 1.23}
)

# Convert to dict
result_dict = result.model_dump()

# Convert to JSON
result_json = result.model_dump_json()
```

### 5️⃣ Common Make Commands

```bash
make help          # Show all available commands
make venv          # Create virtual environment
make install       # Install dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make test-verbose  # Run tests with detailed output
make clean         # Clean build artifacts
```

### 6️⃣ Project Files Overview

| File | Purpose |
|------|---------|
| `cli.py` | Main CLI application |
| `models.py` | Pydantic models for validation |
| `requirements.txt` | Python dependencies |
| `setup_venv.sh` | Automated environment setup |
| `pytest.ini` | Pytest configuration |
| `Makefile` | Common task shortcuts |
| `.python-version` | Python version specification |
| `tests/conftest.py` | Shared test fixtures |
| `tests/test_*.py` | Test files |

### 7️⃣ Troubleshooting

#### Virtual Environment Issues

```bash
# If activation fails, try:
python3 -m venv .venv --clear

# Then activate again
source .venv/bin/activate
```

#### Dependency Issues

```bash
# Reinstall all dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Test Failures

```bash
# Run with maximum verbosity
pytest -vv --tb=long --show-capture=all

# Run a single test
pytest tests/test_cli.py::test_name -v
```

### 8️⃣ Adding New Tests

1. Create test file in `tests/` directory (name it `test_*.py`)
2. Import necessary modules and fixtures
3. Write test functions starting with `test_`
4. Use assertions to verify behavior

Example:

```python
def test_my_feature():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

### 9️⃣ Using Fixtures

Shared fixtures are defined in `tests/conftest.py`:

```python
def test_with_config(sample_config):
    """Use the sample_config fixture."""
    assert sample_config["task"] == "sentiment-analysis"

def test_with_temp_file(temp_config_file):
    """Use temporary file fixture."""
    assert temp_config_file.exists()
```

### 🔟 Best Practices

1. **Always activate the virtual environment** before working
2. **Run tests before committing** code changes
3. **Use Pydantic models** for data validation
4. **Write tests** for new features
5. **Keep requirements.txt updated** when adding dependencies
6. **Use type hints** in Python code
7. **Document complex functions** with docstrings

## Additional Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)

---

**Need help?** Check the main [README.md](README.md) for more details.

