from __future__ import annotations

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from ...models.invoice import ExportRequest, ExtractedInvoice
from ...services.db import DatabaseService

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract user ID from JWT token.
    In a real implementation, you would verify the token and extract user info.
    For now, we'll return a mock user ID.
    """
    # TODO: Implement proper JWT verification
    # For development, returning a fixed user ID
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
        export_request: Contains extraction_id and format (csv/excel)
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

    # Get the extraction record
    extraction_record = await db_service.get_extraction_by_id(export_request.extraction_id)

    if not extraction_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction with ID {export_request.extraction_id} not found"
        )

    # Check if the extraction belongs to the current user
    if extraction_record.get("user_id") != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this extraction"
        )

    # Convert the database record to ExtractedInvoice format
    extracted_data = ExtractedInvoice(**extraction_record["extracted_data"])

    # Generate file content based on format
    if export_request.format == "csv":
        content = _extract_to_csv(extracted_data)
        media_type = "text/csv"
        filename = f"extraction_{export_request.extraction_id}.csv"
    else:  # excel
        content = _extract_to_excel(extracted_data)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"extraction_{export_request.extraction_id}.xlsx"

    # Return as streaming response
    return StreamingResponse(
        io.StringIO(content) if export_request.format == "csv" else io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
