"""Tests for Gemini service."""

import pytest
from unittest.mock import Mock, patch

from app.services.gemini_service import GeminiService
from app.services.base_llm_service import (
    LLMAPIError,
    LLMAuthenticationError,
    LLMRateLimitError,
)


class TestGeminiService:
    """Tests for GeminiService."""

    @pytest.fixture
    def gemini_service(self, mock_settings):
        """Create Gemini service instance."""
        mock_settings.gemini_api_key = "test_key"
        with patch("app.services.gemini_service.settings", mock_settings):
            with patch("app.services.gemini_service.genai.Client") as mock_client:
                service = GeminiService()
                service.client = mock_client.return_value
                return service

    def test_initialization(self, gemini_service, mock_settings):
        """Test Gemini service initialization."""
        assert gemini_service.model_name == mock_settings.gemini_model
        assert gemini_service.temperature == mock_settings.gemini_temperature

    def test_initialization_without_api_key(self, mock_settings):
        """Test initialization without API key."""
        mock_settings.gemini_api_key = None
        with patch("app.services.gemini_service.settings", mock_settings):
            with pytest.raises(LLMAuthenticationError, match="GEMINI_API_KEY"):
                GeminiService()

    @pytest.mark.asyncio
    async def test_analyze_receipt(self, gemini_service, sample_image_path):
        """Test analyzing receipt with Gemini."""
        mock_response = Mock()
        mock_response.text = '{"transaction_info": {"store_name": "Test"}, "items": [], "totals": {"grand_total": 0.0}}'
        gemini_service.client.models.generate_content.return_value = mock_response

        result = await gemini_service.analyze_receipt(sample_image_path)
        assert "transaction_info" in result
        assert result["transaction_info"]["store_name"] == "Test"

    @pytest.mark.asyncio
    async def test_analyze_receipt_auth_error(self, gemini_service, sample_image_path):
        """Test handling authentication error."""
        gemini_service.client.models.generate_content.side_effect = Exception(
            "API key invalid"
        )

        with pytest.raises(LLMAuthenticationError):
            await gemini_service.analyze_receipt(sample_image_path)

    @pytest.mark.asyncio
    async def test_health_check_success(self, gemini_service):
        """Test successful health check."""
        gemini_service.client.models.list.return_value = []
        result = await gemini_service.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, gemini_service):
        """Test failed health check."""
        gemini_service.client.models.list.side_effect = Exception("Error")
        result = await gemini_service.health_check()
        assert result is False
