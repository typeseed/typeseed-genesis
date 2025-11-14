# typeseed-genesis

The core engine of synthetic data generation.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setting Up the Virtual Environment

#### Automated Setup (Recommended)

Run the setup script to create a virtual environment and install all dependencies:

```bash
./setup_venv.sh
```

#### Manual Setup

If you prefer manual setup or are on Windows:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Activating the Virtual Environment

After initial setup, you'll need to activate the virtual environment each time you work on the project:

```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

To deactivate the virtual environment:

```bash
deactivate
```

## 📦 Dependencies

The project uses the following key dependencies:

- **transformers** (>=4.30.0): Hugging Face Transformers library
- **torch** (>=2.0.0): PyTorch deep learning framework
- **numpy** (>=1.24.0): Numerical computing library
- **pandas** (>=2.0.0): Data manipulation and analysis
- **pydantic** (>=2.0.0): Data validation using Python type annotations
- **pytest** (>=7.4.0): Testing framework
- **pytest-cov** (>=4.1.0): Code coverage plugin for pytest

## 🧪 Testing

The project uses pytest as the testing framework with coverage reporting.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cli.py

# Run tests with coverage report
pytest --cov=. --cov-report=html

# Run only unit tests (marked as @pytest.mark.unit)
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Structure

```
tests/
├── __init__.py
├── test_cli.py      # CLI functionality tests
└── test_models.py   # Pydantic model validation tests
```

### Writing Tests

Tests are automatically discovered if they follow these naming conventions:
- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*`
- Test functions: `test_*`

Example test:

```python
def test_example():
    """Test description."""
    result = some_function()
    assert result == expected_value
```

## 🏗️ Project Structure

```
typeseed-genesis/
├── cli.py                 # Main CLI application
├── models.py              # Pydantic models for data validation
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── setup_venv.sh         # Virtual environment setup script
├── .python-version       # Python version specification
├── config.example.json   # Example configuration file
└── tests/                # Test suite
    ├── __init__.py
    ├── test_cli.py
    └── test_models.py
```

## 🔧 Configuration with Pydantic

The project uses Pydantic for configuration validation and data modeling. See `models.py` for available models:

### CLIConfig Model

Validates CLI configuration with automatic type checking and data validation:

```python
from src.models import CLIConfig

config = CLIConfig(
    task="sentiment-analysis",
    text="I love this product!",
    model_name="distilbert-base",
    parameters={"max_length": 512},
    verbose=True,
    output_format="json"
)
```

### TaskResult Model

Structured result output with validation:

```python
from src.models import TaskResult

result = TaskResult(
    task="sentiment-analysis",
    status="success",
    result={"sentiment": "positive", "score": 0.95},
    metadata={"processing_time": 0.42}
)
```

## 💻 CLI Usage

```bash
# Using JSON string
python cli.py --config '{"task": "sentiment-analysis", "text": "I love this!"}'

# Using JSON file
python cli.py --config config.json

# With verbose output
python cli.py --config config.json --verbose

# With output file
python cli.py --config config.json --output results.json
```

## 🐛 Troubleshooting

### Virtual Environment Not Activating

Make sure you're using the correct activation command for your operating system (see above).

### Import Errors

Make sure the virtual environment is activated and all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Test Failures

Run tests with verbose output to see detailed error messages:

```bash
pytest -v --tb=long
```

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Create a virtual environment and install dependencies
2. Write tests for new features
3. Ensure all tests pass: `pytest`
4. Check code coverage: `pytest --cov=. --cov-report=html`
