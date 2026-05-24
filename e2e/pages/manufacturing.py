from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base import BasePage


class ManufacturingPage(BasePage):
    def open(self) -> "ManufacturingPage":
        self.driver.get(f"{self.base_url}/manufacturing")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[contains(normalize-space(),'Manufacturing')]"),
            ),
        )
        return self

    def create_production_order(self, *, product_id: int) -> None:
        self.driver.refresh()
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[contains(normalize-space(),'Manufacturing')]"),
            ),
        )
        try:
            self.click_testid("new-production-order")
        except Exception:
            self.click_button("New production order")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[normalize-space()='New production order']"),
            ),
        )
        product_select = self.wait.until(
            lambda d: d.find_element(By.CSS_SELECTOR, "#po-product"),
        )
        self.wait.until(
            lambda d: any(
                o.get_attribute("value") == str(product_id)
                for o in product_select.find_elements(By.TAG_NAME, "option")
            ),
        )
        Select(product_select).select_by_value(str(product_id))
        try:
            self.click_testid("production-order-save")
        except Exception:
            self.click_button("Save")
        self.wait_dialog_heading_gone("New production order")
