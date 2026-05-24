"""Security-focused unit tests for auth hardening."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.config import DEFAULT_ADMIN_PASSWORD, DEFAULT_SECRET_KEY, Settings
from app.core.html_sanitize import sanitize_html
from app.core.llm_sanitize import sanitize_llm_text
from app.core.login_lockout import clear_failures, is_locked, record_failure
from app.core.security import create_access_token, decode_token
from app.schemas.promotion import PromotionConfirmBody, PromotionProjectConfirm
from app.services.promotion_validation import margin_allows_discount, validate_project_margins


def test_deployed_env_rejects_default_secret_key() -> None:
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(
            environment="production",
            secret_key=DEFAULT_SECRET_KEY,
            admin_password="strong-admin-password-123",
            database_url="postgresql+asyncpg://app:secret@db.example.com:5432/erp",
        )


def test_deployed_env_rejects_default_admin_password() -> None:
    with pytest.raises(ValueError, match="ADMIN_PASSWORD"):
        Settings(
            environment="staging",
            secret_key="a" * 32,
            admin_password=DEFAULT_ADMIN_PASSWORD,
            database_url="postgresql+asyncpg://app:secret@db.example.com:5432/erp",
        )


def test_llm_allowlist_required_when_base_url_set() -> None:
    with pytest.raises(ValueError, match="LLM_ALLOWED_HOSTS"):
        Settings(
            environment="development",
            llm_base_url="http://localhost:11434/v1",
            llm_model="llama3",
        )


def test_access_token_includes_token_version() -> None:
    token = create_access_token("1", "ADMIN", token_version=3)
    payload = decode_token(token)
    assert payload is not None
    assert payload["tv"] == 3
    assert payload.get("jti")


def test_sanitize_html_strips_script_tags() -> None:
    raw = "<html><body><script>alert(1)</script><p>ok</p></body></html>"
    cleaned = sanitize_html(raw)
    assert "<script" not in cleaned.lower()
    assert "ok" in cleaned


def test_sanitize_llm_text_truncates_and_strips_control_chars() -> None:
    assert sanitize_llm_text("hello\x00world", max_length=5) == "hello"


def test_login_lockout_triggers_after_max_failures() -> None:
    clear_failures("lockout-test@example.com")
    for _ in range(5):
        record_failure("lockout-test@example.com")
    locked, remaining = is_locked("lockout-test@example.com")
    assert locked is True
    assert remaining > 0
    clear_failures("lockout-test@example.com")


def test_promotion_confirm_rejects_invalid_discount_percent() -> None:
    with pytest.raises(ValidationError):
        PromotionProjectConfirm.model_validate(
            {
                "anchor": {"product_id": 1},
                "discount_kind": "percent",
                "discount_percent": 150.0,
            },
        )


def test_margin_validation_rejects_deep_discount() -> None:
    project = {
        "discount_kind": "percent",
        "discount_percent": 90.0,
        "anchor": {"product_id": 1},
        "related_items": [],
    }
    prices = {1: (Decimal("10"), Decimal("8"))}
    with pytest.raises(ValueError, match="margin floor"):
        validate_project_margins(project, product_prices=prices)


def test_margin_allows_reasonable_discount() -> None:
    assert margin_allows_discount(Decimal("100"), Decimal("40"), 50.0) is True


def test_promotion_confirm_body_accepts_valid_project() -> None:
    body = PromotionConfirmBody(
        projects=[
            PromotionProjectConfirm.model_validate(
                {
                    "anchor": {"product_id": 1, "sku": "SKU1", "name": "Item"},
                    "discount_kind": "percent",
                    "discount_percent": 10.0,
                    "duration_days": 14,
                },
            ),
        ],
    )
    assert len(body.projects) == 1
