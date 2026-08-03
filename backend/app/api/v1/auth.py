from __future__ import annotations

from typing import Optional

import httpx
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from loguru import logger

from backend.app.core.config import settings
from backend.app.utils.auth import get_current_user, security

router = APIRouter()


async def _revoke_supabase_session(access_token: str) -> None:
    """Best-effort revocation of the Supabase session. Never raises."""
    if settings.IS_DEVELOPMENT or not access_token:
        return

    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/logout"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json={})
            response.raise_for_status()
    except Exception as e:
        logger.warning(f"Supabase session revoke failed (non-fatal): {e}")


@router.post("/auth/logout")
async def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    current_user: str = Depends(get_current_user),
) -> dict:
    """Log out the current user by revoking the Supabase session (best-effort)."""
    access_token = credentials.credentials if credentials else ""
    await _revoke_supabase_session(access_token)
    logger.info(f"User logged out: {current_user}")
    return {"status": "success", "message": "Logged out successfully"}
