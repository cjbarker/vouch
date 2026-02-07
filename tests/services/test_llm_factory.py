"""Tests for LLM factory."""

import pytest
from unittest.mock import patch

from app.config import LLMProvider
from app.services.llm_factory import LLMServiceFactory
from app.services.ollama_service import OllamaService
from app.services.openai_service import OpenAIService
from app.services.gemini_service import GeminiService
from app.services.base_llm_service import LLMAuthenticationError


class TestLLMServiceFactory:
    """Tests for LLMServiceFactory."""

    def test_create_ollama_service(self, mock_settings):
        """Test creating Ollama service."""
        mock_settings.llm_provider = LLMProvider.OLLAMA
        service = LLMServiceFactory.create()
        assert isinstance(service, OllamaService)
        assert service.model == mock_settings.ollama_model

    def test_create_openai_service(self, mock_settings):
        """Test creating OpenAI service."""
        mock_settings.llm_provider = LLMProvider.OPENAI
        mock_settings.openai_api_key = "test_key"
        service = LLMServiceFactory.create()
        assert isinstance(service, OpenAIService)
        assert service.model == mock_settings.openai_model

    def test_create_gemini_service(self, mock_settings):
        """Test creating Gemini service."""
        mock_settings.llm_provider = LLMProvider.GEMINI
        mock_settings.gemini_api_key = "test_key"
        service = LLMServiceFactory.create()
        assert isinstance(service, GeminiService)
        assert service.model_name == mock_settings.gemini_model

    def test_create_with_explicit_provider(self, mock_settings):
        """Test creating service with explicit provider."""
        mock_settings.llm_provider = LLMProvider.GEMINI
        # Create Ollama even though default is Gemini
        service = LLMServiceFactory.create(provider=LLMProvider.OLLAMA)
        assert isinstance(service, OllamaService)

    def test_create_openai_without_api_key(self, mock_settings):
        """Test creating OpenAI service without API key."""
        mock_settings.llm_provider = LLMProvider.OPENAI
        mock_settings.openai_api_key = None
        with pytest.raises(LLMAuthenticationError, match="OPENAI_API_KEY"):
            LLMServiceFactory.create()

    def test_create_gemini_without_api_key(self, mock_settings):
        """Test creating Gemini service without API key."""
        mock_settings.llm_provider = LLMProvider.GEMINI
        mock_settings.gemini_api_key = None
        with pytest.raises(LLMAuthenticationError, match="GEMINI_API_KEY"):
            LLMServiceFactory.create()

    def test_factory_initializes_providers(self):
        """Test that factory initializes provider mapping."""
        # Trigger initialization
        LLMServiceFactory._initialize_providers()
        assert len(LLMServiceFactory._providers) == 3
        assert LLMProvider.OLLAMA in LLMServiceFactory._providers
        assert LLMProvider.OPENAI in LLMServiceFactory._providers
        assert LLMProvider.GEMINI in LLMServiceFactory._providers
