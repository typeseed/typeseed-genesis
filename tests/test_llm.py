"""
Tests for the LLM package.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.llm import LLMCaller
from src.llm.llm_caller import LLMProvider


class TestLLMCallerInitialization:
    """Test LLM Caller initialization."""
    
    def test_local_mode_initialization(self):
        """Test initialization in local mode."""
        with patch('src.llm.llm_caller.ollama') as mock_ollama:
            llm = LLMCaller(local=True)
            assert llm.local is True
            assert hasattr(llm, 'available_local_models')
    
    def test_cloud_mode_initialization_no_keys(self):
        """Test initialization in cloud mode without API keys."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="No cloud providers configured"):
                LLMCaller(local=False)
    
    def test_cloud_mode_initialization_with_openai_key(self):
        """Test initialization in cloud mode with OpenAI key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True):
            with patch('src.llm.llm_caller.openai.OpenAI') as mock_openai:
                mock_openai.return_value = Mock()
                llm = LLMCaller(local=False)
                assert llm.local is False
                assert LLMProvider.OPENAI in llm.available_cloud_providers


class TestLLMCallerLocalMode:
    """Test LLM Caller in local mode."""
    
    def test_list_available_providers_local(self):
        """Test listing available providers in local mode."""
        with patch('src.llm.llm_caller.ollama') as mock_ollama:
            llm = LLMCaller(local=True)
            providers = llm.list_available_providers()
            assert isinstance(providers, list)
            assert len(providers) > 0
    
    def test_call_local_model(self):
        """Test calling a local model."""
        with patch('src.llm.llm_caller.ollama') as mock_ollama:
            mock_ollama.chat.return_value = {
                'message': {'content': 'Test response'}
            }
            
            llm = LLMCaller(local=True)
            response = llm.call(
                prompt="Test prompt",
                temperature=0.7,
                max_tokens=100
            )
            
            assert response == 'Test response'
            mock_ollama.chat.assert_called_once()


class TestLLMCallerCloudMode:
    """Test LLM Caller in cloud mode."""
    
    def test_openai_call(self):
        """Test calling OpenAI API."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True):
            with patch('src.llm.llm_caller.openai.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                
                # Mock the response
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = 'OpenAI response'
                mock_client.chat.completions.create.return_value = mock_response
                
                llm = LLMCaller(local=False)
                response = llm.call(
                    prompt="Test prompt",
                    temperature=0.7,
                    max_tokens=100
                )
                
                assert response == 'OpenAI response'
                mock_client.chat.completions.create.assert_called_once()
    
    def test_claude_call(self):
        """Test calling Claude API."""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'}, clear=True):
            with patch('src.llm.llm_caller.anthropic.Anthropic') as mock_anthropic_class:
                mock_client = Mock()
                mock_anthropic_class.return_value = mock_client
                
                # Mock the response
                mock_response = Mock()
                mock_content = Mock()
                mock_content.text = 'Claude response'
                mock_response.content = [mock_content]
                mock_client.messages.create.return_value = mock_response
                
                llm = LLMCaller(local=False)
                response = llm.call(
                    prompt="Test prompt",
                    temperature=0.7,
                    max_tokens=100
                )
                
                assert response == 'Claude response'
                mock_client.messages.create.assert_called_once()
    
    def test_gemini_call(self):
        """Test calling Gemini API."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}, clear=True):
            with patch('src.llm.llm_caller.google.generativeai') as mock_genai:
                mock_genai.configure = Mock()
                
                # Mock model and response
                mock_model = Mock()
                mock_response = Mock()
                mock_response.text = 'Gemini response'
                mock_model.generate_content.return_value = mock_response
                mock_genai.GenerativeModel.return_value = mock_model
                
                llm = LLMCaller(local=False)
                response = llm.call(
                    prompt="Test prompt",
                    temperature=0.7,
                    max_tokens=100
                )
                
                assert response == 'Gemini response'


class TestLLMCallerModeSwitching:
    """Test mode switching functionality."""
    
    def test_switch_to_cloud_mode(self):
        """Test switching from local to cloud mode."""
        with patch('src.llm.llm_caller.ollama') as mock_ollama:
            llm = LLMCaller(local=True)
            assert llm.local is True
            
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True):
                with patch('src.llm.llm_caller.openai.OpenAI') as mock_openai:
                    mock_openai.return_value = Mock()
                    llm.switch_mode(local=False)
                    assert llm.local is False
    
    def test_switch_to_local_mode(self):
        """Test switching from cloud to local mode."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True):
            with patch('src.llm.llm_caller.openai.OpenAI') as mock_openai:
                mock_openai.return_value = Mock()
                llm = LLMCaller(local=False)
                assert llm.local is False
                
                with patch('src.llm.llm_caller.ollama') as mock_ollama:
                    llm.switch_mode(local=True)
                    assert llm.local is True


class TestLLMCallerProviderSelection:
    """Test provider selection logic."""
    
    def test_preferred_provider(self):
        """Test using a preferred provider."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'openai_key',
            'ANTHROPIC_API_KEY': 'anthropic_key'
        }, clear=True):
            with patch('src.llm.llm_caller.openai.OpenAI') as mock_openai:
                with patch('src.llm.llm_caller.anthropic.Anthropic') as mock_anthropic:
                    mock_openai.return_value = Mock()
                    mock_anthropic.return_value = Mock()
                    
                    llm = LLMCaller(local=False, preferred_provider="claude")
                    
                    # Should select Claude based on preference
                    selected = llm._select_cloud_provider()
                    assert selected == LLMProvider.CLAUDE
    
    def test_provider_priority_order(self):
        """Test default provider priority order."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'openai_key',
            'GOOGLE_API_KEY': 'google_key'
        }, clear=True):
            with patch('src.llm.llm_caller.openai.OpenAI') as mock_openai:
                with patch('src.llm.llm_caller.google.generativeai') as mock_genai:
                    mock_openai.return_value = Mock()
                    mock_genai.configure = Mock()
                    
                    llm = LLMCaller(local=False)
                    
                    # Should select OpenAI (higher priority)
                    selected = llm._select_cloud_provider()
                    assert selected == LLMProvider.OPENAI


class TestLLMCallerErrorHandling:
    """Test error handling."""
    
    def test_local_mode_without_ollama(self):
        """Test error when Ollama is not installed."""
        with patch('src.llm.llm_caller.ollama', side_effect=ImportError):
            with pytest.raises(RuntimeError, match="Ollama package is required"):
                LLMCaller(local=True)
    
    def test_call_with_api_error(self):
        """Test handling of API errors."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True):
            with patch('src.llm.llm_caller.openai.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                mock_client.chat.completions.create.side_effect = Exception("API Error")
                
                llm = LLMCaller(local=False)
                
                with pytest.raises(Exception, match="API Error"):
                    llm.call(prompt="Test prompt")

