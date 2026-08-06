from __future__ import annotations

from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt  # type: ignore[import-untyped]
from loguru import logger

from backend.app.core.config import settings
from backend.app.models.auth import (
    AuthResponse,
    AuthUser,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MeResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SignupRequest,
    SignupResponse,
)
from backend.app.services.auth_service import (
    AuthError,
    forgot_password as auth_forgot_password,
    login as auth_login,
    reset_password as auth_reset_password,
    signup as auth_signup,
)
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
) -> dict[str, str]:
    """Log out the current user by revoking the Supabase session (best-effort)."""
    access_token = credentials.credentials if credentials else ""
    await _revoke_supabase_session(access_token)
    logger.info(f"User logged out: {current_user}")
    return {"status": "success", "message": "Logged out successfully"}


@router.post("/auth/signup", response_model=SignupResponse, status_code=201)
async def signup(payload: SignupRequest) -> SignupResponse:
    """Create a new account via Supabase GoTrue (admin API)."""
    try:
        user = await auth_signup(str(payload.email), payload.password)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Unable to reach the authentication service.")

    email_confirmed = user.get("email_confirmed_at") is not None
    message = (
        "Account created successfully. You can now sign in."
        if email_confirmed
        else "Account created. Please check your email to confirm your address before signing in."
    )
    logger.info(f"Signup completed for {payload.email}")
    return SignupResponse(
        user_id=str(user.get("id", "")),
        email=str(user.get("email") or payload.email),
        email_confirmed=email_confirmed,
        message=message,
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest) -> AuthResponse:
    """Authenticate a user and return a Supabase session (access + refresh tokens)."""
    try:
        token_data = await auth_login(str(payload.email), payload.password)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Unable to reach the authentication service.")

    user = token_data.get("user") or {}
    return AuthResponse(
        access_token=str(token_data["access_token"]),
        refresh_token=str(token_data.get("refresh_token", "")),
        token_type=str(token_data.get("token_type", "bearer")),
        expires_in=int(token_data.get("expires_in", 3600)),
        user=AuthUser(
            id=str(user.get("id", "")),
            email=str(user.get("email") or payload.email),
        ),
    )


@router.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """Send a password recovery email. Always returns a generic message."""
    try:
        await auth_forgot_password(str(payload.email))
    except AuthError as e:
        # Avoid account enumeration by returning the generic message for known errors.
        if e.status_code < 500:
            return ForgotPasswordResponse(
                message="If an account exists for this email, a password reset link has been sent."
            )
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Unable to reach the authentication service.")
    return ForgotPasswordResponse(
        message="If an account exists for this email, a password reset link has been sent."
    )


@router.post("/auth/reset-password", response_model=ResetPasswordResponse)
async def reset_password(payload: ResetPasswordRequest) -> ResetPasswordResponse:
    """Reset a password using a recovery token."""
    try:
        await auth_reset_password(payload.password, payload.token)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Unable to reach the authentication service.")
    return ResetPasswordResponse(message="Password updated successfully. You can now sign in.")


@router.get("/auth/me", response_model=MeResponse)
async def me(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    current_user: str = Depends(get_current_user),
) -> MeResponse:
    """Return the authenticated user's id and email (decoded from the JWT)."""
    user_id = current_user
    email: Optional[str] = None
    if credentials and jwt is not None:
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            email = payload.get("email")
            sub = payload.get("sub")
            if sub:
                user_id = str(sub)
        except JWTError:
            pass
    return MeResponse(user_id=user_id, email=email)
