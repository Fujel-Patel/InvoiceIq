from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_invoices: int
    total_debit: float
    total_credit: float
    combined_total: float
    net_total: float
    total_tax: float
    avg_amount: float
    unique_vendors: int
    currency: str
    total_collected: float
    total_outstanding: float
    paid_bills: int
    outstanding_bills: int


class AnalyticsPeriod(BaseModel):
    period: str
    total: float
    count: int


class AnalyticsVendor(BaseModel):
    vendor: str
    total: float
    count: int


class AnalyticsBill(BaseModel):
    extraction_id: str
    filename: str
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    entry_type: Optional[str] = None
    amount_paid: Optional[float] = None
    balance_due: float = 0.0
    payment_status: str = "unpaid"
    status: str
    extracted_at: str


class AnalyticsResponse(BaseModel):
    summary: AnalyticsSummary
    monthly: List[AnalyticsPeriod]
    weekly: List[AnalyticsPeriod]
    vendors: List[AnalyticsVendor]
    bills: List[AnalyticsBill]
