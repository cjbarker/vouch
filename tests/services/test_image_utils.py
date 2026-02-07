"""Tests for image utility functions."""

import base64

import pytest
from PIL import Image

from app.services.image_utils import image_to_base64, pdf_to_image_base64


class TestImageToBase64:
    """Tests for image_to_base64 function."""

    def test_convert_jpg_to_base64(self, sample_image_path):
        """Test converting JPG image to base64."""
        result = image_to_base64(sample_image_path)
        assert isinstance(result, str)
        assert len(result) > 0
        # Verify it's valid base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_convert_png_to_base64(self, tmp_path):
        """Test converting PNG image to base64."""
        png_path = tmp_path / "test.png"
        img = Image.new("RGB", (50, 50), color="blue")
        img.save(png_path)

        result = image_to_base64(png_path)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_nonexistent_file(self, tmp_path):
        """Test with nonexistent file."""
        nonexistent = tmp_path / "does_not_exist.jpg"
        with pytest.raises(FileNotFoundError):
            image_to_base64(nonexistent)


class TestPdfToImageBase64:
    """Tests for pdf_to_image_base64 function."""

    @pytest.mark.skipif(True, reason="Requires pdf2image and poppler, skipping in basic tests")
    def test_convert_pdf_to_base64(self, sample_pdf_path):
        """Test converting PDF to base64 image."""
        # This would require a real PDF and pdf2image installed
        result = pdf_to_image_base64(sample_pdf_path)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pdf_conversion_import_error(self, sample_pdf_path, monkeypatch):
        """Test PDF conversion when pdf2image not available."""

        # Simulate ImportError
        def mock_import(*args, **kwargs):
            raise ImportError("pdf2image not found")

        monkeypatch.setattr("builtins.__import__", mock_import, raising=False)

        with pytest.raises(ImportError, match="pdf2image is required"):
            pdf_to_image_base64(sample_pdf_path)
