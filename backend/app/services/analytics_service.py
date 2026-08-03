from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.app.models.analytics import (
    AnalyticsBill,
    AnalyticsPeriod,
    AnalyticsResponse,
    AnalyticsSummary,
    AnalyticsVendor,
)


def _to_float(value: Any) -> float:
    """Safely coerce a value to a float, defaulting to 0.0."""
    try:
        return float(value) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    """Parse a date string using common formats. Returns None if unparseable."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d %b %Y",
        "%b %d, %Y",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _record_date(record: Dict[str, Any]) -> datetime:
    """Best-effort date for grouping: invoice_date, then created_at, then now."""
    dt = _parse_date(record.get("invoice_date")) or _parse_date(record.get("created_at"))
    return dt if dt is not None else datetime.now()


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _week_key(dt: datetime) -> str:
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _entry_type(record: Dict[str, Any]) -> str:
    entry_type = record.get("entry_type")
    if not entry_type:
        full_data = record.get("full_data")
        if isinstance(full_data, dict):
            entry_type = full_data.get("entry_type")
    return "credit" if entry_type == "credit" else "debit"


def _amount_paid(record: Dict[str, Any]) -> float:
    amount_paid = record.get("amount_paid")
    if amount_paid is None:
        full_data = record.get("full_data")
        if isinstance(full_data, dict):
            amount_paid = full_data.get("amount_paid")
    return _to_float(amount_paid)


def _payment_status(total: float, paid: float) -> str:
    if total <= 0:
        return "unpaid"
    if paid >= total:
        return "paid"
    if paid > 0:
        return "partial"
    return "unpaid"


def _dominant_currency(records: List[Dict[str, Any]]) -> str:
    counts: Dict[str, int] = defaultdict(int)
    for record in records:
        currency = record.get("currency")
        if currency:
            counts[str(currency).upper()] += 1
    if not counts:
        return "INR"
    return max(counts.items(), key=lambda item: item[1])[0]


def build_analytics(records: List[Dict[str, Any]]) -> AnalyticsResponse:
    """Aggregate extraction records into an AnalyticsResponse."""
    bills: List[AnalyticsBill] = []
    debit_total = 0.0
    credit_total = 0.0
    tax_total = 0.0
    collected_total = 0.0
    outstanding_total = 0.0
    paid_bills = 0
    outstanding_bills = 0
    vendor_totals: Dict[str, float] = defaultdict(float)
    vendor_counts: Dict[str, int] = defaultdict(int)
    monthly_totals: Dict[str, float] = defaultdict(float)
    monthly_counts: Dict[str, int] = defaultdict(int)
    weekly_totals: Dict[str, float] = defaultdict(float)
    weekly_counts: Dict[str, int] = defaultdict(int)

    for record in records:
        total = _to_float(record.get("total_amount"))
        entry_type = _entry_type(record)
        if entry_type == "credit":
            credit_total += abs(total)
        else:
            debit_total += abs(total)
        tax_total += _to_float(record.get("tax"))

        amount_paid = max(0.0, _amount_paid(record))
        balance_due = max(0.0, abs(total) - amount_paid)
        collected_total += min(amount_paid, abs(total))
        outstanding_total += balance_due
        payment_status = _payment_status(abs(total), amount_paid)
        if payment_status == "paid":
            paid_bills += 1
        elif balance_due > 0:
            outstanding_bills += 1

        vendor = record.get("vendor_name") or "Unknown"
        vendor_totals[vendor] += abs(total)
        vendor_counts[vendor] += 1

        date = _record_date(record)
        month_key = _month_key(date)
        week_key = _week_key(date)
        monthly_totals[month_key] += abs(total)
        monthly_counts[month_key] += 1
        weekly_totals[week_key] += abs(total)
        weekly_counts[week_key] += 1

        bills.append(
            AnalyticsBill(
                extraction_id=str(record.get("id", "")),
                filename=record.get("filename", ""),
                vendor_name=record.get("vendor_name"),
                invoice_number=record.get("invoice_number"),
                invoice_date=record.get("invoice_date"),
                due_date=record.get("due_date"),
                subtotal=record.get("subtotal"),
                tax=record.get("tax"),
                total_amount=record.get("total_amount"),
                currency=record.get("currency"),
                entry_type=entry_type,
                amount_paid=round(amount_paid, 2) if amount_paid else None,
                balance_due=round(balance_due, 2),
                payment_status=payment_status,
                status=record.get("status", "unknown"),
                extracted_at=str(record.get("created_at", "")),
            )
        )

    monthly_list: List[AnalyticsPeriod] = [
        AnalyticsPeriod(period=key, total=round(monthly_totals[key], 2), count=monthly_counts[key])
        for key in sorted(monthly_totals)
    ]
    weekly_list: List[AnalyticsPeriod] = [
        AnalyticsPeriod(period=key, total=round(weekly_totals[key], 2), count=weekly_counts[key])
        for key in sorted(weekly_totals)
    ]
    vendor_list: List[AnalyticsVendor] = [
        AnalyticsVendor(vendor=key, total=round(total, 2), count=vendor_counts[key])
        for key, total in sorted(vendor_totals.items(), key=lambda item: item[1], reverse=True)
    ]

    currency = _dominant_currency(records)
    combined_total = round(debit_total + credit_total, 2)
    debit_rounded = round(debit_total, 2)
    credit_rounded = round(credit_total, 2)

    return AnalyticsResponse(
        summary=AnalyticsSummary(
            total_invoices=len(bills),
            total_debit=debit_rounded,
            total_credit=credit_rounded,
            combined_total=combined_total,
            net_total=round(debit_rounded - credit_rounded, 2),
            total_tax=round(tax_total, 2),
            avg_amount=round(debit_rounded / len(bills), 2) if bills else 0.0,
            unique_vendors=len(vendor_totals),
            currency=currency,
            total_collected=round(collected_total, 2),
            total_outstanding=round(outstanding_total, 2),
            paid_bills=paid_bills,
            outstanding_bills=outstanding_bills,
        ),
        monthly=monthly_list,
        weekly=weekly_list,
        vendors=vendor_list,
        bills=bills,
    )
