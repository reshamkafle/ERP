from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class SuppliersPage(BasePage):
    def open(self) -> "SuppliersPage":
        self.driver.get(f"{self.base_url}/suppliers")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Vendor master']")),
        )
        return self

    def create_supplier(self, *, vendor_code: str, name: str) -> int:
        self.open()
        self.click_button("Add vendor")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New vendor']")),
        )
        self.fill_input_for_label_contains("Vendor code", vendor_code)
        self.fill_input_for_label_contains("Vendor name", name)
        self.click_button("Create vendor")
        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, "//h2[normalize-space()='New vendor']")),
        )
        return self.id_from_detail_link("/suppliers", name)
