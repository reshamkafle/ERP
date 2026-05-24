from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class WarehousesPage(BasePage):
    def open(self) -> "WarehousesPage":
        self.driver.get(f"{self.base_url}/warehouses")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Warehouses']")))
        return self

    def create_warehouse(self, *, code: str, name: str) -> None:
        self.open()
        self.click_button("Add warehouse")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New warehouse']")),
        )
        self.fill_input_for_label_contains("Code", code)
        self.fill_input_for_label_contains("Name", name)
        self.click_button("Save")
        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, "//h2[normalize-space()='New warehouse']")),
        )


class LocationsPage(BasePage):
    def open(self) -> "LocationsPage":
        self.driver.get(f"{self.base_url}/locations")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Storage locations']")),
        )
        return self

    def create_location(self, *, code: str) -> None:
        self.open()
        self.click_button("Add location")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New location']")),
        )
        self.wait.until(
            lambda d: len(
                d.find_elements(
                    By.XPATH,
                    "//label[contains(normalize-space(),'Warehouse')]/following::select[1]/option",
                ),
            )
            > 0,
        )
        self.fill_input_for_label_contains("Location code", code)
        self.click_button("Save")
        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, "//h2[normalize-space()='New location']")),
        )
