"""Tests for Elasticsearch service."""

from unittest.mock import AsyncMock

import pytest

from app.services.elasticsearch_service import ElasticsearchService


class TestElasticsearchService:
    """Tests for ElasticsearchService."""

    @pytest.fixture
    def service(self):
        """Create an ElasticsearchService with mocked client."""
        svc = ElasticsearchService()
        svc.client = AsyncMock()
        return svc

    @pytest.mark.asyncio
    async def test_create_index_when_not_exists(self, service):
        """Test index creation when it doesn't exist."""
        service.client.indices.exists = AsyncMock(return_value=False)
        service.client.indices.create = AsyncMock(return_value={"acknowledged": True})

        await service.create_index()

        service.client.indices.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_index_already_exists(self, service):
        """Test index creation skipped when already exists."""
        service.client.indices.exists = AsyncMock(return_value=True)

        await service.create_index()

        service.client.indices.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_index_receipt(self, service, sample_receipt_data):
        """Test indexing a receipt document."""
        service.client.index = AsyncMock(return_value={"result": "created"})

        await service.index_receipt("test_id", sample_receipt_data)

        service.client.index.assert_called_once()
        call_kwargs = service.client.index.call_args[1]
        assert call_kwargs["id"] == "test_id"
        assert call_kwargs["index"] == "receipts"

    @pytest.mark.asyncio
    async def test_search_with_query(self, service):
        """Test search with a text query."""
        service.client.search = AsyncMock(
            return_value={
                "hits": {
                    "total": {"value": 1},
                    "hits": [
                        {
                            "_id": "test_id",
                            "_score": 1.5,
                            "_source": {"transaction_info": {"store_name": "Test"}},
                        }
                    ],
                }
            }
        )

        result = await service.search(query="Test")

        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["receipt_id"] == "test_id"

    @pytest.mark.asyncio
    async def test_search_match_all(self, service):
        """Test search with no filters returns match_all query."""
        service.client.search = AsyncMock(
            return_value={"hits": {"total": {"value": 0}, "hits": []}}
        )

        result = await service.search()

        assert result["total"] == 0
        call_kwargs = service.client.search.call_args[1]
        assert call_kwargs["query"] == {"match_all": {}}

    @pytest.mark.asyncio
    async def test_search_with_store_filter(self, service):
        """Test search with store filter."""
        service.client.search = AsyncMock(
            return_value={"hits": {"total": {"value": 0}, "hits": []}}
        )

        await service.search(store="Walmart")

        call_kwargs = service.client.search.call_args[1]
        query = call_kwargs["query"]
        assert "bool" in query
        assert len(query["bool"]["filter"]) == 1

    @pytest.mark.asyncio
    async def test_search_with_price_range(self, service):
        """Test search with price range filter."""
        service.client.search = AsyncMock(
            return_value={"hits": {"total": {"value": 0}, "hits": []}}
        )

        await service.search(min_price=10.0, max_price=100.0)

        call_kwargs = service.client.search.call_args[1]
        query = call_kwargs["query"]
        assert "bool" in query

    @pytest.mark.asyncio
    async def test_search_pagination(self, service):
        """Test search pagination parameters."""
        service.client.search = AsyncMock(
            return_value={"hits": {"total": {"value": 0}, "hits": []}}
        )

        await service.search(skip=10, limit=5)

        call_kwargs = service.client.search.call_args[1]
        assert call_kwargs["from_"] == 10
        assert call_kwargs["size"] == 5

    @pytest.mark.asyncio
    async def test_delete_receipt(self, service):
        """Test deleting a receipt from index."""
        service.client.delete = AsyncMock()

        await service.delete_receipt("test_id")

        service.client.delete.assert_called_once_with(index="receipts", id="test_id")

    @pytest.mark.asyncio
    async def test_delete_receipt_not_found(self, service):
        """Test deleting a non-existent receipt logs warning."""
        service.client.delete = AsyncMock(side_effect=Exception("Not found"))

        # Should not raise
        await service.delete_receipt("missing_id")

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, service):
        """Test health check when Elasticsearch is healthy."""
        service.client.cluster.health = AsyncMock(return_value={"status": "green"})

        result = await service.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, service):
        """Test health check when Elasticsearch is down."""
        service.client.cluster.health = AsyncMock(side_effect=Exception("Connection refused"))

        result = await service.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_disconnect(self, service):
        """Test disconnect closes client."""
        await service.disconnect()
        service.client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_client(self):
        """Test disconnect with no client is safe."""
        svc = ElasticsearchService()
        await svc.disconnect()  # Should not raise
