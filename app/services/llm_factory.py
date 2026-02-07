"""Factory for creating LLM service instances."""

from typing import Optional

from app.config import LLMProvider, settings
from app.services.base_llm_service import BaseLLMService


class LLMServiceFactory:
    """Factory for creating LLM service instances."""

    _providers = {}  # Will be populated lazily to avoid circular imports

    @classmethod
    def _initialize_providers(cls):
        """Lazy initialization of provider mapping to avoid circular imports."""
        if not cls._providers:
            from app.services.gemini_service import GeminiService
            from app.services.ollama_service import OllamaService
            from app.services.openai_service import OpenAIService

            cls._providers = {
                LLMProvider.OLLAMA: OllamaService,
                LLMProvider.OPENAI: OpenAIService,
                LLMProvider.GEMINI: GeminiService,
            }

    @classmethod
    def create(cls, provider: Optional[LLMProvider] = None) -> BaseLLMService:
        """
        Create an LLM service instance for the specified provider.

        Args:
            provider: LLM provider to use. If None, uses settings.llm_provider

        Returns:
            Instance of the appropriate LLM service

        Raises:
            ValueError: If provider is not supported
        """
        cls._initialize_providers()

        provider = provider or settings.llm_provider
        service_class = cls._providers.get(provider)

        if not service_class:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        return service_class()
