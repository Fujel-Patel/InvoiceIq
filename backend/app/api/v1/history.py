from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional

from backend.app.models.invoice import HistoryItem
from backend.app.services.db import DatabaseService
from backend.app.utils.auth import get_current_user

router = APIRouter()


def get_user_id(current_user: dict) -> str:
    """Extract user_id from current_user dict."""
    return current_user["sub"]


@router.get("/history", response_model=List[HistoryItem])
async def get_user_history(
    user_id: Optional[str] = Query(None, description="User ID to fetch history for"),
    db_service: DatabaseService = Depends(),
    current_user: dict = Depends(get_current_user),
) -> List[HistoryItem]:
    """
    Get extraction history for a user.

    Args:
        user_id: Optional user ID (if not provided, uses current user)
        db_service: Service for database operations
        current_user: Authenticated user info

    Returns:
        List of HistoryItem objects representing the user's extraction history
    """
    current_user_id = get_user_id(current_user)

    # If user_id is not provided, use the current user's ID
    target_user_id = user_id if user_id is not None else current_user_id

    # For security, users can only access their own history
    if target_user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's history",
        )

    # Get history from database
    history_records = await db_service.get_user_history(target_user_id)

    # Convert to HistoryItem objects
    history_items = []
    for record in history_records:
        extracted_data = record.get("full_data") or record.get("extracted_data", {})
        total_amount = (
            extracted_data.get("total_amount")
            if extracted_data.get("total_amount") is not None
            else record.get("total_amount")
        )
        amount_paid = (
            extracted_data.get("amount_paid")
            if extracted_data.get("amount_paid") is not None
            else record.get("amount_paid")
        )
        amount_paid = float(amount_paid) if amount_paid is not None else 0.0
        balance_due = (
            max(0.0, float(total_amount) - amount_paid) if total_amount is not None else None
        )
        history_item = HistoryItem(
            extraction_id=record["id"],
            filename=record["filename"],
            extracted_at=record.get("created_at", ""),
            vendor_name=extracted_data.get("vendor_name") or record.get("vendor_name"),
            total_amount=total_amount,
            amount_paid=round(amount_paid, 2) if amount_paid else None,
            balance_due=round(balance_due, 2) if balance_due is not None else None,
            status=record.get("status", "unknown"),
        )
        history_items.append(history_item)

    return history_items