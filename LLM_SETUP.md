# LLM Package Setup Guide

This guide will help you set up and use the new LLM package for making calls to both local and cloud-based language models.

## 📁 Package Structure

```
src/llm/
├── __init__.py          # Package initialization
├── llm_caller.py        # Main LLM caller implementation
└── README.md            # Detailed package documentation

.env.example             # Environment variable template
examples_llm.py          # Usage examples
tests/test_llm.py        # Unit tests
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 2. Set Up Environment Variables (for cloud providers)

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
# Uncomment and replace the placeholder values with your actual keys
```

Example `.env` file:
```bash
# Uncomment and add your keys:
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
```

### 3. Install Ollama (for local models)

For local model support, install Ollama:

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or visit https://ollama.ai for other installation methods
```

Then pull the models you want to use:

```bash
ollama pull qwen2.5
ollama pull llama3.1:7b
ollama pull gemma2
```

## 💡 Basic Usage

### Using Local Models (Default)

```python
from src.llm import LLMCaller

# Initialize with local mode (default)
llm = LLMCaller(local=True)

# Make a call
response = llm.call(
    prompt="What is the capital of France?",
    temperature=0.7,
    max_tokens=100
)
print(response)
```

### Using Cloud Providers

```python
from src.llm import LLMCaller

# Initialize with cloud mode
llm = LLMCaller(local=False)

# The caller will automatically use the first available provider
# based on which API keys are configured

response = llm.call(
    prompt="Explain quantum computing in one sentence.",
    system_prompt="You are a helpful assistant.",
    temperature=0.7,
    max_tokens=100
)
print(response)
```

### Specifying a Preferred Provider

```python
from src.llm import LLMCaller

# Prefer OpenAI when multiple providers are available
llm = LLMCaller(local=False, preferred_provider="openai")

response = llm.call(
    prompt="Write a haiku about coding.",
    model="gpt-4o-mini"  # Provider-specific parameter
)
print(response)
```

## 📚 Available Models

### Local Models (via Ollama)
- `qwen2.5` - Default local model
- `llama3.1:7b` - Meta's Llama 3.1 7B
- `gemma2` - Google's Gemma 2

### Cloud Providers

**OpenAI:**
- `gpt-4o-mini` (default)
- `gpt-4o`
- `gpt-3.5-turbo`

**Anthropic Claude:**
- `claude-3-5-sonnet-20241022` (default)
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

**Google Gemini:**
- `gemini-1.5-flash` (default)
- `gemini-1.5-pro`

## 🔄 Switching Between Modes

You can switch between local and cloud modes at runtime:

```python
llm = LLMCaller(local=True)
print(f"Local providers: {llm.list_available_providers()}")

# Switch to cloud
llm.switch_mode(local=False)
print(f"Cloud providers: {llm.list_available_providers()}")
```

## 🧪 Running Tests

```bash
# Run all LLM tests
python -m pytest tests/test_llm.py -v

# Run with coverage
python -m pytest tests/test_llm.py --cov=src.llm --cov-report=html
```

## 📖 Examples

Comprehensive examples are available in `examples_llm.py`:

```bash
python examples_llm.py
```

This will demonstrate:
1. Using local models
2. Using cloud providers
3. Specifying preferred providers
4. Switching between modes
5. Advanced options and parameters

## 🛠️ How It Works

### Local Mode (`local=True`)
- Uses **Ollama** to run models locally on your machine
- No API costs, but requires model downloads
- Models run on your hardware (GPU/CPU)
- Default model: `qwen2.5`

### Cloud Mode (`local=False`)
- Connects to cloud APIs using your API keys
- Automatically selects available provider based on:
  1. Preferred provider (if specified)
  2. Default priority: OpenAI → Claude → Gemini
  3. First available provider
- Requires API keys in `.env` file

## 🔑 API Key Setup

### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Anthropic Claude
1. Visit https://console.anthropic.com/
2. Create a new API key
3. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### Google Gemini
1. Visit https://aistudio.google.com/app/apikey
2. Create a new API key
3. Add to `.env`: `GOOGLE_API_KEY=AI...`

## ⚠️ Troubleshooting

### "No module named 'ollama'"
```bash
pip install ollama
```

### "Ollama package is required for local mode"
```bash
# Install Ollama from https://ollama.ai
# Make sure it's running: ollama serve
```

### "No cloud providers configured"
- Check that `.env` file exists in project root
- Ensure at least one API key is set and valid
- API keys should not have the placeholder values

### Models not responding (local)
```bash
# Check if Ollama is running
ollama list

# Pull the model if not available
ollama pull qwen2.5
```

## 📊 Performance Considerations

### Local Models
- **Pros**: No API costs, data privacy, offline capability
- **Cons**: Slower on CPU, requires disk space, limited by hardware

### Cloud Models
- **Pros**: Fast, powerful models, no local resources needed
- **Cons**: API costs, requires internet, data leaves your system

## 🔒 Security Notes

1. **Never commit `.env` file** - It's in `.gitignore` by default
2. **Use `.env.example`** for sharing configuration structure
3. **Rotate API keys** regularly
4. **Use environment-specific keys** for development/production

## 📝 Advanced Usage

### Custom Temperature and Tokens

```python
response = llm.call(
    prompt="Be creative!",
    temperature=0.9,     # Higher = more creative
    max_tokens=500       # Longer responses
)
```

### With System Prompts

```python
response = llm.call(
    prompt="Explain recursion.",
    system_prompt="You are a patient teacher explaining to a beginner."
)
```

### Provider-Specific Parameters

```python
# OpenAI-specific
response = llm.call(
    prompt="Hello",
    model="gpt-4o",
    top_p=0.9
)

# Claude-specific
response = llm.call(
    prompt="Hello",
    model="claude-3-opus-20240229"
)

# Gemini-specific
response = llm.call(
    prompt="Hello",
    model="gemini-1.5-pro"
)
```

## 🤝 Contributing

When adding new providers or features:

1. Update `LLMProvider` enum in `llm_caller.py`
2. Add setup method (e.g., `_setup_newprovider`)
3. Add call method (e.g., `_call_newprovider`)
4. Update documentation in `src/llm/README.md`
5. Add tests in `tests/test_llm.py`
6. Add examples in `examples_llm.py`

## 📞 Support

For issues or questions:
1. Check this guide and `src/llm/README.md`
2. Review examples in `examples_llm.py`
3. Check test cases in `tests/test_llm.py`
4. Consult provider-specific documentation:
   - [Ollama Docs](https://github.com/ollama/ollama)
   - [OpenAI API Docs](https://platform.openai.com/docs)
   - [Claude API Docs](https://docs.anthropic.com)
   - [Gemini API Docs](https://ai.google.dev/docs)

