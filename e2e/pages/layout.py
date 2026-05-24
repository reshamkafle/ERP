from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class AppLayout(BasePage):
    SIDEBAR = (By.CSS_SELECTOR, "[data-testid='app-sidebar']")
    LOGOUT = (By.CSS_SELECTOR, "[data-testid='logout-button']")

    def wait_authenticated(self) -> "AppLayout":
        self.wait.until(EC.visibility_of_element_located(self.SIDEBAR))
        return self

    def click_nav(self, label: str) -> None:
        """Click sidebar link by visible label."""
        link = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//aside[@data-testid='app-sidebar']//a[normalize-space()='{label}']"),
            ),
        )
        link.click()

    def click_nav_slug(self, slug: str) -> None:
        """Click sidebar link by data-testid slug (e.g. dashboard, inventory)."""
        link = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-testid='nav-{slug}']")),
        )
        link.click()

    def wait_page_heading(self, title: str) -> None:
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//h1[normalize-space()='{title}']"),
            ),
        )

    def logout(self) -> None:
        self.driver.find_element(*self.LOGOUT).click()
        self.wait.until(EC.url_contains("/login"))
