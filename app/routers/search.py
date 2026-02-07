"""Search router for receipt retrieval and search."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import Receipt, SearchQuery, SearchResponse, SearchResult
from app.services.elasticsearch_service import ElasticsearchService
from app.services.mongodb_service import MongoDBService

router = APIRouter(prefix="/api", tags=["search"])
logger = logging.getLogger(__name__)

# Service instances (will be injected from main app)
mongodb_service: Optional[MongoDBService] = None
elasticsearch_service: Optional[ElasticsearchService] = None


def set_services(mongo: MongoDBService, elastic: ElasticsearchService):
    """Set service instances."""
    global mongodb_service, elasticsearch_service
    mongodb_service = mongo
    elasticsearch_service = elastic


@router.get("/search", response_model=SearchResponse)
async def search_receipts(
    q: Optional[str] = Query(None, description="Search query text"),
    store: Optional[str] = Query(None, description="Filter by store name"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
):
    """
    Search receipts with optional filters.

    Supports full-text search across store names, product names, UPCs, and transaction IDs.
    Can filter by store, date range, and price range.
    """
    try:
        # Create search query
        search_query = SearchQuery(
            q=q,
            store=store,
            date_from=date_from,
            date_to=date_to,
            min_price=min_price,
            max_price=max_price,
            skip=skip,
            limit=limit,
        )

        # Execute search
        search_results = await elasticsearch_service.search(
            query=q,
            store=store,
            date_from=date_from,
            date_to=date_to,
            min_price=min_price,
            max_price=max_price,
            skip=skip,
            limit=limit,
        )

        # Format results
        results = []
        for result in search_results["results"]:
            # Remove MongoDB metadata fields
            receipt_data = result["receipt"]
            if "_id" in receipt_data:
                del receipt_data["_id"]
            if "created_at" in receipt_data:
                del receipt_data["created_at"]
            if "updated_at" in receipt_data:
                del receipt_data["updated_at"]
            if "receipt_id" in receipt_data:
                del receipt_data["receipt_id"]

            results.append(
                SearchResult(
                    receipt_id=result["receipt_id"],
                    score=result["score"],
                    receipt=Receipt(**receipt_data),
                    highlights=result.get("highlights"),
                )
            )

        return SearchResponse(
            total=search_results["total"], results=results, query=search_query
        )

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/receipts/{receipt_id}", response_model=Receipt)
async def get_receipt(receipt_id: str):
    """
    Get single receipt by ID.

    Returns full receipt details including transaction info, items, and totals.
    """
    try:
        receipt_data = await mongodb_service.get_receipt(receipt_id)

        if not receipt_data:
            raise HTTPException(status_code=404, detail="Receipt not found")

        # Remove MongoDB metadata
        if "_id" in receipt_data:
            del receipt_data["_id"]
        if "created_at" in receipt_data:
            del receipt_data["created_at"]
        if "updated_at" in receipt_data:
            del receipt_data["updated_at"]

        return Receipt(**receipt_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve receipt: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve receipt: {str(e)}"
        )


@router.get("/receipts")
async def list_receipts(
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
):
    """
    List all receipts with pagination.

    Returns receipts sorted by creation date (newest first).
    """
    try:
        receipts = await mongodb_service.get_all_receipts(skip=skip, limit=limit)
        total = await mongodb_service.count_receipts()

        # Remove MongoDB metadata from receipts
        cleaned_receipts = []
        for receipt in receipts:
            receipt_id = receipt.pop("_id", None)
            receipt.pop("created_at", None)
            receipt.pop("updated_at", None)
            cleaned_receipts.append(
                {"receipt_id": receipt_id, "receipt": Receipt(**receipt)}
            )

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "receipts": cleaned_receipts,
        }

    except Exception as e:
        logger.error(f"Failed to list receipts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to list receipts: {str(e)}"
        )
