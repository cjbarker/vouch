"""Tests for search router."""

from unittest.mock import AsyncMock, patch

import pytest


class TestSearchRouter:
    """Tests for search router."""

    @pytest.fixture
    def mock_services(self, sample_receipt_data):
        """Mock required services."""
        with (
            patch("app.routers.search.mongodb_service") as mock_mongo,
            patch("app.routers.search.elasticsearch_service") as mock_elastic,
        ):

            # Mock search results
            mock_elastic.search_receipts = AsyncMock(
                return_value={
                    "hits": {
                        "total": {"value": 1},
                        "hits": [
                            {
                                "_id": "test_id",
                                "_score": 1.0,
                                "_source": sample_receipt_data,
                            }
                        ],
                    }
                }
            )

            # Mock get receipt
            receipt_with_id = {"_id": "test_id", **sample_receipt_data}
            mock_mongo.get_receipt = AsyncMock(return_value=receipt_with_id)

            # Mock list receipts
            mock_mongo.list_receipts = AsyncMock(return_value=[receipt_with_id])
            mock_mongo.count_receipts = AsyncMock(return_value=1)

            yield {
                "mongo": mock_mongo,
                "elastic": mock_elastic,
            }

    @pytest.mark.integration
    def test_search_receipts(self, test_client, mock_services):
        """Test searching receipts."""
        response = test_client.get("/api/search?q=Test Store")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["receipt"]["transaction_info"]["store_name"] == "Test Store"

    @pytest.mark.integration
    def test_search_with_filters(self, test_client, mock_services):
        """Test search with filters."""
        response = test_client.get("/api/search?q=Store&store_name=Test&min_price=10&max_price=100")

        assert response.status_code == 200
        mock_services["elastic"].search_receipts.assert_called_once()

    @pytest.mark.integration
    def test_search_empty_results(self, test_client, mock_services):
        """Test search with no results."""
        mock_services["elastic"].search_receipts.return_value = {
            "hits": {"total": {"value": 0}, "hits": []}
        }

        response = test_client.get("/api/search?q=NonexistentStore")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["results"]) == 0

    @pytest.mark.integration
    def test_get_receipt_by_id(self, test_client, mock_services):
        """Test getting receipt by ID."""
        response = test_client.get("/api/receipts/test_id")

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_info"]["store_name"] == "Test Store"

    @pytest.mark.integration
    def test_get_nonexistent_receipt(self, test_client, mock_services):
        """Test getting nonexistent receipt."""
        mock_services["mongo"].get_receipt.return_value = None

        response = test_client.get("/api/receipts/nonexistent_id")

        assert response.status_code == 404

    @pytest.mark.integration
    def test_list_receipts(self, test_client, mock_services):
        """Test listing all receipts."""
        response = test_client.get("/api/receipts?skip=0&limit=20")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["results"]) == 1

    @pytest.mark.integration
    def test_list_receipts_pagination(self, test_client, mock_services):
        """Test pagination in list receipts."""
        response = test_client.get("/api/receipts?skip=10&limit=5")

        assert response.status_code == 200
        mock_services["mongo"].list_receipts.assert_called_once()
        call_args = mock_services["mongo"].list_receipts.call_args
        assert call_args[1]["skip"] == 10
        assert call_args[1]["limit"] == 5
