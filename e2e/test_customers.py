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


def test_customer_form_has_master_tabs(logged_in_admin: AppLayout) -> None:
    logged_in_admin.click_nav("Customers")
    logged_in_admin.wait_page_heading("Customers")
    driver = logged_in_admin.driver
    add_btn = driver.find_element("xpath", "//button[normalize-space()='Add customer']")
    add_btn.click()
    logged_in_admin.wait.until(
        lambda d: "Company" in d.page_source and "Tax" in d.page_source,
    )
    driver.find_element("xpath", "//button[normalize-space()='Cancel']").click()
