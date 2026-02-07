"""Pytest configuration and shared fixtures."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.config import LLMProvider, Settings


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with safe defaults."""
    return Settings(
        mongodb_url="mongodb://localhost:27017",
        mongodb_db_name="vouch_test",
        elasticsearch_url="http://localhost:9200",
        llm_provider=LLMProvider.OLLAMA,
        ollama_api_url="http://localhost:11434",
        ollama_model="llama3.2-vision",
        openai_api_key="test_key",
        openai_model="gpt-4-vision-preview",
        gemini_api_key="test_key",
        gemini_model="gemini-1.5-pro-vision",
        upload_dir=Path("/tmp/test_uploads"),
        max_upload_size=5242880,
        allowed_extensions="jpg,jpeg,png,pdf",
    )


@pytest.fixture
def mock_settings(test_settings: Settings) -> Generator[Settings, None, None]:
    """Mock the settings module."""
    with patch("app.config.settings", test_settings):
        yield test_settings


@pytest.fixture
def sample_receipt_data() -> dict:
    """Sample receipt data for testing - matches actual models.py schema."""
    return {
        "transaction_info": {
            "store_name": "Test Store",
            "store_address": "123 Test St",
            "store_phone": "555-1234",
            "date_purchased": "2024-01-15",
            "time_purchased": "14:30:00",
            "cashier": "John Doe",
            "transaction_id": "TX123456",
        },
        "items": [
            {
                "upc": "123456789012",
                "product_name": "Test Product",
                "quantity": 2,
                "unit_price": 10.00,
                "total_price": 20.00,
                "serial_number": "SN123456",
                "warranty_details": None,
            }
        ],
        "totals": {
            "subtotal": 20.00,
            "sales_tax": 1.60,
            "grand_total": 21.60,
        },
        "payment_info": {
            "card_type": "Visa",
            "card_last_four": "1234",
            "auth_code": "AUTH123",
        },
        "return_policy": {
            "policy_id": "RP001",
            "return_window_days": 30,
            "policy_expiration_date": "2024-02-14",
            "notes": "Receipt required for returns",
        },
    }


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    """Create a sample test image."""
    from PIL import Image

    image_path = tmp_path / "test_receipt.jpg"
    img = Image.new("RGB", (100, 100), color="white")
    img.save(image_path)
    return image_path


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    """Create a sample test PDF."""
    pdf_path = tmp_path / "test_receipt.pdf"
    # Create minimal PDF
    pdf_path.write_text("%PDF-1.4\n%%EOF")
    return pdf_path


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Mock httpx AsyncClient for Ollama service."""
    client = AsyncMock()
    response = AsyncMock()
    response.status_code = 200
    response.json.return_value = {"response": '{"test": "data"}'}
    response.raise_for_status = Mock()
    client.post.return_value = response
    client.get.return_value = response
    return client


@pytest.fixture
def mock_openai_client() -> AsyncMock:
    """Mock OpenAI AsyncClient."""
    client = AsyncMock()
    response = AsyncMock()
    choice = AsyncMock()
    message = AsyncMock()
    message.content = '{"test": "data"}'
    choice.message = message
    response.choices = [choice]
    client.chat.completions.create.return_value = response
    client.models.list.return_value = AsyncMock()
    return client


@pytest.fixture
def mock_genai_client() -> Mock:
    """Mock Google Genai Client."""
    client = Mock()
    response = Mock()
    response.text = '{"test": "data"}'
    client.models.generate_content.return_value = response
    client.models.list.return_value = []
    return client


@pytest.fixture
def mock_mongodb_client() -> Mock:
    """Mock MongoDB client."""
    client = Mock()
    db = Mock()
    collection = Mock()

    # Setup async methods
    collection.insert_one = AsyncMock(return_value=Mock(inserted_id="test_id"))
    collection.find_one = AsyncMock(return_value={"_id": "test_id", "test": "data"})
    collection.find = Mock(return_value=AsyncMock(to_list=AsyncMock(return_value=[])))
    collection.count_documents = AsyncMock(return_value=0)

    db.__getitem__ = Mock(return_value=collection)
    client.__getitem__ = Mock(return_value=db)

    return client


@pytest.fixture
def mock_elasticsearch_client() -> AsyncMock:
    """Mock Elasticsearch client."""
    client = AsyncMock()
    client.ping.return_value = True
    client.indices.exists.return_value = False
    client.indices.create.return_value = {"acknowledged": True}
    client.index.return_value = {"result": "created"}
    client.search.return_value = {
        "hits": {"total": {"value": 0}, "hits": []}
    }
    return client


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create FastAPI test client."""
    # Import here to avoid circular imports
    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_llm_service(sample_receipt_data) -> AsyncMock:
    """Mock LLM service for testing."""
    service = AsyncMock()
    service.analyze_receipt.return_value = sample_receipt_data
    service.health_check.return_value = True
    return service


@pytest.fixture(autouse=True)
def cleanup_uploads(tmp_path: Path):
    """Clean up test uploads after each test."""
    yield
    # Cleanup happens automatically with tmp_path
