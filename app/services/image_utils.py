"""Shared image processing utilities for LLM services."""

import base64
from pathlib import Path


def image_to_base64(image_path: Path) -> str:
    """
    Convert image file to base64 string.

    Args:
        image_path: Path to image file

    Returns:
        Base64 encoded string
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def pdf_to_image_base64(pdf_path: Path) -> str:
    """
    Convert first page of PDF to base64 image string.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Base64 encoded string of first page as PNG

    Raises:
        ImportError: If pdf2image is not installed
        ValueError: If PDF conversion fails
    """
    try:
        from pdf2image import convert_from_path

        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if not images:
            raise ValueError("PDF conversion produced no images")

        # Save to temporary file
        temp_image = pdf_path.parent / f"{pdf_path.stem}_temp.png"
        images[0].save(temp_image, "PNG")

        # Convert to base64
        base64_str = image_to_base64(temp_image)

        # Clean up temp file
        temp_image.unlink()

        return base64_str
    except ImportError:
        # Fallback to simpler method if pdf2image not available
        raise ImportError(
            "pdf2image is required for PDF processing. Install with: pip install pdf2image"
        )
