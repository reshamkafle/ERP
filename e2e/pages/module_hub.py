from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class ModuleHubPage(BasePage):
    """Generic ERP module hub (Finance, HCM, SCM, Projects, etc.)."""

    def open(self, route_path: str) -> "ModuleHubPage":
        path = route_path if route_path.startswith("/") else f"/{route_path}"
        self.driver.get(f"{self.base_url}{path}")
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1")))
        return self

    def add_record(self, *, title: str) -> None:
        title_input = self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='New record title…']"),
            ),
        )
        title_input.clear()
        title_input.send_keys(title)
        self.click_button("Add record")
        self.wait.until(lambda d: title in d.page_source)
