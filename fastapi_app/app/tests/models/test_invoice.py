from __future__ import annotations

from fastapi_app.app.models.invoice import (
    LineItem,
    ExtractedInvoice,
    ExtractionResponse,
    HistoryItem,
    ExportRequest
)


def test_line_item_creation():
    """Test LineItem model creation with optional fields"""
    item = LineItem(description="Test Item")
    assert item.description == "Test Item"
    assert item.quantity is None
    assert item.unit_price is None
    assert item.total is None

    # Test with values
    item_with_values = LineItem(
        description="Test Item",
        quantity=2.0,
        unit_price=10.0,
        total=20.0
    )
    assert item_with_values.quantity == 2.0
    assert item_with_values.unit_price == 10.0
    assert item_with_values.total == 20.0


def test_extracted_invoice_creation():
    """Test ExtractedInvoice model creation"""
    invoice = ExtractedInvoice()
    assert invoice.vendor_name is None
    assert invoice.invoice_number is None
    assert invoice.line_items == []

    # Test with values
    line_item = LineItem(description="Test Item", quantity=1.0, unit_price=5.0, total=5.0)
    invoice_with_data = ExtractedInvoice(
        vendor_name="Test Vendor",
        invoice_number="INV-001",
        invoice_date="2026-01-15",
        due_date="2026-02-15",
        line_items=[line_item],
        subtotal=5.0,
        tax=0.5,
        total_amount=5.5,
        currency="USD"
    )
    assert invoice_with_data.vendor_name == "Test Vendor"
    assert invoice_with_data.invoice_number == "INV-001"
    assert len(invoice_with_data.line_items) == 1
    assert invoice_with_data.line_items[0].description == "Test Item"
    assert invoice_with_data.total_amount == 5.5
    assert invoice_with_data.currency == "USD"


def test_extraction_response():
    """Test ExtractionResponse model"""
    line_item = LineItem(description="Test Item")
    invoice = ExtractedInvoice(line_items=[line_item])
    response = ExtractionResponse(
        extraction_id="test-id-123",
        status="success",
        data=invoice,
        raw_text="Some raw text"
    )
    assert response.extraction_id == "test-id-123"
    assert response.status == "success"
    assert response.data == invoice
    assert response.raw_text == "Some raw text"


def test_history_item():
    """Test HistoryItem model"""
    history = HistoryItem(
        extraction_id="hist-123",
        filename="test.pdf",
        extracted_at="2026-01-15T10:30:00Z",
        vendor_name="Test Vendor",
        total_amount=100.0,
        status="success"
    )
    assert history.extraction_id == "hist-123"
    assert history.filename == "test.pdf"
    assert history.vendor_name == "Test Vendor"
    assert history.total_amount == 100.0
    assert history.status == "success"


def test_export_request():
    """Test ExportRequest model"""
    export_csv = ExportRequest(
        extraction_ids=["ext-123"],
        format="csv"
    )
    assert export_csv.extraction_ids == ["ext-123"]
    assert export_csv.format == "csv"

    export_excel = ExportRequest(
        extraction_ids=["ext-123", "ext-456"],
        format="excel"
    )
    assert export_excel.extraction_ids == ["ext-123", "ext-456"]
    assert export_excel.format == "excel"