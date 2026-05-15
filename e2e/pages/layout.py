from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class AppLayout(BasePage):
    HEADER = (By.CSS_SELECTOR, "header")
    LOGOUT = (By.XPATH, "//button[normalize-space()='Log out']")

    def wait_authenticated(self) -> "AppLayout":
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        return self

    def click_nav(self, label: str) -> None:
        link = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//nav//a[normalize-space()='{label}']"),
            ),
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
