from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class ModuleRecordPage(BasePage):
    """Dedicated module pages that use Add record + dialog (Finance, HCM, SCM)."""

    def open(self, route_path: str) -> "ModuleRecordPage":
        path = route_path if route_path.startswith("/") else f"/{route_path}"
        self.driver.get(f"{self.base_url}{path}")
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1")))
        return self

    def create_record(self, *, title: str, title_label: str = "Title / summary") -> None:
        self.click_button("Add record")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[contains(normalize-space(),'record') or contains(normalize-space(),'FI/CO')]"),
            ),
        )
        self.fill_input_for_label_contains(title_label, title)
        self.click_button("Create record")
        self.wait.until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//h2[contains(normalize-space(),'record') or contains(normalize-space(),'FI/CO')]"),
            ),
        )
