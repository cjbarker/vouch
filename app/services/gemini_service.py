"""Gemini service for receipt analysis using vision models."""

import base64
import json
from pathlib import Path
from typing import Dict

from google import genai
from google.genai import types

from app.config import settings
from app.services.base_llm_service import (
    BaseLLMService,
    LLMAPIError,
    LLMAuthenticationError,
    LLMRateLimitError,
)
from app.services.image_utils import pdf_to_image_base64


class GeminiService(BaseLLMService):
    """Service for interacting with Google Gemini API for receipt analysis."""

    def __init__(self):
        """Initialize Gemini service."""
        super().__init__()

        if not settings.gemini_api_key:
            raise LLMAuthenticationError("GEMINI_API_KEY is required for Gemini provider")

        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.temperature = settings.gemini_temperature

    async def analyze_receipt(self, image_path: Path) -> Dict:
        """
        Analyze receipt image using Gemini vision model.

        Args:
            image_path: Path to receipt image file (JPG, PNG, or PDF)

        Returns:
            Structured receipt data as dictionary

        Raises:
            LLMServiceError: If analysis fails
        """
        # Determine file type and load image
        file_extension = image_path.suffix.lower()

        try:
            if file_extension in [".jpg", ".jpeg", ".png"]:
                # Read image file as bytes
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                # Determine mime type
                mime_type = "image/jpeg" if file_extension in [".jpg", ".jpeg"] else "image/png"
            elif file_extension == ".pdf":
                # Convert PDF to image first
                image_base64 = pdf_to_image_base64(image_path)
                image_bytes = base64.b64decode(image_base64)
                mime_type = "image/png"
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

            # Create part with inline data
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            # Call Gemini API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[self.prompt, image_part],
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type="application/json",
                ),
            )

            # Extract response text
            response_text = response.text

            if not response_text:
                raise LLMAPIError("Empty response from Gemini API")

            # Parse JSON response
            try:
                receipt_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to extract JSON from response
                try:
                    receipt_data = self._extract_json_from_response(response_text)
                except ValueError:
                    raise LLMAPIError(
                        f"Failed to parse receipt data: {e}\nResponse: {response_text}"
                    )

            return receipt_data

        except Exception as e:
            # Check error type based on message content
            error_msg = str(e).lower()
            if "auth" in error_msg or "api key" in error_msg or "401" in error_msg:
                raise LLMAuthenticationError(f"Gemini authentication failed: {e}")
            elif "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
                raise LLMRateLimitError(f"Gemini rate limit exceeded: {e}")
            else:
                raise LLMAPIError(f"Gemini API error: {e}")

    async def health_check(self) -> bool:
        """
        Check if Gemini service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Test with a simple API call to list models
            self.client.models.list()
            return True
        except Exception:
            return False
