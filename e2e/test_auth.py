"""Authentication flows in the browser."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config import ADMIN_EMAIL, ADMIN_PASSWORD
from pages.login import LoginPage


pytestmark = pytest.mark.e2e


def test_login_page_renders(login_page: LoginPage) -> None:
    login_page.open().wait_loaded()
    assert login_page.driver.find_element(*LoginPage.EMAIL).is_displayed()
    assert login_page.driver.find_element(*LoginPage.PASSWORD).is_displayed()


def test_admin_can_sign_in_and_reach_dashboard(
    login_page: LoginPage,
    app_layout,
) -> None:
    login_page.open().wait_loaded()
    login_page.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    app_layout.wait_authenticated()
    app_layout.wait_page_heading("Dashboard")
    assert "/dashboard" in app_layout.driver.current_url


def test_invalid_credentials_show_error(login_page: LoginPage) -> None:
    login_page.open().wait_loaded()
    login_page.login("wrong@example.com", "not-a-real-password")
    toast = login_page.wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(normalize-space(), 'Invalid email or password')]"),
        ),
    )
    assert toast.is_displayed()
    assert "/login" in login_page.driver.current_url


def test_logout_returns_to_login(logged_in_admin, login_page: LoginPage) -> None:
    logged_in_admin.logout()
    login_page.wait_loaded()
