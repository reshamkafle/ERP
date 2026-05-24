from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base import BasePage


class BomPage(BasePage):
    def open(self) -> "BomPage":
        self.driver.get(f"{self.base_url}/bom")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Bill of Materials']")),
        )
        return self

    def create_bom(self, *, parent_sku: str, component_sku: str) -> None:
        self.driver.refresh()
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[normalize-space()='Bill of Materials']"),
            ),
        )
        parent_row = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//span[contains(@class,'font-mono') and normalize-space()='{parent_sku}']",
                ),
            ),
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", parent_row)
        create_btn = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//span[contains(@class,'font-mono') and normalize-space()='{parent_sku}']"
                    f"/ancestor::li[1]//button[normalize-space()='Create BOM']",
                ),
            ),
        )
        create_btn.click()
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='Create BOM']")),
        )
        component_select = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "(//table//select[.//option[normalize-space()='Select…']])[1]"),
            ),
        )
        Select(component_select).select_by_value(component_sku)
        self.click_button("Create BOM")
        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, "//h2[normalize-space()='Create BOM']")),
        )
