from __future__ import annotations

import json
import re
from typing import List, Optional
from datetime import datetime
from ..models.invoice import LineItem, ExtractedInvoice


def parse_llm_response(raw_dict: dict) -> ExtractedInvoice:
    """
    Parse and validate raw invoice data from LLM response.
    Extract JSON cleanly from LLM text and map fields to ExtractedInvoice model.

    Args:
        raw_dict: Dictionary from LLM response (may contain extra text or formatting)

    Returns:
        ExtractedInvoice model instance
    """
    # If raw_dict is already a dictionary, use it directly
    # Otherwise, try to extract JSON from it
    if isinstance(raw_dict, dict):
        data = raw_dict
    else:
        # Try to extract JSON from text
        text = str(raw_dict)
        json_str = _extract_json_from_text(text)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # If we can't parse JSON, return empty model
            data = {}

    # Create ExtractedInvoice instance, handling missing fields gracefully
    return ExtractedInvoice(**data)


def _extract_json_from_text(text: str) -> str:
    """
    Extract JSON from text that might contain markdown or other formatting.

    Args:
        text: Raw text from LLM response

    Returns:
        Clean JSON string
    """
    # Look for JSON block in markdown
    if "```json" in text:
        # Extract JSON from markdown code block
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()

    # Look for any JSON-like content (starts with { and ends with })
    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end != 0 and end > start:
        return text[start:end]

    # If we can't find JSON, return empty object
    return "{}"


def determine_status(data: ExtractedInvoice) -> str:
    """
    Determine the status of an extraction based on which fields are present.

    Args:
        data: ExtractedInvoice instance

    Returns:
        "success" if vendor_name and total_amount present
        "partial" if some fields missing
        "failed" if all fields are null
    """
    # Check if all fields are None/empty
    all_none = True
    for field_name, field_value in data.dict().items():
        if field_value is not None and field_value != [] and field_value != "":
            all_none = False
            break

    if all_none:
        return "failed"

    # Check if required fields for success are present
    if data.vendor_name is not None and data.vendor_name != "":
        if data.total_amount is not None:
            return "success"

    # If we have some fields but not the required ones for success
    return "partial"