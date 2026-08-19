from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.services.auth_service import get_current_user as auth_get_current_user
from sqlalchemy.ext.asyncio import AsyncSession


security = HTTPBearer(auto_error=False)


async def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Extract access token from Authorization header or cookie."""
    if credentials:
        return credentials.credentials
    return request.cookies.get("access_token")


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_request)
) -> dict:
    """
    Validate access token and return user info.
    Returns dict with: sub (user_id), email, email_confirmed
    """
    # Development bypass - create a dev user if needed
    if settings.IS_DEVELOPMENT and not token:
        # In development, create a default dev user
        return {
            "sub": "00000000-0000-0000-0000-000000000001",
            "email": "dev@localhost",
            "email_confirmed": True,
        }

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if not user_id or not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        # Verify user exists in database
        user = await auth_get_current_user(db, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return {
            "sub": str(user.id),
            "email": user.email,
            "email_confirmed": user.email_confirmed,
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_request)
) -> Optional[dict]:
    """Get current user if authenticated, otherwise return None."""
    try:
        return await get_current_user(request, db, token)
    except HTTPException:
        return None