from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from dataclasses import dataclass

from jose import jwt, JWTError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.services.password_service import hash_password, verify_password
from backend.app.services.token_service import (
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens,
    rotate_refresh_token,
)
from backend.app.services.email_service import send_password_reset_email


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


@dataclass
class AuthUser:
    id: uuid.UUID
    email: str
    email_confirmed: bool


class AuthError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


async def signup(
    db: AsyncSession,
    email: str,
    password: str
) -> AuthUser:
    """Register a new user."""
    email = email.strip().lower()

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise AuthError(409, "An account with this email already exists. Please log in instead.")

    # Create user
    password_hash = hash_password(password)
    user = User(
        email=email,
        password_hash=password_hash,
        email_confirmed_at=datetime.now(timezone.utc),  # Auto-confirm for now
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return AuthUser(
        id=user.id,
        email=user.email,
        email_confirmed=user.email_confirmed_at is not None,
    )


async def login(
    db: AsyncSession,
    email: str,
    password: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuthTokens:
    """Authenticate a user and return tokens."""
    email = email.strip().lower()

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise AuthError(401, "Invalid email or password.")

    # Create tokens
    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token()

    # Store refresh token
    await store_refresh_token(db, user.id, refresh_token, user_agent, ip_address)

    return AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_tokens(
    db: AsyncSession,
    refresh_token: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuthTokens:
    """Rotate refresh token and issue new access token."""
    result = await rotate_refresh_token(db, refresh_token, user_agent, ip_address)
    if not result:
        raise AuthError(401, "Invalid or expired refresh token.")

    new_refresh_token, _ = result

    # Get user for new access token
    user_result = await db.execute(select(User).where(User.id == _.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise AuthError(401, "User not found.")

    new_access_token = create_access_token(user.id, user.email)

    return AuthTokens(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


async def logout(
    db: AsyncSession,
    refresh_token: str
) -> bool:
    """Revoke a refresh token (logout)."""
    return await revoke_refresh_token(db, refresh_token)


async def logout_all(
    db: AsyncSession,
    user_id: uuid.UUID
) -> int:
    """Revoke all refresh tokens for a user (logout from all devices)."""
    return await revoke_all_user_refresh_tokens(db, user_id)


async def get_current_user(
    db: AsyncSession,
    access_token: str
) -> Optional[AuthUser]:
    """Validate access token and return user."""
    from backend.app.services.token_service import decode_access_token

    payload = decode_access_token(access_token)
    if not payload:
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    return AuthUser(
        id=user.id,
        email=user.email,
        email_confirmed=user.email_confirmed_at is not None,
    )


async def forgot_password(
    db: AsyncSession,
    email: str
) -> None:
    """Request a password reset email. Always succeeds to avoid enumeration."""
    email = email.strip().lower()

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # Generate reset token (in production, store hashed in DB with expiry)
        reset_token = secrets.token_urlsafe(32)
        # TODO: Store reset token in DB with expiry
        # For now, we'll use a simple approach with JWT
        reset_payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "password_reset",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        reset_token = jwt.encode(reset_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        # Send email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        await send_password_reset_email(user.email, reset_url)


async def reset_password(
    db: AsyncSession,
    token: str,
    new_password: str
) -> bool:
    """Reset password using a reset token."""

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            raise AuthError(400, "Invalid reset token.")
    except JWTError:
        raise AuthError(400, "Invalid or expired reset token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthError(400, "Invalid reset token.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthError(400, "Invalid reset token.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthError(400, "Invalid reset token.")

    # Update password
    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)

    # Revoke all existing refresh tokens (force re-login)
    await revoke_all_user_refresh_tokens(db, user_id)

    await db.commit()
    return True


async def change_password(
    db: AsyncSession,
    user_id: uuid.UUID,
    current_password: str,
    new_password: str
) -> bool:
    """Change password for authenticated user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthError(404, "User not found.")

    if not verify_password(current_password, user.password_hash):
        raise AuthError(401, "Current password is incorrect.")

    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc)

    # Revoke all existing refresh tokens (force re-login)
    await revoke_all_user_refresh_tokens(db, user_id)

    await db.commit()
    return True