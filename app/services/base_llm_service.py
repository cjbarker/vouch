"""Base LLM service class and shared utilities."""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""


class LLMAPIError(LLMServiceError):
    """API communication error."""


class LLMAuthenticationError(LLMServiceError):
    """Authentication/API key error."""


class LLMRateLimitError(LLMServiceError):
    """Rate limit exceeded."""


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    def __init__(self):
        """Initialize the base service."""
        self.prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load the receipt analysis prompt from prompt.txt."""
        prompt_path = Path(__file__).parent.parent.parent / "prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    @abstractmethod
    async def analyze_receipt(self, image_path: Path) -> Dict:
        """
        Analyze receipt image using the LLM provider.

        Args:
            image_path: Path to receipt image file (JPG, PNG, or PDF)

        Returns:
            Structured receipt data as dictionary

        Raises:
            LLMServiceError: If analysis fails
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the LLM service is available.

        Returns:
            True if service is healthy, False otherwise
        """

    def _extract_json_from_response(self, text: str) -> dict:
        """
        Extract JSON object from LLM response text.

        Args:
            text: Response text from LLM

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If no valid JSON found in response
        """
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
