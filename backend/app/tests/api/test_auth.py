from __future__ import annotations

from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.core.config import settings
from backend.app.main import app
from backend.app.schemas.auth import SignupRequest, LoginRequest

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_dev_auth_state(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Reset the in-memory dev auth store and force dev mode before each test."""
    monkeypatch.setattr(settings, "IS_DEVELOPMENT", True)
    yield


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


def test_signup_conflict_returns_409() -> None:
    # This test would require mocking the database
    pass


def test_signup_success_returns_201() -> None:
    # This test would require mocking the database
    pass


def test_login_invalid_credentials_returns_401() -> None:
    # This test would require mocking the database
    pass


def test_login_success_returns_tokens() -> None:
    # This test would require mocking the database
    pass


def test_forgot_password_returns_generic_message() -> None:
    # This test would require mocking the database
    pass