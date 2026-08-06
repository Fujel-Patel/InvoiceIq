from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, cast

import httpx
from jose import jwt  # type: ignore[import-untyped]
from loguru import logger

from backend.app.core.config import settings

SUPABASE_AUTH_URL: str = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"


@dataclass
class _DevUser:
    id: str
    email: str
    password_hash: str
    salt: str
    email_confirmed_at: str


_dev_users: Dict[str, _DevUser] = {}
_dev_recovery_tokens: Dict[str, str] = {}


def _dev_password_hash(password: str) -> tuple[str, str]:
    """Return (salt, pbkdf2-sha256 hash) for a dev-mode password."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    )
    return salt, digest.hex()


def _dev_password_matches(password: str, salt: str, expected_hash: str) -> bool:
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    )
    return hmac.compare_digest(digest.hex(), expected_hash)


def _dev_issue_access_token(user: _DevUser) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "email": user.email,
        "aud": "authenticated",
        "role": "authenticated",
        "iat": now,
        "exp": now + timedelta(seconds=3600),
    }
    return cast(str, jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256"))


class AuthError(Exception):
    """Raised when Supabase GoTrue returns a structured auth error."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def _headers(api_key: str, token: str | None = None) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "apikey": api_key,
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def map_gotrue_error(status_code: int, body: Dict[str, Any]) -> AuthError:
    """Map a GoTrue error response to a user-friendly HTTP error.

    Handles both the GoTrue `{code, msg}` shape and the OAuth-style
    `{error, error_description}` shape returned by the token endpoint.
    """
    code = str(body.get("code") or body.get("error") or "").lower()
    message = str(
        body.get("msg")
        or body.get("error_description")
        or body.get("message")
        or "Authentication failed"
    ).lower()

    if "user_already_exists" in code or "already registered" in message:
        return AuthError(409, "An account with this email already exists. Please log in instead.")
    if "email_not_confirmed" in code:
        return AuthError(403, "Please verify your email address before signing in.")
    if (
        "invalid_credentials" in code
        or "invalid_grant" in code
        or "invalid login credentials" in message
    ):
        return AuthError(401, "Invalid email or password.")
    if status_code == 422 or "weak_password" in code:
        return AuthError(
            422,
            "Password does not meet the requirements. Use at least 8 characters "
            "with a mix of uppercase, lowercase, and numbers.",
        )
    if status_code == 429:
        return AuthError(429, "Too many attempts. Please wait a moment and try again.")
    if status_code in (502, 503):
        return AuthError(502, "Authentication service is temporarily unavailable. Please try again.")
    if status_code >= 500:
        return AuthError(502, "Something went wrong on our end. Please try again.")
    return AuthError(status_code, message.capitalize() or "Authentication failed.")


async def _request(
    method: str,
    path: str,
    api_key: str,
    token: str | None = None,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    url = f"{SUPABASE_AUTH_URL}/{path}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(
                method,
                url,
                headers=_headers(api_key, token),
                json=payload,
            )
    except httpx.HTTPError as e:
        logger.error(f"GoTrue request failed for {url}: {e}")
        raise AuthError(502, "Authentication service is temporarily unavailable. Please try again.")

    if response.status_code >= 400:
        try:
            body: Dict[str, Any] = response.json()
        except Exception:
            body = {}
        logger.warning(
            f"GoTrue error for {method} {path}: {response.status_code} - {body.get('code') or body.get('error')}"
        )
        raise map_gotrue_error(response.status_code, body)

    return cast(Dict[str, Any], response.json())


async def _dev_signup(email: str, password: str) -> Dict[str, Any]:
    key = email.strip().lower()
    if key in _dev_users:
        raise AuthError(
            409, "An account with this email already exists. Please log in instead."
        )
    salt, password_hash = _dev_password_hash(password)
    now = datetime.now(timezone.utc).isoformat()
    user = _DevUser(
        id=str(uuid.uuid4()),
        email=key,
        password_hash=password_hash,
        salt=salt,
        email_confirmed_at=now,
    )
    _dev_users[key] = user
    logger.info(f"[dev-auth] Created local user {key} ({user.id})")
    return {"id": user.id, "email": user.email, "email_confirmed_at": now}


async def _dev_login(email: str, password: str) -> Dict[str, Any]:
    key = email.strip().lower()
    user = _dev_users.get(key)
    if user is None or not _dev_password_matches(password, user.salt, user.password_hash):
        raise AuthError(401, "Invalid email or password.")
    return {
        "access_token": _dev_issue_access_token(user),
        "refresh_token": secrets.token_urlsafe(32),
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {"id": user.id, "email": user.email},
    }


async def _dev_forgot_password(email: str) -> str:
    key = email.strip().lower()
    user = _dev_users.get(key)
    if user is None:
        return ""
    token = secrets.token_urlsafe(32)
    _dev_recovery_tokens[token] = key
    logger.info(
        f"[dev-auth] Password reset link for {key}: "
        f"http://localhost:3001/reset-password?token={token}"
    )
    return token


async def _dev_reset_password(password: str, token: str) -> Dict[str, Any]:
    key = _dev_recovery_tokens.pop(token, None)
    user = _dev_users.get(key or "")
    if user is None:
        raise AuthError(400, "Invalid or expired recovery token.")
    salt, password_hash = _dev_password_hash(password)
    user.salt = salt
    user.password_hash = password_hash
    logger.info(f"[dev-auth] Password reset for {user.email}")
    return {}


async def signup(email: str, password: str) -> Dict[str, Any]:
    """Create a user. In development, uses a local in-memory store."""
    if settings.IS_DEVELOPMENT:
        logger.info(f"[dev-auth] Signup for {email} (local store)")
        return await _dev_signup(email, password)
    logger.info(f"Creating user for email: {email}")
    return await _request(
        "POST",
        "admin/users",
        settings.SUPABASE_SERVICE_ROLE_KEY,
        token=settings.SUPABASE_SERVICE_ROLE_KEY,
        payload={
            "email": email,
            "password": password,
            "email_confirm": not settings.EMAIL_CONFIRMATION_REQUIRED,
        },
    )


async def login(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user. In development, validates against the local store."""
    if settings.IS_DEVELOPMENT:
        logger.info(f"[dev-auth] Login for {email} (local store)")
        return await _dev_login(email, password)
    return await _request(
        "POST",
        "token?grant_type=password",
        settings.SUPABASE_KEY,
        payload={"email": email, "password": password},
    )


async def forgot_password(email: str) -> None:
    """Request a password recovery email. Always succeeds to avoid enumeration."""
    if settings.IS_DEVELOPMENT:
        logger.info(f"[dev-auth] Forgot-password for {email} (local store)")
        await _dev_forgot_password(email)
        return
    await _request("POST", "recover", settings.SUPABASE_KEY, payload={"email": email})


async def reset_password(password: str, token: str) -> Dict[str, Any]:
    """Reset a password using a recovery token."""
    if settings.IS_DEVELOPMENT:
        logger.info("[dev-auth] Reset-password (local store)")
        return await _dev_reset_password(password, token)
    return await _request(
        "POST",
        "verify",
        settings.SUPABASE_KEY,
        payload={"type": "recovery", "token": token, "password": password},
    )
