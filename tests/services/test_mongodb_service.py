"""Tests for MongoDB service."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from bson import ObjectId

from app.services.mongodb_service import MongoDBService


class TestMongoDBService:
    """Tests for MongoDBService."""

    @pytest.fixture
    def service(self):
        """Create a MongoDBService with mocked internals."""
        svc = MongoDBService()
        svc.client = Mock()
        svc.db = Mock()
        svc.collection = Mock()
        return svc

    @pytest.mark.asyncio
    async def test_save_receipt(self, service, sample_receipt_data):
        """Test saving a receipt adds metadata and returns ID."""
        inserted_id = ObjectId()
        service.collection.insert_one = AsyncMock(return_value=Mock(inserted_id=inserted_id))

        result = await service.save_receipt(sample_receipt_data)

        assert result == str(inserted_id)
        call_args = service.collection.insert_one.call_args[0][0]
        assert "created_at" in call_args
        assert "updated_at" in call_args
        assert isinstance(call_args["created_at"], datetime)

    @pytest.mark.asyncio
    async def test_get_receipt_valid_id(self, service, sample_receipt_data):
        """Test retrieving a receipt by valid ID."""
        obj_id = ObjectId()
        doc = {"_id": obj_id, **sample_receipt_data}
        service.collection.find_one = AsyncMock(return_value=doc)

        result = await service.get_receipt(str(obj_id))

        assert result is not None
        assert result["_id"] == str(obj_id)

    @pytest.mark.asyncio
    async def test_get_receipt_invalid_id(self, service):
        """Test retrieving a receipt with invalid ID returns None."""
        result = await service.get_receipt("not-a-valid-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_receipt_not_found(self, service):
        """Test retrieving a non-existent receipt returns None."""
        service.collection.find_one = AsyncMock(return_value=None)

        result = await service.get_receipt(str(ObjectId()))
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_receipt_success(self, service):
        """Test deleting an existing receipt."""
        service.collection.delete_one = AsyncMock(return_value=Mock(deleted_count=1))

        result = await service.delete_receipt(str(ObjectId()))
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_receipt_not_found(self, service):
        """Test deleting a non-existent receipt."""
        service.collection.delete_one = AsyncMock(return_value=Mock(deleted_count=0))

        result = await service.delete_receipt(str(ObjectId()))
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_receipt_invalid_id(self, service):
        """Test deleting with invalid ID returns False."""
        result = await service.delete_receipt("invalid-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_count_receipts(self, service):
        """Test counting receipts."""
        service.collection.count_documents = AsyncMock(return_value=5)

        result = await service.count_receipts()
        assert result == 5

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, service):
        """Test health check when MongoDB is healthy."""
        service.client.admin.command = AsyncMock(return_value={"ok": 1})

        result = await service.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, service):
        """Test health check when MongoDB is down."""
        service.client.admin.command = AsyncMock(side_effect=Exception("Connection refused"))

        result = await service.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_search_by_store_escapes_regex(self, service):
        """Test that store name search escapes regex special characters."""

        class MockAsyncCursor:
            def __init__(self):
                self.data = []

            def sort(self, *args, **kwargs):
                return self

            def __aiter__(self):
                return self

            async def __anext__(self):
                raise StopAsyncIteration

        service.collection.find = Mock(return_value=MockAsyncCursor())

        await service.search_receipts_by_store("Store (Test)")

        call_args = service.collection.find.call_args[0][0]
        regex_value = call_args["transaction_info.store_name"]["$regex"]
        # Parentheses should be escaped
        assert r"\(" in regex_value
        assert r"\)" in regex_value

    @pytest.mark.asyncio
    async def test_disconnect_closes_client(self, service):
        """Test disconnect closes the client."""
        await service.disconnect()
        service.client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_client(self):
        """Test disconnect with no client is safe."""
        svc = MongoDBService()
        await svc.disconnect()  # Should not raise
