"""Pytest fixtures for Selenium E2E tests (Chrome)."""

from __future__ import annotations

import sys
import uuid
from collections.abc import Generator
from pathlib import Path

import httpx
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

# Allow `from pages...` when running pytest from repo root or e2e/
E2E_ROOT = Path(__file__).resolve().parent
if str(E2E_ROOT) not in sys.path:
    sys.path.insert(0, str(E2E_ROOT))

from config import (  # noqa: E402
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    API_URL,
    BASE_URL,
    EXPLICIT_WAIT_SEC,
    HEADLESS,
    IMPLICIT_WAIT_SEC,
)
from helpers.seed_masters import FlowSeedMasters, seed_flow_masters  # noqa: E402
from pages.layout import AppLayout  # noqa: E402
from pages.login import LoginPage  # noqa: E402


def _stack_available() -> tuple[bool, str]:
    try:
        with httpx.Client(timeout=3.0) as client:
            health = client.get(f"{API_URL}/api/v1/health")
            if health.status_code != 200:
                return False, f"API health returned {health.status_code}"
            front = client.get(BASE_URL)
            if front.status_code >= 500:
                return False, f"Frontend returned {front.status_code}"
    except httpx.HTTPError as exc:
        return False, str(exc)
    return True, ""


@pytest.fixture(scope="session")
def require_stack() -> None:
    ok, reason = _stack_available()
    if not ok:
        pytest.skip(
            f"E2E stack not reachable ({reason}). "
            "Start postgres, backend (port 8000), and frontend (port 5173)."
        )


@pytest.fixture
def driver(require_stack: None) -> Generator[WebDriver, None, None]:
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    chrome = webdriver.Chrome(options=options)
    chrome.implicitly_wait(IMPLICIT_WAIT_SEC)
    try:
        yield chrome
    finally:
        chrome.quit()


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def wait_timeout() -> float:
    return EXPLICIT_WAIT_SEC


@pytest.fixture
def login_page(driver: WebDriver, base_url: str, wait_timeout: float) -> LoginPage:
    return LoginPage(driver, base_url, wait_timeout)


@pytest.fixture
def app_layout(driver: WebDriver, base_url: str, wait_timeout: float) -> AppLayout:
    return AppLayout(driver, base_url, wait_timeout)


def _login_api_client(timeout: float = 15.0) -> httpx.Client:
    """Authenticate via HttpOnly cookie (no token in JSON body)."""
    client = httpx.Client(base_url=API_URL, timeout=timeout)
    res = client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    res.raise_for_status()
    return client


@pytest.fixture
def api_client(require_stack: None) -> Generator[httpx.Client, None, None]:
    client = _login_api_client()
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def seeded_product(api_client: httpx.Client) -> dict:
    """Create a sellable product for POS tests; unique SKU per run."""
    sku = f"E2E-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "sku": sku,
        "name": f"E2E Widget {sku}",
        "lifecycle_status": "ACTIVE",
        "initial_stock": 25,
        "price": "12.50",
        "cost_price": "6.00",
        "low_stock_threshold": 3,
    }
    res = api_client.post("/api/v1/inventory", json=payload)
    res.raise_for_status()
    return res.json()


@pytest.fixture
def logged_in_admin(login_page: LoginPage, app_layout: AppLayout) -> AppLayout:
    login_page.open().wait_loaded()
    login_page.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    app_layout.wait_authenticated()
    return app_layout


@pytest.fixture(scope="session")
def flow_seed_masters(require_stack: None) -> FlowSeedMasters:
    """Customer, supplier, products, and BOM parent SKUs for ERPFlow seed tests."""
    import os

    bom_count = int(os.getenv("E2E_DOC_COUNT", "20"))
    client = _login_api_client(timeout=30.0)
    try:
        return seed_flow_masters(client, bom_parent_count=bom_count)
    finally:
        client.close()
