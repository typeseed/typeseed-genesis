"""
LLM Caller module for unified interface to local and cloud LLM providers.
"""

from binascii import crc32
import os
import json
import logging
from typing import Optional, Dict, List, Any
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    # Local providers
    # Cloud providers
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


CACHE_FILE = "llm_cache.json"


class LLMCaller:
    """
    Unified interface for calling both local and cloud-based LLM providers.

    Local mode uses Ollama to run models like Qwen 2.5, Llama 3.1 7B, and Gemma.
    Cloud mode uses API keys to connect to OpenAI, Claude, or Gemini.
    """

    def __init__(self, local: bool = True, preferred_provider: Optional[str] = None):
        """
        Initialize the LLM Caller.

        Args:
            local: If True, use local models via Ollama. If False, use cloud providers.
            preferred_provider: Optional preferred provider name (for cloud mode).
        """
        self.local = local
        self.preferred_provider = preferred_provider
        self._setup_providers()

        self._load_cache()

    def get_key_data(self, payload: dict) -> str:
        # Convert to JSON string and then to hex
        json_str = json.dumps(payload, sort_keys=True)

        ## crc hash of the json string
        crc_hash = crc32(json_str.encode("utf-8"))
        # Return the hex string
        return str(crc_hash)

    def _save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=4)

    def _load_cache(self):
        try:
            with open(CACHE_FILE, "r") as f:
                self.cache = json.load(f)

            logger.info(f"Cache loaded successfully: {len(self.cache)} items")
        except FileNotFoundError:
            logger.info("Cache file not found. Creating new cache.")
            self.cache = {}
        except json.JSONDecodeError:
            logger.info("Cache file is not valid JSON. Creating new cache.")
            self.cache = {}

    def _get_cache(self, payload: Any) -> Optional[str]:
        key = self.get_key_data(payload)
        return self.cache.get(key, None)

    def _set_cache(self, payload: Any, value: str):
        key = self.get_key_data(payload)
        self.cache[key] = value
        self._save_cache()

    def _setup_providers(self):
        """Setup and validate available providers."""
        if self.local:
            self._setup_local_providers()
        else:
            self._setup_cloud_providers()

    def _setup_local_providers(self):
        """Setup local Ollama-based providers."""
        try:
            import ollama

            self.ollama_client = ollama

            models_list = self.ollama_client.list()
            models = models_list.models

            self.available_local_models = models

            logger.info(
                f"Local mode enabled. Available models: {[m.model for m in self.available_local_models]}"
            )
        except ImportError:
            logger.error(
                "Ollama package not installed. Install with: pip install ollama"
            )
            raise RuntimeError("Ollama package is required for local mode")

    def _setup_cloud_providers(self):
        """Setup cloud providers based on available API keys."""
        self.available_cloud_providers = {}

        # Check OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                import openai

                self.available_cloud_providers[LLMProvider.OPENAI] = openai.OpenAI(
                    api_key=openai_key
                )
                logger.info("OpenAI provider configured")
            except ImportError:
                logger.warning(
                    "OpenAI package not installed. Install with: pip install openai"
                )

        # Check Anthropic Claude
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
            try:
                import anthropic

                self.available_cloud_providers[LLMProvider.CLAUDE] = (
                    anthropic.Anthropic(api_key=anthropic_key)
                )
                logger.info("Claude provider configured")
            except ImportError:
                logger.warning(
                    "Anthropic package not installed. Install with: pip install anthropic"
                )

        # Check Google Gemini
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key and google_key != "your_google_api_key_here":
            try:
                import google.generativeai as genai

                genai.configure(api_key=google_key)
                self.available_cloud_providers[LLMProvider.GEMINI] = genai
                logger.info("Gemini provider configured")
            except ImportError:
                logger.warning(
                    "Google Generative AI package not installed. Install with: pip install google-generativeai"
                )

        if not self.available_cloud_providers:
            raise RuntimeError(
                "No cloud providers configured. Please set at least one API key in .env file:\n"
                "- OPENAI_API_KEY\n"
                "- ANTHROPIC_API_KEY\n"
                "- GOOGLE_API_KEY"
            )

        logger.info(
            f"Cloud mode enabled. Available providers: {list(self.available_cloud_providers.keys())}"
        )

    def _select_local_model(self) -> LLMProvider:
        """Select a local model (default to Qwen 2.5)."""
        return self.available_local_models[0]

    def _select_cloud_provider(self) -> LLMProvider:
        """Select a cloud provider based on preference or availability."""
        if self.preferred_provider:
            for provider in self.available_cloud_providers.keys():
                if provider.value == self.preferred_provider:
                    return provider

        # Default priority: OpenAI -> Claude -> Gemini
        priority_order = [LLMProvider.OPENAI, LLMProvider.CLAUDE, LLMProvider.GEMINI]
        for provider in priority_order:
            if provider in self.available_cloud_providers:
                return provider

        # Fallback to first available
        return list(self.available_cloud_providers.keys())[0]

    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        allow_cache: bool = True,
        **kwargs,
    ) -> str:
        """
        Make a call to the LLM with the given prompt.

        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters


        Returns:
            Generated text response from the LLM
        """

        payload = {
            "local": self.local,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        if allow_cache:
            cache = self._get_cache(payload)
            if cache:
                return cache

        if self.local:
            response = self._call_local(
                prompt, system_prompt, temperature, max_tokens, **kwargs
            )
            self._set_cache(payload, response)
            return response
        else:
            response = self._call_cloud(
                prompt, system_prompt, temperature, max_tokens, **kwargs
            )
            self._set_cache(payload, response)
            return response

    def _call_local(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Call local Ollama model."""
        model = self._select_local_model()
        logger.info(f"Calling local model: {model.model}")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.ollama_client.chat(
                model=model.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs,
                },
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling local model {model.model}: {e}")
            raise

    def _call_cloud(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Call cloud provider API."""
        provider = self._select_cloud_provider()
        logger.info(f"Calling cloud provider: {provider.value}")

        try:
            if provider == LLMProvider.OPENAI:
                return self._call_openai(
                    prompt, system_prompt, temperature, max_tokens, **kwargs
                )
            elif provider == LLMProvider.CLAUDE:
                return self._call_claude(
                    prompt, system_prompt, temperature, max_tokens, **kwargs
                )
            elif provider == LLMProvider.GEMINI:
                return self._call_gemini(
                    prompt, system_prompt, temperature, max_tokens, **kwargs
                )
        except Exception as e:
            logger.error(f"Error calling {provider.value}: {e}")
            raise

    def _call_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Call OpenAI API."""
        client = self.available_cloud_providers[LLMProvider.OPENAI]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model = kwargs.pop("model", "gpt-4o-mini")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.choices[0].message.content

    def _call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Call Anthropic Claude API."""
        client = self.available_cloud_providers[LLMProvider.CLAUDE]

        model = kwargs.pop("model", "claude-3-5-sonnet-20241022")

        message_kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }

        if system_prompt:
            message_kwargs["system"] = system_prompt

        response = client.messages.create(**message_kwargs)
        return response.content[0].text

    def _call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> str:
        """Call Google Gemini API."""
        genai = self.available_cloud_providers[LLMProvider.GEMINI]

        model_name = kwargs.pop("model", "gemini-2.5-flash-lite")

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            **kwargs,
        }

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None,
        )

        response = model.generate_content(prompt)
        return response.text

    def list_available_providers(self) -> List[str]:
        """
        List all available providers based on current mode.

        Returns:
            List of provider names
        """
        if self.local:
            return [model.value for model in self.available_local_models]
        else:
            return [
                provider.value for provider in self.available_cloud_providers.keys()
            ]

    def switch_mode(self, local: bool):
        """
        Switch between local and cloud mode.

        Args:
            local: True for local mode, False for cloud mode
        """
        self.local = local
        self._setup_providers()
        logger.info(f"Switched to {'local' if local else 'cloud'} mode")


# # Initialize with cloud mode
# llm = LLMCaller(local=True)

# # Make a call with system prompt
# response = llm.call(
#     prompt="Generate a numbered list of 100 people name and surnames",
#     system_prompt="You are a helpful assistant.",
#     temperature=0.7,
#     max_tokens=1000,
# )
# print(response)
