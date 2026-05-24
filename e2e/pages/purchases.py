import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class PurchasesPage(BasePage):
    def open(self) -> "PurchasesPage":
        self.driver.get(f"{self.base_url}/purchases")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New purchase']")),
        )
        return self

    def create_purchase(self, *, supplier_id: int, product_sku: str) -> None:
        supplier_select = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//label[normalize-space()='Supplier']/following-sibling::select[1]"),
            ),
        )
        for option in supplier_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == str(supplier_id):
                option.click()
                break

        search_input = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//label[normalize-space()='Search products']/following-sibling::input[1]"),
            ),
        )
        search_input.clear()
        search_input.send_keys(product_sku)
        time.sleep(0.5)
        add_button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    (
                        "//h2[normalize-space()='New purchase']/ancestor::section[1]"
                        "//button[contains(@class,'hover:bg-muted') "
                        f"and contains(., '{product_sku}')]"
                    ),
                ),
            ),
        )
        add_button.click()
        self.click_button("Record purchase")
        self.wait.until(
            lambda d: "Purchase recorded" in d.page_source or "Saving…" not in d.page_source,
        )
