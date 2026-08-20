from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    AuthTokensResponse,
    AuthMeResponse,
    MessageResponse,
)
from backend.app.services.auth_service import (
    signup,
    login,
    refresh_tokens,
    logout,
    logout_all,
    get_current_user,
    forgot_password,
    reset_password,
    change_password,
    AuthError,
)

router = APIRouter()
security = HTTPBearer(auto_error=False)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set HttpOnly cookies for access and refresh tokens."""
    secure = not settings.IS_DEVELOPMENT
    samesite = "none" if secure else "lax"
    # Access token cookie (15 minutes)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )
    # Refresh token cookie (7 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear auth cookies."""
    secure = not settings.IS_DEVELOPMENT
    samesite = "none" if secure else "lax"
    response.delete_cookie(key="access_token", path="/", httponly=True, secure=secure, samesite=samesite)
    response.delete_cookie(key="refresh_token", path="/", httponly=True, secure=secure, samesite=samesite)


async def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Get access token from Authorization header or cookie."""
    if credentials:
        return credentials.credentials
    return request.cookies.get("access_token")


async def get_refresh_token_from_cookie(request: Request) -> Optional[str]:
    """Get refresh token from cookie."""
    return request.cookies.get("refresh_token")


@router.post("/auth/signup", response_model=AuthTokensResponse, status_code=status.HTTP_201_CREATED)
async def signup_endpoint(
    request: Request,
    response: Response,
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthTokensResponse:
    """Register a new user and return tokens."""
    try:
        user = await signup(db, str(payload.email), payload.password)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # Create tokens for the new user
    access_token = ""
    refresh_token = ""
    try:
        from backend.app.services.token_service import create_access_token, create_refresh_token, store_refresh_token
        access_token = create_access_token(user.id, user.email)
        refresh_token = create_refresh_token()
        await store_refresh_token(db, user.id, refresh_token)
    except Exception:
        # If token creation fails, still return success for signup
        # User will need to login
        pass

    if access_token and refresh_token:
        set_auth_cookies(response, access_token, refresh_token)

    return AuthTokensResponse(
        access_token=access_token or "",
        refresh_token=refresh_token or "",
    )


@router.post("/auth/login", response_model=AuthTokensResponse)
async def login_endpoint(
    request: Request,
    response: Response,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthTokensResponse:
    """Authenticate a user and return tokens."""
    try:
        tokens = await login(
            db,
            str(payload.email),
            payload.password,
            request.headers.get("user-agent"),
            request.client.host if request.client else None,
        )
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)

    return AuthTokensResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/auth/refresh", response_model=AuthTokensResponse)
async def refresh_endpoint(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthTokensResponse:
    """Rotate refresh token and issue new access token."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        try:
            body = await request.json()
            if isinstance(body, dict):
                refresh_token = body.get("refresh_token")
        except Exception:
            pass

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided",
        )

    try:
        tokens = await refresh_tokens(
            db,
            refresh_token,
            request.headers.get("user-agent"),
            request.client.host if request.client else None,
        )
    except AuthError as e:
        clear_auth_cookies(response)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)

    return AuthTokensResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/auth/logout", response_model=MessageResponse)
async def logout_endpoint(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke refresh token and clear cookies."""
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await logout(db, refresh_token)

    clear_auth_cookies(response)
    return MessageResponse(message="Logged out successfully")


async def get_current_user_dependency(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_request)
) -> dict:
    """Wrapper dependency for get_current_user to avoid FastAPI response model issues."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "sub": str(user.id),
        "email": user.email,
        "email_confirmed": user.email_confirmed,
    }


@router.post("/auth/logout-all", response_model=MessageResponse)
async def logout_all_endpoint(
    response: Response,
    current_user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke all refresh tokens for the current user."""
    user_id = UUID(current_user["sub"])
    await logout_all(db, user_id)
    clear_auth_cookies(response)
    return MessageResponse(message="Logged out from all devices")


@router.post("/auth/forgot-password", response_model=MessageResponse)
async def forgot_password_endpoint(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Request a password reset email."""
    await forgot_password(db, str(payload.email))
    return MessageResponse(
        message="If an account exists for this email, a password reset link has been sent."
    )


@router.post("/auth/reset-password", response_model=MessageResponse)
async def reset_password_endpoint(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Reset password using a reset token."""
    try:
        await reset_password(db, payload.token, payload.password)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return MessageResponse(message="Password updated successfully. You can now sign in.")


@router.post("/auth/change-password", response_model=MessageResponse)
async def change_password_endpoint(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Change password for authenticated user."""
    user_id = UUID(current_user["sub"])
    try:
        await change_password(db, user_id, payload.current_password, payload.new_password)
    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    return MessageResponse(message="Password changed successfully. Please log in again.")


@router.get("/auth/me", response_model=AuthMeResponse)
async def me_endpoint(
    current_user: dict = Depends(get_current_user_dependency),
) -> AuthMeResponse:
    """Return the authenticated user's profile."""
    return AuthMeResponse(
        user={
            "id": current_user["sub"],
            "email": current_user["email"],
            "email_confirmed": current_user.get("email_confirmed", False),
        }
    )