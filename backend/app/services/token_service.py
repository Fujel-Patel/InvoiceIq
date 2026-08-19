from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from backend.app.core.config import settings
from backend.app.models.refresh_token import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


def create_access_token(user_id: uuid.UUID, email: str) -> str:
    """Create a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token() -> str:
    """Create a cryptographically secure random refresh token."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token for storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate an access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


async def store_refresh_token(
    db: AsyncSession,
    user_id: uuid.UUID,
    token: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> RefreshToken:
    """Store a hashed refresh token in the database."""
    token_hash = hash_refresh_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def validate_refresh_token(
    db: AsyncSession,
    token: str
) -> Optional[RefreshToken]:
    """Validate a refresh token and return the token record if valid."""
    token_hash = hash_refresh_token(token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        return None

    if not refresh_token.is_valid:
        return None

    return refresh_token


async def revoke_refresh_token(
    db: AsyncSession,
    token: str
) -> bool:
    """Revoke a refresh token."""
    token_hash = hash_refresh_token(token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    refresh_token = result.scalar_one_or_none()

    if not refresh_token:
        return False

    refresh_token.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def revoke_all_user_refresh_tokens(
    db: AsyncSession,
    user_id: uuid.UUID
) -> int:
    """Revoke all refresh tokens for a user."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        )
    )
    tokens = result.scalars().all()
    count = 0
    for token in tokens:
        token.revoked_at = datetime.now(timezone.utc)
        count += 1
    await db.commit()
    return count


async def rotate_refresh_token(
    db: AsyncSession,
    old_token: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Optional[tuple[str, RefreshToken]]:
    """Rotate a refresh token: revoke old, create new."""
    refresh_token = await validate_refresh_token(db, old_token)
    if not refresh_token:
        return None

    # Revoke old token
    refresh_token.revoked_at = datetime.now(timezone.utc)

    # Create new token
    new_token = create_refresh_token()
    new_refresh_token = await store_refresh_token(
        db,
        refresh_token.user_id,
        new_token,
        user_agent,
        ip_address
    )

    await db.commit()
    return new_token, new_refresh_token