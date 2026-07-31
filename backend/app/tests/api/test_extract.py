from __future__ import annotations

# Test that the API imports work correctly
from backend.app.api.v1.extract import router
from backend.app.models.invoice import (
    LineItem,
    ExtractedInvoice,
    ExtractionResponse,
    HistoryItem,
    ExportRequest
)


def test_imports_work():
    """Test that we can import the API routers and models"""
    assert router is not None
    assert LineItem is not None
    assert ExtractedInvoice is not None
    assert ExtractionResponse is not None
    assert HistoryItem is not None
    assert ExportRequest is not None


def test_extraction_response_creation():
    """Test creating an ExtractionResponse"""
    line_item = LineItem(description="Test Item", quantity=2.0, unit_price=5.0, total=10.0)
    invoice = ExtractedInvoice(
        vendor_name="Test Vendor",
        total_amount=10.0,
        line_items=[line_item]
    )

    response = ExtractionResponse(
        extraction_id="test-123",
        status="success",
        data=invoice
    )

    assert response.extraction_id == "test-123"
    assert response.status == "success"
    assert response.data.vendor_name == "Test Vendor"
    assert len(response.data.line_items) == 1