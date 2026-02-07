"""OpenAI service for receipt analysis using vision models."""

import json
from pathlib import Path
from typing import Dict

from openai import APIError, AsyncOpenAI, AuthenticationError, RateLimitError

from app.config import settings
from app.services.base_llm_service import (
    BaseLLMService,
    LLMAPIError,
    LLMAuthenticationError,
    LLMRateLimitError,
)
from app.services.image_utils import image_to_base64, pdf_to_image_base64


class OpenAIService(BaseLLMService):
    """Service for interacting with OpenAI API for receipt analysis."""

    def __init__(self):
        """Initialize OpenAI service."""
        super().__init__()

        if not settings.openai_api_key:
            raise LLMAuthenticationError("OPENAI_API_KEY is required for OpenAI provider")

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def analyze_receipt(self, image_path: Path) -> Dict:
        """
        Analyze receipt image using OpenAI vision model.

        Args:
            image_path: Path to receipt image file (JPG, PNG, or PDF)

        Returns:
            Structured receipt data as dictionary

        Raises:
            LLMServiceError: If analysis fails
        """
        # Determine file type and convert to base64
        file_extension = image_path.suffix.lower()

        if file_extension in [".jpg", ".jpeg", ".png"]:
            image_base64 = image_to_base64(image_path)
            # Determine mime type
            mime_type = "image/jpeg" if file_extension in [".jpg", ".jpeg"] else "image/png"
        elif file_extension == ".pdf":
            image_base64 = pdf_to_image_base64(image_path)
            mime_type = "image/png"
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Format as data URL
        image_data_url = f"data:{mime_type};base64,{image_base64}"

        try:
            # Call OpenAI API with vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.prompt},
                            {"type": "image_url", "image_url": {"url": image_data_url}},
                        ],
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )

            # Extract response text
            response_text = response.choices[0].message.content

            if not response_text:
                raise LLMAPIError("Empty response from OpenAI API")

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

        except AuthenticationError as e:
            raise LLMAuthenticationError(f"OpenAI authentication failed: {e}")
        except RateLimitError as e:
            raise LLMRateLimitError(f"OpenAI rate limit exceeded: {e}")
        except APIError as e:
            raise LLMAPIError(f"OpenAI API error: {e}")
        except Exception as e:
            raise LLMAPIError(f"Unexpected error with OpenAI: {e}")

    async def health_check(self) -> bool:
        """
        Check if OpenAI service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Test with a simple API call
            await self.client.models.list()
            return True
        except Exception:
            return False
