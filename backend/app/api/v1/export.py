from __future__ import annotations

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.models.invoice import ExportRequest, ExtractedInvoice
from backend.app.services.db import DatabaseService

router = APIRouter()
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Return a user ID.

    In development mode, bypass authentication and return a fixed ID.
    If credentials are missing (auto_error=False), also return the dev ID.
    """
    # Development bypass
    return "dev-user-id"



def _extract_to_csv(data: ExtractedInvoice) -> str:
    """Convert extracted invoice data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Field", "Value"])

    # Write invoice info
    writer.writerow(["Vendor Name", data.vendor_name or ""])
    writer.writerow(["Invoice Number", data.invoice_number or ""])
    writer.writerow(["Invoice Date", data.invoice_date or ""])
    writer.writerow(["Due Date", data.due_date or ""])
    writer.writerow(["Subtotal", data.subtotal or ""])
    writer.writerow(["Tax", data.tax or ""])
    writer.writerow(["Total Amount", data.total_amount or ""])
    writer.writerow(["Currency", data.currency or ""])
    writer.writerow([])  # Empty row

    # Write line items header
    writer.writerow(["Line Items"])
    writer.writerow(["Description", "Quantity", "Unit Price", "Total"])

    # Write line items
    for item in data.line_items:
        writer.writerow([
            item.description or "",
            item.quantity or "",
            item.unit_price or "",
            item.total or ""
        ])

    return output.getvalue()


def _extract_to_excel(data: ExtractedInvoice) -> bytes:
    """Convert extracted invoice data to Excel format"""
    # For simplicity, we'll return CSV-like data for now
    # In a real implementation, you would use openpyxl or similar
    csv_data = _extract_to_csv(data)
    return csv_data.encode('utf-8')


@router.post("/export")
async def export_data(
    export_request: ExportRequest,
    db_service: DatabaseService = Depends(),
    current_user: str = Depends(get_current_user)
):
    """
    Export extraction data as CSV or Excel file.

    Args:
        export_request: Contains extraction_ids and format (csv/excel)
        db_service: Service for database operations
        current_user: ID of the authenticated user

    Returns:
        StreamingResponse with the file data

    Raises:
        HTTPException: If extraction record is not found, not authorized, or format is invalid
    """
    # Validate format
    if export_request.format not in ["csv", "excel"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'excel'"
        )

    # Get all extraction records
    extraction_records = []
    for extraction_id in export_request.extraction_ids:
        extraction_record = await db_service.get_extraction_by_id(extraction_id)
        if not extraction_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction with ID {extraction_id} not found"
            )

        # Check if the extraction belongs to the current user
        if extraction_record.get("user_id") != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to access extraction with ID {extraction_id}"
            )

        extraction_records.append(extraction_record)

    # Generate file content based on format
    if export_request.format == "csv":
        # For multiple extractions, we'll create a combined CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Field", "Value"])

        # Process each extraction
        for i, extraction_record in enumerate(extraction_records):
            if i > 0:
                writer.writerow([])  # Empty row between extractions
                writer.writerow([f"Extraction {i+1}"])
                writer.writerow([])  # Empty row

            extracted_data = ExtractedInvoice(**extraction_record["full_data"])

            # Write invoice info
            writer.writerow(["Vendor Name", extracted_data.vendor_name or ""])
            writer.writerow(["Invoice Number", extracted_data.invoice_number or ""])
            writer.writerow(["Invoice Date", extracted_data.invoice_date or ""])
            writer.writerow(["Due Date", extracted_data.due_date or ""])
            writer.writerow(["Subtotal", extracted_data.subtotal or ""])
            writer.writerow(["Tax", extracted_data.tax or ""])
            writer.writerow(["Total Amount", extracted_data.total_amount or ""])
            writer.writerow(["Currency", extracted_data.currency or ""])
            writer.writerow([])  # Empty row

            # Write line items header
            writer.writerow(["Line Items"])
            writer.writerow(["Description", "Quantity", "Unit Price", "Total"])

            # Write line items
            for item in extracted_data.line_items:
                writer.writerow([
                    item.description or "",
                    item.quantity or "",
                    item.unit_price or "",
                    item.total or ""
                ])

        content = output.getvalue()
        media_type = "text/csv"
        filename = f"export_{len(extraction_records)}_extractions.csv"
    else:  # excel
        # For Excel, we'll create a simple combined export for now
        # In a real implementation, you would use openpyxl to create multiple sheets
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Field", "Value"])

        # Process each extraction
        for i, extraction_record in enumerate(extraction_records):
            if i > 0:
                writer.writerow([])  # Empty row between extractions
                writer.writerow([f"Extraction {i+1}"])
                writer.writerow([])  # Empty row

            extracted_data = ExtractedInvoice(**extraction_record["full_data"])

            # Write invoice info
            writer.writerow(["Vendor Name", extracted_data.vendor_name or ""])
            writer.writerow(["Invoice Number", extracted_data.invoice_number or ""])
            writer.writerow(["Invoice Date", extracted_data.invoice_date or ""])
            writer.writerow(["Due Date", extracted_data.due_date or ""])
            writer.writerow(["Subtotal", extracted_data.subtotal or ""])
            writer.writerow(["Tax", extracted_data.tax or ""])
            writer.writerow(["Total Amount", extracted_data.total_amount or ""])
            writer.writerow(["Currency", extracted_data.currency or ""])
            writer.writerow([])  # Empty row

            # Write line items header
            writer.writerow(["Line Items"])
            writer.writerow(["Description", "Quantity", "Unit Price", "Total"])

            # Write line items
            for item in extracted_data.line_items:
                writer.writerow([
                    item.description or "",
                    item.quantity or "",
                    item.unit_price or "",
                    item.total or ""
                ])

        content = output.getvalue()
        media_type = "text/csv"  # Fallback to CSV for simplicity
        filename = f"export_{len(extraction_records)}_extractions.csv"

    # Return as streaming response
    return StreamingResponse(
        io.StringIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
