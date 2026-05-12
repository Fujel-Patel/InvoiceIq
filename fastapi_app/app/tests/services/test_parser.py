from __future__ import annotations

import json
from fastapi_app.app.services.parser import (
    parse_llm_response,
    determine_status,
    _extract_json_from_text
)
from fastapi_app.app.models.invoice import ExtractedInvoice, LineItem


def test_parse_llm_response_dict():
    """Test parsing when input is already a dictionary"""
    raw_dict = {
        "vendor_name": "Test Store",
        "total_amount": 25.50,
        "line_items": [
            {"description": "Item 1", "quantity": 2, "unit_price": 10.0, "total": 20.0},
            {"description": "Item 2", "quantity": 1, "unit_price": 5.50, "total": 5.50}
        ]
    }

    result = parse_llm_response(raw_dict)
    assert isinstance(result, ExtractedInvoice)
    assert result.vendor_name == "Test Store"
    assert result.total_amount == 25.50
    assert len(result.line_items) == 2


def test_parse_llm_response_json_string():
    """Test parsing when input is a JSON string"""
    raw_dict = '{"vendor_name": "Test Store", "total_amount": 15.0}'

    result = parse_llm_response(raw_dict)
    assert isinstance(result, ExtractedInvoice)
    assert result.vendor_name == "Test Store"
    assert result.total_amount == 15.0


def test_parse_llm_response_markdown_json():
    """Test parsing JSON from markdown code block"""
    raw_dict = '''
    Here is the extracted data:
    ```json
    {
        "vendor_name": "Market Store",
        "invoice_number": "INV-001",
        "total_amount": 42.99
    }
    ```
    '''

    result = parse_llm_response(raw_dict)
    assert isinstance(result, ExtractedInvoice)
    assert result.vendor_name == "Market Store"
    assert result.invoice_number == "INV-001"
    assert result.total_amount == 42.99


def test_parse_llm_response_invalid_json():
    """Test handling of invalid JSON"""
    raw_dict = "This is not JSON at all"

    result = parse_llm_response(raw_dict)
    assert isinstance(result, ExtractedInvoice)
    # Should return empty model
    assert result.vendor_name is None
    assert result.total_amount is None


def test_determine_status_success():
    """Test status determination for successful extraction"""
    line_item = LineItem(description="Test", quantity=1.0, unit_price=10.0, total=10.0)
    data = ExtractedInvoice(
        vendor_name="Test Store",
        total_amount=10.0,
        line_items=[line_item]
    )

    status = determine_status(data)
    assert status == "success"


def test_determine_status_partial():
    """Test status determination for partial extraction"""
    # Has vendor but no total
    data = ExtractedInvoice(vendor_name="Test Store")
    status = determine_status(data)
    assert status == "partial"

    # Has total but no vendor
    data = ExtractedInvoice(total_amount=10.0)
    status = determine_status(data)
    assert status == "partial"


def test_determine_status_failed():
    """Test status determination for failed extraction"""
    data = ExtractedInvoice()  # All fields None/empty
    status = determine_status(data)
    assert status == "failed"


def test_extract_json_from_text():
    """Test JSON extraction from various text formats"""
    # Plain JSON
    text = '{"key": "value"}'
    assert _extract_json_from_text(text) == '{"key": "value"}'

    # JSON in markdown
    text = 'Some text\n```json\n{"key": "value"}\n```\nMore text'
    assert _extract_json_from_text(text) == '{"key": "value"}'

    # JSON-like content
    text = 'Prefix {"nested": {"key": "val"}} Suffix'
    assert _extract_json_from_text(text) == '{"nested": {"key": "val"}}'

    # No JSON found
    text = 'Just plain text here'
    assert _extract_json_from_text(text) == '{}'