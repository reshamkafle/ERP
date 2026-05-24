from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class CustomersPage(BasePage):
    def open(self) -> "CustomersPage":
        self.driver.get(f"{self.base_url}/customers")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Customers']")))
        return self

    def create_customer(self, *, name: str, code: str | None = None) -> int:
        self.open()
        self.click_button("Add customer")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[contains(normalize-space(),'customer')]")),
        )
        self.fill_input_for_label_contains("Customer / company name", name)
        if code:
            self.fill_input_for_label_contains("Customer ID / code", code)
        self.click_button("Create")
        self.wait.until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//h2[contains(normalize-space(),'customer')]"),
            ),
        )
        return self.id_from_detail_link("/customers", name)
