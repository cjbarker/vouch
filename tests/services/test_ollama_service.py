"""Tests for Ollama service."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path

from app.services.ollama_service import OllamaService
from app.services.base_llm_service import LLMAPIError, LLMAuthenticationError


class TestOllamaService:
    """Tests for OllamaService."""

    @pytest.fixture
    def ollama_service(self, mock_settings):
        """Create Ollama service instance."""
        with patch("app.services.ollama_service.settings", mock_settings):
            return OllamaService()

    def test_initialization(self, ollama_service, mock_settings):
        """Test Ollama service initialization."""
        assert ollama_service.api_url == mock_settings.ollama_api_url
        assert ollama_service.model == mock_settings.ollama_model
        assert len(ollama_service.prompt) > 0

    @pytest.mark.asyncio
    async def test_analyze_receipt_jpg(self, ollama_service, sample_image_path):
        """Test analyzing JPG receipt."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"transaction_info": {"store_name": "Test Store"}, "items": [], "totals": {"grand_total": 0.0}}'
        }
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await ollama_service.analyze_receipt(sample_image_path)
            assert "transaction_info" in result
            assert result["transaction_info"]["store_name"] == "Test Store"

    @pytest.mark.asyncio
    async def test_analyze_receipt_unsupported_format(self, ollama_service, tmp_path):
        """Test analyzing unsupported file format."""
        unsupported_file = tmp_path / "test.txt"
        unsupported_file.write_text("test")

        with pytest.raises(ValueError, match="Unsupported file format"):
            await ollama_service.analyze_receipt(unsupported_file)

    @pytest.mark.asyncio
    async def test_analyze_receipt_empty_response(
        self, ollama_service, sample_image_path
    ):
        """Test handling empty response from Ollama."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": ""}
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            with pytest.raises(LLMAPIError, match="Empty response"):
                await ollama_service.analyze_receipt(sample_image_path)

    @pytest.mark.asyncio
    async def test_analyze_receipt_auth_error(self, ollama_service, sample_image_path):
        """Test handling authentication error."""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            with pytest.raises(LLMAuthenticationError):
                await ollama_service.analyze_receipt(sample_image_path)

    @pytest.mark.asyncio
    async def test_health_check_success(self, ollama_service):
        """Test successful health check."""
        mock_response = AsyncMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await ollama_service.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, ollama_service):
        """Test failed health check."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = Exception("Connection error")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await ollama_service.health_check()
            assert result is False

    def test_extract_json_from_response(self, ollama_service):
        """Test JSON extraction from response."""
        response_text = 'Here is the data: {"key": "value"}'
        result = ollama_service._extract_json_from_response(response_text)
        assert result == {"key": "value"}

    def test_extract_json_no_json(self, ollama_service):
        """Test JSON extraction when no JSON present."""
        response_text = "No JSON here"
        with pytest.raises(ValueError, match="No JSON object found"):
            ollama_service._extract_json_from_response(response_text)
