"""Tests for OpenAPI-compatible LLM service."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.services.base_llm_service import LLMAPIError, LLMAuthenticationError, LLMRateLimitError
from app.services.openapi_service import OpenAPIService


class TestOpenAPIService:
    """Tests for OpenAPIService."""

    @pytest.fixture
    def openapi_service(self, mock_settings):
        """Create OpenAPI service instance."""
        mock_settings.openapi_api_url = "http://localhost:8080/v1"
        mock_settings.openapi_api_key = "test_key"
        mock_settings.openapi_model = "test-model"
        with patch("app.services.openapi_service.settings", mock_settings):
            return OpenAPIService()

    def test_initialization(self, openapi_service):
        """Test OpenAPI service initialization."""
        assert openapi_service.model == "test-model"
        assert openapi_service.max_tokens == 4096
        assert openapi_service.temperature == 0.0

    def test_initialization_without_api_url(self, mock_settings):
        """Test initialization without API URL."""
        mock_settings.openapi_api_url = None
        mock_settings.openapi_api_key = "test_key"
        with patch("app.services.openapi_service.settings", mock_settings):
            with pytest.raises(LLMAPIError, match="OPENAPI_API_URL"):
                OpenAPIService()

    def test_initialization_without_api_key(self, mock_settings):
        """Test initialization without API key."""
        mock_settings.openapi_api_url = "http://localhost:8080/v1"
        mock_settings.openapi_api_key = None
        with patch("app.services.openapi_service.settings", mock_settings):
            with pytest.raises(LLMAuthenticationError, match="OPENAPI_API_KEY"):
                OpenAPIService()

    @pytest.mark.asyncio
    async def test_analyze_receipt(self, openapi_service, sample_image_path):
        """Test analyzing receipt with OpenAPI endpoint."""
        mock_response = AsyncMock()
        mock_choice = AsyncMock()
        mock_message = AsyncMock()
        mock_message.content = '{"transaction_info": {"store_name": "Test"}, "items": [], "totals": {"grand_total": 0.0}}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        openapi_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await openapi_service.analyze_receipt(sample_image_path)
        assert "transaction_info" in result
        assert result["transaction_info"]["store_name"] == "Test"

    @pytest.mark.asyncio
    async def test_analyze_receipt_rate_limit(self, openapi_service, sample_image_path):
        """Test handling rate limit error."""
        from openai import RateLimitError

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_response.request = Mock()
        mock_response.request.url = "http://localhost:8080/v1/chat/completions"

        openapi_service.client.chat.completions.create = AsyncMock(
            side_effect=RateLimitError("Rate limit exceeded", response=mock_response, body=None)
        )

        with pytest.raises(LLMRateLimitError):
            await openapi_service.analyze_receipt(sample_image_path)

    @pytest.mark.asyncio
    async def test_health_check_success(self, openapi_service):
        """Test successful health check."""
        openapi_service.client.models.list = AsyncMock(return_value=[])
        result = await openapi_service.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, openapi_service):
        """Test failed health check."""
        openapi_service.client.models.list = AsyncMock(side_effect=Exception("Error"))
        result = await openapi_service.health_check()
        assert result is False
