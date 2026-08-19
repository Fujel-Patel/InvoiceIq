from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.core.database import get_db_service
from backend.app.models.analytics import AnalyticsResponse
from backend.app.services.analytics_service import build_analytics
from backend.app.services.db import DatabaseService
from backend.app.utils.auth import get_current_user

router = APIRouter()


def get_user_id(current_user: dict) -> str:
    """Extract user_id from current_user dict."""
    return current_user["sub"]


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    db_service: DatabaseService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user),
) -> AnalyticsResponse:
    """
    Get aggregated analytics across all of a user's invoices.

    Args:
        db_service: Service for database operations
        current_user: Authenticated user info

    Returns:
        AnalyticsResponse with debit/credit totals, monthly/weekly breakdowns,
        vendor summaries, and the full list of bills
    """
    user_id = get_user_id(current_user)
    records = await db_service.get_user_history(user_id)
    return build_analytics(records)