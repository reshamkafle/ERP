"""Smoke-test every authenticated route for admin users."""

import pytest

from pages.layout import AppLayout


pytestmark = pytest.mark.e2e

# (nav label or None for direct URL, expected h1 title)
ADMIN_ROUTES: list[tuple[str | None, str, str]] = [
    ("Dashboard", "Dashboard", "/dashboard"),
    ("Reports", "Reports", "/reports"),
    ("Inventory", "Inventory", "/inventory"),
    ("Customers", "Customers", "/customers"),
    ("Suppliers", "Suppliers", "/suppliers"),
    ("Purchases", "Purchases", "/purchases"),
    ("POS", "Point of sale", "/pos"),
]


@pytest.mark.parametrize("nav_label,heading,path", ADMIN_ROUTES)
def test_admin_can_open_each_module(
    logged_in_admin: AppLayout,
    nav_label: str | None,
    heading: str,
    path: str,
) -> None:
    if nav_label:
        logged_in_admin.click_nav(nav_label)
    else:
        logged_in_admin.driver.get(f"{logged_in_admin.base_url}{path}")
    logged_in_admin.wait_page_heading(heading)
    assert path in logged_in_admin.driver.current_url


def test_reports_tabs_switch(logged_in_admin: AppLayout) -> None:
    from selenium.webdriver.common.by import By

    logged_in_admin.click_nav("Reports")
    logged_in_admin.wait_page_heading("Reports")

    for tab in ("Top products", "Stock value", "Sales"):
        btn = logged_in_admin.driver.find_element(
            By.XPATH,
            f"//button[normalize-space()='{tab}']",
        )
        btn.click()
        assert btn.is_displayed()
