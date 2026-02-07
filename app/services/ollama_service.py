"""Ollama service for receipt analysis using vision models."""

import json
from pathlib import Path
from typing import Dict

import httpx

from app.config import settings
from app.services.base_llm_service import BaseLLMService, LLMAPIError, LLMAuthenticationError
from app.services.image_utils import image_to_base64, pdf_to_image_base64


class OllamaService(BaseLLMService):
    """Service for interacting with Ollama API for receipt analysis."""

    def __init__(self):
        """Initialize Ollama service."""
        super().__init__()
        self.api_url = settings.ollama_api_url
        self.model = settings.ollama_model

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
            image_base64 = image_to_base64(image_path)
        elif file_extension == ".pdf":
            image_base64 = pdf_to_image_base64(image_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Prepare API request
        payload = {
            "model": self.model,
            "prompt": self.prompt,
            "images": [image_base64],
            "stream": False,
            "format": "json",
        }

        # Call Ollama API
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(f"{self.api_url}/api/generate", json=payload)
                response.raise_for_status()

                result = response.json()
                response_text = result.get("response", "")

                if not response_text:
                    raise LLMAPIError("Empty response from Ollama API")

                # Extract JSON from response
                try:
                    receipt_data = self._extract_json_from_response(response_text)
                except ValueError:
                    # If extraction fails, try parsing the entire response as JSON
                    try:
                        receipt_data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        raise LLMAPIError(
                            f"Failed to parse receipt data: {e}\nResponse: {response_text}"
                        )

                return receipt_data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise LLMAuthenticationError(f"Ollama authentication failed: {e}")
            raise LLMAPIError(f"Ollama API error: {e}")
        except httpx.RequestError as e:
            raise LLMAPIError(f"Failed to connect to Ollama: {e}")

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
