"""Pydantic models for receipt data."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WarrantyDetails(BaseModel):
    """Warranty information for high-value items."""

    coverage: str = Field(
        ..., min_length=1, description="Description of warranty coverage"
    )
    requirements: str = Field(
        ..., min_length=1, description="Requirements to maintain warranty"
    )
    source_url: str = Field(
        ..., min_length=1, description="URL to warranty information"
    )


class Item(BaseModel):
    """Individual item on receipt."""

    upc: str = Field(..., min_length=1, description="Universal Product Code")
    product_name: str = Field(..., min_length=1, description="Name of the product")
    quantity: float = Field(..., gt=0, description="Quantity purchased")
    unit_price: float = Field(..., ge=0, description="Price per unit")
    total_price: float = Field(..., ge=0, description="Total price for this item")
    serial_number: str = Field(..., min_length=1, description="Serial or SKU number")
    warranty_details: Optional[WarrantyDetails] = Field(
        None, description="Warranty info for items >= $100"
    )


class TransactionInfo(BaseModel):
    """Transaction metadata."""

    store_name: str = Field(..., min_length=1, description="Name of the store")
    store_address: str = Field(..., min_length=1, description="Store address")
    store_phone: str = Field(..., min_length=1, description="Store phone number")
    date_purchased: str = Field(..., min_length=1, description="Date of purchase")
    time_purchased: str = Field(..., min_length=1, description="Time of purchase")
    cashier: str = Field(..., min_length=1, description="Cashier name or ID")
    transaction_id: str = Field(
        ..., min_length=1, description="Unique transaction identifier"
    )


class Totals(BaseModel):
    """Receipt totals."""

    subtotal: float = Field(..., ge=0, description="Subtotal before tax")
    sales_tax: float = Field(..., ge=0, description="Sales tax amount")
    grand_total: float = Field(..., ge=0, description="Final total amount")


class PaymentInfo(BaseModel):
    """Payment information."""

    card_type: str = Field(..., min_length=1, description="Type of card used")
    card_last_four: str = Field(
        ..., min_length=1, description="Last four digits of card"
    )
    auth_code: str = Field(..., min_length=1, description="Authorization code")


class ReturnPolicy(BaseModel):
    """Return policy details."""

    policy_id: str = Field(..., min_length=1, description="Policy identifier")
    return_window_days: float = Field(
        ..., gt=0, description="Number of days for returns"
    )
    policy_expiration_date: str = Field(
        ..., min_length=1, description="Policy expiration date"
    )
    notes: str = Field(..., min_length=1, description="Additional policy notes")


class Receipt(BaseModel):
    """Complete receipt structure."""

    transaction_info: TransactionInfo
    items: List[Item] = Field(..., min_length=1)
    totals: Totals
    payment_info: PaymentInfo
    return_policy: ReturnPolicy


class ReceiptDocument(Receipt):
    """Receipt with MongoDB metadata."""

    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Document creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Document update timestamp"
    )

    class Config:
        populate_by_name = True


class UploadResponse(BaseModel):
    """Response from file upload."""

    success: bool = Field(..., description="Whether upload was successful")
    receipt_id: Optional[str] = Field(None, description="MongoDB receipt ID")
    receipt: Optional[Receipt] = Field(None, description="Analyzed receipt data")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")


class SearchQuery(BaseModel):
    """Search query parameters."""

    q: Optional[str] = Field(None, description="Search query text")
    store: Optional[str] = Field(None, description="Filter by store name")
    date_from: Optional[str] = Field(None, description="Start date filter (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="End date filter (YYYY-MM-DD)")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    skip: int = Field(0, ge=0, description="Number of results to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum results to return")


class SearchResult(BaseModel):
    """Search result item."""

    receipt_id: str = Field(..., description="Receipt document ID")
    score: float = Field(..., description="Search relevance score")
    receipt: Receipt = Field(..., description="Receipt data")
    highlights: Optional[dict] = Field(None, description="Search term highlights")


class SearchResponse(BaseModel):
    """Search results response."""

    total: int = Field(..., ge=0, description="Total matching results")
    results: List[SearchResult] = Field(..., description="List of search results")
    query: SearchQuery = Field(..., description="Original search query")
