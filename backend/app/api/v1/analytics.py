from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.models.analytics import AnalyticsResponse
from backend.app.services.analytics_service import build_analytics
from backend.app.services.db import DatabaseService
from backend.app.utils.auth import get_current_user

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    db_service: DatabaseService = Depends(),
    current_user: str = Depends(get_current_user),
) -> AnalyticsResponse:
    """
    Get aggregated analytics across all of a user's invoices.

    Args:
        db_service: Service for database operations
        current_user: ID of the authenticated user

    Returns:
        AnalyticsResponse with debit/credit totals, monthly/weekly breakdowns,
        vendor summaries, and the full list of bills
    """
    records = await db_service.get_user_history(current_user)
    return build_analytics(records)
