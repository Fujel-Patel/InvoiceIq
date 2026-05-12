from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class ExtractedInvoice(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    line_items: List[LineItem] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None


class ExtractionResponse(BaseModel):
    extraction_id: str
    status: str  # "success" | "partial" | "failed"
    data: ExtractedInvoice
    raw_text: Optional[str] = None


class HistoryItem(BaseModel):
    extraction_id: str
    filename: str
    extracted_at: str
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    status: str


class ExportRequest(BaseModel):
    extraction_id: str
    format: str  # "csv" | "excel"