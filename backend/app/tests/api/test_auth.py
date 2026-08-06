from __future__ import annotations

from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.core.config import settings
from backend.app.main import app
from backend.app.models.auth import LoginRequest, SignupRequest
from backend.app.services import auth_service
from backend.app.services.auth_service import AuthError, map_gotrue_error

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_dev_auth_state(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Reset the in-memory dev auth store and force dev mode before each test."""
    monkeypatch.setattr(settings, "IS_DEVELOPMENT", True)
    auth_service._dev_users.clear()
    auth_service._dev_recovery_tokens.clear()
    yield
    auth_service._dev_users.clear()
    auth_service._dev_recovery_tokens.clear()


def test_map_gotrue_error_user_already_exists() -> None:
    err = map_gotrue_error(400, {"code": "user_already_exists", "msg": "User already registered"})
    assert err.status_code == 409


def test_map_gotrue_error_invalid_credentials() -> None:
    err = map_gotrue_error(
        400,
        {"error": "invalid_grant", "error_description": "Invalid login credentials"},
    )
    assert err.status_code == 401


def test_map_gotrue_error_email_not_confirmed() -> None:
    err = map_gotrue_error(400, {"code": "email_not_confirmed", "msg": "Email not confirmed"})
    assert err.status_code == 403


def test_map_gotrue_error_rate_limit() -> None:
    err = map_gotrue_error(429, {"msg": "over_request_rate_limit"})
    assert err.status_code == 429


def test_signup_request_rejects_weak_password() -> None:
    with pytest.raises(ValidationError):
        SignupRequest(email="test@example.com", password="short")


def test_signup_request_rejects_missing_uppercase() -> None:
    with pytest.raises(ValidationError):
        SignupRequest(email="test@example.com", password="lowercase123")


def test_signup_request_valid() -> None:
    req = SignupRequest(email="test@example.com", password="Password123")
    assert req.email == "test@example.com"


def test_login_request_valid() -> None:
    req = LoginRequest(email="test@example.com", password="password123")
    assert req.email == "test@example.com"


@patch("backend.app.api.v1.auth.auth_signup")
def test_signup_conflict_returns_409(mock_signup: MagicMock) -> None:
    mock_signup.side_effect = AuthError(
        409, "An account with this email already exists. Please log in instead."
    )
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "existing@example.com", "password": "Password123"},
    )
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


@patch("backend.app.api.v1.auth.auth_signup")
def test_signup_success_returns_201(mock_signup: MagicMock) -> None:
    mock_signup.return_value = {
        "id": "user-1",
        "email": "new@example.com",
        "email_confirmed_at": "2026-01-01T00:00:00Z",
    }
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "new@example.com", "password": "Password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["user_id"] == "user-1"
    assert body["email_confirmed"] is True


@patch("backend.app.api.v1.auth.auth_login")
def test_login_invalid_credentials_returns_401(mock_login: MagicMock) -> None:
    mock_login.side_effect = AuthError(401, "Invalid email or password.")
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "WrongPass1"},
    )
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


@patch("backend.app.api.v1.auth.auth_login")
def test_login_success_returns_tokens(mock_login: MagicMock) -> None:
    mock_login.return_value = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {"id": "user-1", "email": "a@example.com"},
    }
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "Password123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] == "access-token"
    assert body["refresh_token"] == "refresh-token"
    assert body["user"]["id"] == "user-1"


@patch("backend.app.api.v1.auth.auth_forgot_password")
def test_forgot_password_returns_generic_message(mock_forgot: MagicMock) -> None:
    mock_forgot.side_effect = AuthError(400, "Email not found")
    resp = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "unknown@example.com"},
    )
    assert resp.status_code == 200
    assert "If an account exists" in resp.json()["message"]


def test_dev_signup_then_login_roundtrip() -> None:
    signup_resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "dev@example.com", "password": "Password123"},
    )
    assert signup_resp.status_code == 201
    user_id = signup_resp.json()["user_id"]
    assert signup_resp.json()["email_confirmed"] is True

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "dev@example.com", "password": "Password123"},
    )
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["id"] == user_id
    assert body["user"]["email"] == "dev@example.com"


def test_dev_signup_duplicate_returns_409() -> None:
    payload = {"email": "dup@example.com", "password": "Password123"}
    assert client.post("/api/v1/auth/signup", json=payload).status_code == 201
    resp = client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_dev_login_wrong_password_returns_401() -> None:
    client.post(
        "/api/v1/auth/signup",
        json={"email": "wrong@example.com", "password": "Password123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPass1"},
    )
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


def test_dev_login_unknown_user_returns_401() -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123"},
    )
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]


def test_dev_forgot_and_reset_password_roundtrip() -> None:
    client.post(
        "/api/v1/auth/signup",
        json={"email": "reset@example.com", "password": "Password123"},
    )
    resp = client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
    assert resp.status_code == 200
    assert "If an account exists" in resp.json()["message"]

    token = next(iter(auth_service._dev_recovery_tokens))
    assert auth_service._dev_recovery_tokens[token] == "reset@example.com"

    reset_resp = client.post(
        "/api/v1/auth/reset-password",
        json={"password": "NewPassword456", "token": token},
    )
    assert reset_resp.status_code == 200

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "reset@example.com", "password": "NewPassword456"},
    )
    assert login_resp.status_code == 200


def test_dev_reset_password_with_invalid_token_returns_400() -> None:
    resp = client.post(
        "/api/v1/auth/reset-password",
        json={"password": "NewPassword456", "token": "not-a-real-token"},
    )
    assert resp.status_code == 400
    assert "Invalid or expired" in resp.json()["detail"]


def test_dev_me_returns_signed_in_user() -> None:
    client.post(
        "/api/v1/auth/signup",
        json={"email": "me@example.com", "password": "Password123"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "Password123"},
    )
    token = login_resp.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_id"] != "dev-user-id"
    assert body["email"] == "me@example.com"
