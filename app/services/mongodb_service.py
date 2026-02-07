"""MongoDB service for receipt storage and retrieval."""

from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings


class MongoDBService:
    """Service for MongoDB operations."""

    def __init__(self):
        """Initialize MongoDB service."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection = None

    async def connect(self):
        """Connect to MongoDB and initialize database and collection."""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_db_name]
        self.collection = self.db["receipts"]

        # Create indexes
        await self._create_indexes()

    async def _create_indexes(self):
        """Create indexes for efficient querying."""
        await self.collection.create_index("transaction_info.store_name")
        await self.collection.create_index("transaction_info.date_purchased")
        await self.collection.create_index("transaction_info.transaction_id", unique=True)
        await self.collection.create_index("items.product_name")
        await self.collection.create_index("items.upc")
        await self.collection.create_index("created_at")

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()

    async def save_receipt(self, receipt_data: Dict) -> str:
        """
        Save receipt to MongoDB.

        Args:
            receipt_data: Receipt document to save

        Returns:
            String ID of saved document
        """
        # Add metadata
        document = {
            **receipt_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_receipt(self, receipt_id: str) -> Optional[Dict]:
        """
        Retrieve single receipt by ID.

        Args:
            receipt_id: MongoDB ObjectId as string

        Returns:
            Receipt document or None if not found
        """
        try:
            obj_id = ObjectId(receipt_id)
        except Exception:
            return None

        document = await self.collection.find_one({"_id": obj_id})

        if document:
            document["_id"] = str(document["_id"])

        return document

    async def get_all_receipts(self, skip: int = 0, limit: int = 20) -> List[Dict]:
        """
        Get paginated list of all receipts.

        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of receipt documents
        """
        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        receipts = []

        async for document in cursor:
            document["_id"] = str(document["_id"])
            receipts.append(document)

        return receipts

    async def count_receipts(self) -> int:
        """
        Get total count of receipts.

        Returns:
            Total number of receipts in collection
        """
        return await self.collection.count_documents({})

    async def search_receipts_by_store(self, store_name: str) -> List[Dict]:
        """
        Search receipts by store name.

        Args:
            store_name: Store name to search for (partial match)

        Returns:
            List of matching receipt documents
        """
        query = {"transaction_info.store_name": {"$regex": store_name, "$options": "i"}}

        cursor = self.collection.find(query).sort("created_at", -1)
        receipts = []

        async for document in cursor:
            document["_id"] = str(document["_id"])
            receipts.append(document)

        return receipts

    async def search_receipts_by_date_range(
        self, date_from: Optional[str] = None, date_to: Optional[str] = None
    ) -> List[Dict]:
        """
        Search receipts by date range.

        Args:
            date_from: Start date (YYYY-MM-DD format or any format from receipts)
            date_to: End date (YYYY-MM-DD format or any format from receipts)

        Returns:
            List of matching receipt documents
        """
        query = {}

        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to

            query["transaction_info.date_purchased"] = date_query

        cursor = self.collection.find(query).sort("created_at", -1)
        receipts = []

        async for document in cursor:
            document["_id"] = str(document["_id"])
            receipts.append(document)

        return receipts

    async def health_check(self) -> bool:
        """
        Check if MongoDB connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False
