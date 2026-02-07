"""Elasticsearch service for receipt search and indexing."""

from typing import Dict, Optional

from elasticsearch import AsyncElasticsearch

from app.config import settings


class ElasticsearchService:
    """Service for Elasticsearch operations."""

    INDEX_NAME = "receipts"

    def __init__(self):
        """Initialize Elasticsearch service."""
        self.client: Optional[AsyncElasticsearch] = None

    async def connect(self):
        """Connect to Elasticsearch."""
        self.client = AsyncElasticsearch([settings.elasticsearch_url])

    async def disconnect(self):
        """Close Elasticsearch connection."""
        if self.client:
            await self.client.close()

    async def create_index(self):
        """Create receipts index with mapping if it doesn't exist."""
        try:
            exists = await self.client.indices.exists(index=self.INDEX_NAME)
            if exists:
                return
        except Exception:
            # If check fails, try to create anyway and handle the error
            pass

        mapping = {
            "mappings": {
                "properties": {
                    "receipt_id": {"type": "keyword"},
                    "transaction_info": {
                        "properties": {
                            "store_name": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                            "store_address": {"type": "text"},
                            "store_phone": {"type": "keyword"},
                            "date_purchased": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                            "time_purchased": {"type": "keyword"},
                            "cashier": {"type": "text"},
                            "transaction_id": {"type": "keyword"},
                        }
                    },
                    "items": {
                        "type": "nested",
                        "properties": {
                            "upc": {"type": "keyword"},
                            "product_name": {"type": "text"},
                            "quantity": {"type": "float"},
                            "unit_price": {"type": "float"},
                            "total_price": {"type": "float"},
                            "serial_number": {"type": "keyword"},
                            "warranty_details": {
                                "properties": {
                                    "coverage": {"type": "text"},
                                    "requirements": {"type": "text"},
                                    "source_url": {"type": "keyword"},
                                }
                            },
                        },
                    },
                    "totals": {
                        "properties": {
                            "subtotal": {"type": "float"},
                            "sales_tax": {"type": "float"},
                            "grand_total": {"type": "float"},
                        }
                    },
                    "payment_info": {
                        "properties": {
                            "card_type": {"type": "keyword"},
                            "card_last_four": {"type": "keyword"},
                            "auth_code": {"type": "keyword"},
                        }
                    },
                    "return_policy": {
                        "properties": {
                            "policy_id": {"type": "keyword"},
                            "return_window_days": {"type": "float"},
                            "policy_expiration_date": {"type": "text"},
                            "notes": {"type": "text"},
                        }
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                }
            }
        }

        try:
            await self.client.indices.create(index=self.INDEX_NAME, body=mapping)
        except Exception as e:
            # Index might already exist, that's okay
            if "resource_already_exists" not in str(e).lower():
                raise

    async def index_receipt(self, receipt_id: str, receipt_data: Dict):
        """
        Index receipt document in Elasticsearch.

        Args:
            receipt_id: MongoDB document ID
            receipt_data: Receipt document to index
        """
        document = {"receipt_id": receipt_id, **receipt_data}

        await self.client.index(index=self.INDEX_NAME, id=receipt_id, document=document)

    async def search(
        self,
        query: Optional[str] = None,
        store: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Dict:
        """
        Search receipts with filters.

        Args:
            query: Full-text search query
            store: Filter by store name
            date_from: Filter by start date
            date_to: Filter by end date
            min_price: Filter by minimum price
            max_price: Filter by maximum price
            skip: Number of results to skip
            limit: Maximum results to return

        Returns:
            Dictionary with total count, results, and highlights
        """
        must_queries = []
        filter_queries = []

        # Full-text search
        if query:
            must_queries.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "transaction_info.store_name^3",
                            "transaction_info.transaction_id^2",
                            "items.product_name^2",
                            "items.upc",
                            "items.serial_number",
                            "transaction_info.store_address",
                            "payment_info.card_type",
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            )

        # Store filter
        if store:
            filter_queries.append(
                {
                    "match": {
                        "transaction_info.store_name": {
                            "query": store,
                            "fuzziness": "AUTO",
                        }
                    }
                }
            )

        # Date range filter
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to

            filter_queries.append(
                {"range": {"transaction_info.date_purchased.keyword": date_range}}
            )

        # Price range filter (on grand total)
        if min_price is not None or max_price is not None:
            price_range = {}
            if min_price is not None:
                price_range["gte"] = min_price
            if max_price is not None:
                price_range["lte"] = max_price

            filter_queries.append({"range": {"totals.grand_total": price_range}})

        # Build query
        if must_queries or filter_queries:
            search_query = {
                "bool": {
                    "must": must_queries if must_queries else [],
                    "filter": filter_queries if filter_queries else [],
                }
            }
        else:
            search_query = {"match_all": {}}

        # Execute search
        response = await self.client.search(
            index=self.INDEX_NAME,
            query=search_query,
            from_=skip,
            size=limit,
            highlight={
                "fields": {
                    "transaction_info.store_name": {},
                    "items.product_name": {},
                    "items.upc": {},
                    "transaction_info.transaction_id": {},
                }
            },
        )

        # Format results
        results = []
        for hit in response["hits"]["hits"]:
            results.append(
                {
                    "receipt_id": hit["_id"],
                    "score": hit["_score"],
                    "receipt": hit["_source"],
                    "highlights": hit.get("highlight", {}),
                }
            )

        return {"total": response["hits"]["total"]["value"], "results": results}

    async def delete_receipt(self, receipt_id: str):
        """
        Delete receipt from index.

        Args:
            receipt_id: Receipt document ID
        """
        try:
            await self.client.delete(index=self.INDEX_NAME, id=receipt_id)
        except Exception:
            pass  # Document might not exist

    async def health_check(self) -> bool:
        """
        Check if Elasticsearch connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            await self.client.cluster.health()
            return True
        except Exception:
            return False
