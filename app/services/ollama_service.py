"""Ollama service for receipt analysis using vision models."""

import base64
import json
import re
from pathlib import Path
from typing import Dict

import httpx
from PIL import Image
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # Fallback for older installations

from app.config import settings


class OllamaService:
    """Service for interacting with Ollama API for receipt analysis."""

    def __init__(self):
        """Initialize Ollama service."""
        self.api_url = settings.ollama_api_url
        self.model = settings.ollama_model
        self.prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load the receipt analysis prompt from prompt.txt."""
        prompt_path = Path(__file__).parent.parent.parent / "prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _image_to_base64(self, image_path: Path) -> str:
        """Convert image file to base64 string."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _pdf_to_image_base64(self, pdf_path: Path) -> str:
        """Convert first page of PDF to base64 image string."""
        try:
            from pdf2image import convert_from_path

            images = convert_from_path(pdf_path, first_page=1, last_page=1)
            if not images:
                raise ValueError("PDF conversion produced no images")

            # Save to temporary file
            temp_image = pdf_path.parent / f"{pdf_path.stem}_temp.png"
            images[0].save(temp_image, "PNG")

            # Convert to base64
            base64_str = self._image_to_base64(temp_image)

            # Clean up temp file
            temp_image.unlink()

            return base64_str
        except ImportError:
            # Fallback to simpler method if pdf2image not available
            raise ImportError("pdf2image is required for PDF processing. Install with: pip install pdf2image")

    def _extract_json_from_response(self, text: str) -> dict:
        """Extract JSON object from LLM response text."""
        # Try to find JSON object in the response
        # Look for content between curly braces
        json_pattern = r'\{[\s\S]*\}'
        matches = re.findall(json_pattern, text)

        if not matches:
            raise ValueError("No JSON object found in response")

        # Try to parse each match until we find valid JSON
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        raise ValueError("Could not parse JSON from response")

    async def analyze_receipt(self, image_path: Path) -> Dict:
        """
        Analyze receipt image using Ollama vision model.

        Args:
            image_path: Path to receipt image file (JPG, PNG, or PDF)

        Returns:
            Structured receipt data as dictionary

        Raises:
            ValueError: If file format is unsupported or analysis fails
            httpx.HTTPError: If API request fails
        """
        # Determine file type and convert to base64
        file_extension = image_path.suffix.lower()

        if file_extension in [".jpg", ".jpeg", ".png"]:
            image_base64 = self._image_to_base64(image_path)
        elif file_extension == ".pdf":
            image_base64 = self._pdf_to_image_base64(image_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Prepare API request
        payload = {
            "model": self.model,
            "prompt": self.prompt,
            "images": [image_base64],
            "stream": False,
            "format": "json"
        }

        # Call Ollama API
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.api_url}/api/generate",
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "")

            if not response_text:
                raise ValueError("Empty response from Ollama API")

            # Extract JSON from response
            try:
                receipt_data = self._extract_json_from_response(response_text)
            except ValueError:
                # If extraction fails, try parsing the entire response as JSON
                try:
                    receipt_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse receipt data: {e}\nResponse: {response_text}")

            return receipt_data

    async def health_check(self) -> bool:
        """
        Check if Ollama service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.api_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
