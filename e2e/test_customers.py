"""Customer module UI smoke test."""

import pytest

from pages.layout import AppLayout


pytestmark = pytest.mark.e2e


def test_customers_list_loads(logged_in_admin: AppLayout) -> None:
    logged_in_admin.click_nav("Customers")
    logged_in_admin.wait_page_heading("Customers")
    logged_in_admin.wait.until(
        lambda d: len(
            d.find_elements(
                "xpath",
                "//h1[normalize-space()='Customers']/following::input[1]",
            ),
        )
        > 0,
    )
