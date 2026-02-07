"""Tests for OpenAI service."""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.openai_service import OpenAIService
from app.services.base_llm_service import (
    LLMAPIError,
    LLMAuthenticationError,
    LLMRateLimitError,
)


class TestOpenAIService:
    """Tests for OpenAIService."""

    @pytest.fixture
    def openai_service(self, mock_settings):
        """Create OpenAI service instance."""
        mock_settings.openai_api_key = "test_key"
        with patch("app.services.openai_service.settings", mock_settings):
            return OpenAIService()

    def test_initialization(self, openai_service, mock_settings):
        """Test OpenAI service initialization."""
        assert openai_service.model == mock_settings.openai_model
        assert openai_service.max_tokens == mock_settings.openai_max_tokens
        assert openai_service.temperature == mock_settings.openai_temperature

    def test_initialization_without_api_key(self, mock_settings):
        """Test initialization without API key."""
        mock_settings.openai_api_key = None
        with patch("app.services.openai_service.settings", mock_settings):
            with pytest.raises(LLMAuthenticationError, match="OPENAI_API_KEY"):
                OpenAIService()

    @pytest.mark.asyncio
    async def test_analyze_receipt(self, openai_service, sample_image_path):
        """Test analyzing receipt with OpenAI."""
        mock_response = AsyncMock()
        mock_choice = AsyncMock()
        mock_message = AsyncMock()
        mock_message.content = '{"transaction_info": {"store_name": "Test"}, "items": [], "totals": {"grand_total": 0.0}}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        openai_service.client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        result = await openai_service.analyze_receipt(sample_image_path)
        assert "transaction_info" in result
        assert result["transaction_info"]["store_name"] == "Test"

    @pytest.mark.asyncio
    async def test_analyze_receipt_rate_limit(self, openai_service, sample_image_path):
        """Test handling rate limit error."""
        from openai import RateLimitError

        openai_service.client.chat.completions.create = AsyncMock(
            side_effect=RateLimitError("Rate limit exceeded", response=None, body=None)
        )

        with pytest.raises(LLMRateLimitError):
            await openai_service.analyze_receipt(sample_image_path)

    @pytest.mark.asyncio
    async def test_health_check_success(self, openai_service):
        """Test successful health check."""
        openai_service.client.models.list = AsyncMock(return_value=[])
        result = await openai_service.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, openai_service):
        """Test failed health check."""
        openai_service.client.models.list = AsyncMock(side_effect=Exception("Error"))
        result = await openai_service.health_check()
        assert result is False
