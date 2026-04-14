"""OpenAPI-compatible LLM service for receipt analysis.

Connects to any LLM endpoint that exposes an OpenAI-compatible
chat completions API (e.g. vLLM, LiteLLM, Together AI, Azure OpenAI).
"""

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


class OpenAPIService(BaseLLMService):
    """Service for interacting with OpenAI-compatible API endpoints."""

    def __init__(self):
        """Initialize OpenAPI-compatible service."""
        super().__init__()

        if not settings.openapi_api_url:
            raise LLMAPIError("OPENAPI_API_URL is required for the openapi provider")
        if not settings.openapi_api_key:
            raise LLMAuthenticationError("OPENAPI_API_KEY is required for the openapi provider")

        self.client = AsyncOpenAI(
            base_url=settings.openapi_api_url,
            api_key=settings.openapi_api_key,
        )
        self.model = settings.openapi_model
        self.max_tokens = settings.openapi_max_tokens
        self.temperature = settings.openapi_temperature

    async def analyze_receipt(self, image_path: Path) -> Dict:
        """
        Analyze receipt image using an OpenAI-compatible endpoint.

        Args:
            image_path: Path to receipt image file (JPG, PNG, or PDF)

        Returns:
            Structured receipt data as dictionary

        Raises:
            LLMServiceError: If analysis fails
        """
        file_extension = image_path.suffix.lower()

        if file_extension in [".jpg", ".jpeg", ".png"]:
            image_base64 = image_to_base64(image_path)
            mime_type = "image/jpeg" if file_extension in [".jpg", ".jpeg"] else "image/png"
        elif file_extension == ".pdf":
            image_base64 = pdf_to_image_base64(image_path)
            mime_type = "image/png"
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        image_data_url = f"data:{mime_type};base64,{image_base64}"

        try:
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
            )

            response_text = response.choices[0].message.content

            if not response_text:
                raise LLMAPIError("Empty response from OpenAPI-compatible endpoint")

            try:
                receipt_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                try:
                    receipt_data = self._extract_json_from_response(response_text)
                except ValueError:
                    raise LLMAPIError(
                        f"Failed to parse receipt data: {e}\nResponse: {response_text}"
                    )

            return receipt_data

        except AuthenticationError as e:
            raise LLMAuthenticationError(f"OpenAPI endpoint authentication failed: {e}")
        except RateLimitError as e:
            raise LLMRateLimitError(f"OpenAPI endpoint rate limit exceeded: {e}")
        except APIError as e:
            raise LLMAPIError(f"OpenAPI endpoint error: {e}")
        except LLMAPIError:
            raise
        except Exception as e:
            raise LLMAPIError(f"Unexpected error with OpenAPI endpoint: {e}")

    async def health_check(self) -> bool:
        """
        Check if the OpenAPI-compatible endpoint is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
