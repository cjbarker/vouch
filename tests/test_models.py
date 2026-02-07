"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models import (
    Item,
    PaymentInfo,
    Receipt,
    ReturnPolicy,
    SearchQuery,
    SearchResponse,
    SearchResult,
    Totals,
    TransactionInfo,
    UploadResponse,
    WarrantyDetails,
)


class TestTransactionInfo:
    """Tests for TransactionInfo model."""

    def test_valid_transaction_info(self):
        """Test creating valid transaction info."""
        info = TransactionInfo(
            store_name="Test Store",
            store_address="123 Test St",
            store_phone="555-1234",
            date_purchased="2024-01-15",
            time_purchased="14:30:00",
            cashier="John Doe",
            transaction_id="TX123",
        )
        assert info.store_name == "Test Store"
        assert info.transaction_id == "TX123"
        assert info.cashier == "John Doe"

    def test_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            TransactionInfo(
                store_name="Test Store",
                # Missing other required fields
            )


class TestWarrantyDetails:
    """Tests for WarrantyDetails model."""

    def test_valid_warranty(self):
        """Test creating valid warranty details."""
        warranty = WarrantyDetails(
            coverage="12 months manufacturer warranty",
            requirements="Original receipt required",
            source_url="https://example.com/warranty",
        )
        assert warranty.coverage == "12 months manufacturer warranty"
        assert warranty.source_url == "https://example.com/warranty"

    def test_required_fields(self):
        """Test that all warranty fields are required."""
        with pytest.raises(ValidationError):
            WarrantyDetails(
                coverage="12 months",
                # Missing requirements and source_url
            )


class TestItem:
    """Tests for Item model."""

    def test_valid_item(self):
        """Test creating valid item."""
        item = Item(
            upc="123456789012",
            product_name="Test Product",
            quantity=2,
            unit_price=10.00,
            total_price=20.00,
            serial_number="SN123",
        )
        assert item.upc == "123456789012"
        assert item.quantity == 2
        assert item.total_price == 20.00
        assert item.serial_number == "SN123"

    def test_item_with_warranty(self):
        """Test item with warranty details."""
        warranty = WarrantyDetails(
            coverage="12 months warranty",
            requirements="Receipt required",
            source_url="https://example.com/warranty",
        )
        item = Item(
            upc="123456789012",
            product_name="Expensive Item",
            quantity=1,
            unit_price=150.00,
            total_price=150.00,
            serial_number="SN456",
            warranty_details=warranty,
        )
        assert item.warranty_details is not None
        assert item.warranty_details.coverage == "12 months warranty"

    def test_required_fields(self):
        """Test that serial_number is required."""
        with pytest.raises(ValidationError):
            Item(
                upc="123456789012",
                product_name="Test Product",
                quantity=1,
                unit_price=10.00,
                total_price=10.00,
                # Missing serial_number
            )


class TestTotals:
    """Tests for Totals model."""

    def test_valid_totals(self):
        """Test creating valid totals."""
        totals = Totals(
            subtotal=100.00,
            sales_tax=8.00,
            grand_total=108.00,
        )
        assert totals.subtotal == 100.00
        assert totals.sales_tax == 8.00
        assert totals.grand_total == 108.00


class TestPaymentInfo:
    """Tests for PaymentInfo model."""

    def test_valid_payment_info(self):
        """Test creating valid payment info."""
        payment = PaymentInfo(
            card_type="Visa",
            card_last_four="1234",
            auth_code="AUTH123",
        )
        assert payment.card_type == "Visa"
        assert payment.card_last_four == "1234"
        assert payment.auth_code == "AUTH123"

    def test_all_fields_required(self):
        """Test all payment fields are required."""
        with pytest.raises(ValidationError):
            PaymentInfo(card_type="Visa")


class TestReturnPolicy:
    """Tests for ReturnPolicy model."""

    def test_valid_return_policy(self):
        """Test creating valid return policy."""
        policy = ReturnPolicy(
            policy_id="RP001",
            return_window_days=30,
            policy_expiration_date="2024-02-14",
            notes="Receipt required",
        )
        assert policy.policy_id == "RP001"
        assert policy.return_window_days == 30
        assert policy.notes == "Receipt required"


class TestReceipt:
    """Tests for Receipt model."""

    def test_valid_receipt(self, sample_receipt_data):
        """Test creating valid receipt."""
        receipt = Receipt(**sample_receipt_data)
        assert receipt.transaction_info.store_name == "Test Store"
        assert len(receipt.items) == 1
        assert receipt.totals.grand_total == 21.60
        assert receipt.payment_info.card_type == "Visa"

    def test_receipt_validation(self):
        """Test receipt validation with invalid data."""
        with pytest.raises(ValidationError):
            Receipt(
                transaction_info={},  # Missing required fields
                items=[],
                totals={},
                payment_info={},
                return_policy={},
            )


class TestUploadResponse:
    """Tests for UploadResponse model."""

    def test_successful_upload(self, sample_receipt_data):
        """Test successful upload response."""
        receipt = Receipt(**sample_receipt_data)
        response = UploadResponse(
            success=True,
            receipt_id="test123",
            receipt=receipt,
            message="Success",
        )
        assert response.success is True
        assert response.receipt_id == "test123"
        assert response.receipt.transaction_info.store_name == "Test Store"

    def test_failed_upload(self):
        """Test failed upload response."""
        response = UploadResponse(
            success=False,
            message="Upload failed",
            error="Invalid file format",
        )
        assert response.success is False
        assert response.error == "Invalid file format"
        assert response.receipt_id is None


class TestSearchQuery:
    """Tests for SearchQuery model."""

    def test_basic_search(self):
        """Test basic search query."""
        query = SearchQuery(q="Test Store")
        assert query.q == "Test Store"
        assert query.skip == 0
        assert query.limit == 20

    def test_search_with_filters(self):
        """Test search with filters."""
        query = SearchQuery(
            q="Product",
            store="Test Store",
            min_price=10.0,
            max_price=100.0,
            skip=10,
            limit=50,
        )
        assert query.store == "Test Store"
        assert query.min_price == 10.0
        assert query.max_price == 100.0
        assert query.skip == 10
        assert query.limit == 50

    def test_empty_query(self):
        """Test empty search query with defaults."""
        query = SearchQuery()
        assert query.q is None
        assert query.skip == 0
        assert query.limit == 20


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_search_result(self, sample_receipt_data):
        """Test search result."""
        receipt = Receipt(**sample_receipt_data)
        result = SearchResult(
            receipt_id="test123",
            score=0.95,
            receipt=receipt,
        )
        assert result.receipt_id == "test123"
        assert result.score == 0.95
        assert result.receipt.transaction_info.store_name == "Test Store"


class TestSearchResponse:
    """Tests for SearchResponse model."""

    def test_search_response(self, sample_receipt_data):
        """Test search response."""
        receipt = Receipt(**sample_receipt_data)
        result = SearchResult(
            receipt_id="test123",
            score=0.95,
            receipt=receipt,
        )
        query = SearchQuery(q="Test")
        response = SearchResponse(
            total=1,
            results=[result],
            query=query,
        )
        assert response.total == 1
        assert len(response.results) == 1
        assert response.results[0].receipt_id == "test123"
        assert response.query.q == "Test"

    def test_empty_search_response(self):
        """Test empty search response."""
        query = SearchQuery(q="Nonexistent")
        response = SearchResponse(
            total=0,
            results=[],
            query=query,
        )
        assert response.total == 0
        assert len(response.results) == 0
        assert response.query.q == "Nonexistent"
