"""Tests for upload router."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image


class TestUploadRouter:
    """Tests for upload router."""

    @pytest.fixture
    def mock_services(self, sample_receipt_data):
        """Mock all required services."""
        with (
            patch("app.routers.upload.mongodb_service") as mock_mongo,
            patch("app.routers.upload.elasticsearch_service") as mock_elastic,
            patch("app.routers.upload.llm_service") as mock_llm,
        ):

            mock_mongo.save_receipt = AsyncMock(return_value="test_receipt_id")
            mock_elastic.index_receipt = AsyncMock()
            mock_llm.analyze_receipt = AsyncMock(return_value=sample_receipt_data)

            yield {
                "mongo": mock_mongo,
                "elastic": mock_elastic,
                "llm": mock_llm,
            }

    def create_test_image(self) -> bytes:
        """Create test image bytes."""
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        return img_bytes.getvalue()

    @pytest.mark.integration
    def test_upload_receipt_success(self, test_client, mock_services):
        """Test successful receipt upload."""
        img_data = self.create_test_image()

        response = test_client.post(
            "/api/upload", files={"file": ("receipt.jpg", img_data, "image/jpeg")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "receipt_id" in data
        assert data["receipt"]["transaction_info"]["store_name"] == "Test Store"

    @pytest.mark.integration
    def test_upload_invalid_file_type(self, test_client):
        """Test upload with invalid file type."""
        response = test_client.post(
            "/api/upload", files={"file": ("test.txt", b"test content", "text/plain")}
        )

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    @pytest.mark.integration
    def test_upload_file_too_large(self, test_client, mock_settings):
        """Test upload with file too large."""
        # Create file larger than max size
        large_data = b"x" * (mock_settings.max_upload_size + 1000)

        response = test_client.post(
            "/api/upload", files={"file": ("receipt.jpg", large_data, "image/jpeg")}
        )

        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]

    @pytest.mark.integration
    def test_upload_analysis_failure(self, test_client, mock_services):
        """Test upload when analysis fails."""
        mock_services["llm"].analyze_receipt.side_effect = Exception("Analysis failed")
        img_data = self.create_test_image()

        response = test_client.post(
            "/api/upload", files={"file": ("receipt.jpg", img_data, "image/jpeg")}
        )

        # Should return 200 with success=False
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data
