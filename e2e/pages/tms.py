from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class TmsPage(BasePage):
    def open(self) -> "TmsPage":
        self.driver.get(f"{self.base_url}/tms")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[contains(normalize-space(),'Transportation')]"),
            ),
        )
        return self

    def create_shipment(self, *, title: str) -> None:
        self.click_button("New shipment")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New shipment']")),
        )
        self.fill_input_for_label_contains("Title / summary", title)
        self.click_button("Create shipment")
        self.wait_dialog_heading_gone("New shipment")
