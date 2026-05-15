from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class PosPage(BasePage):
    SEARCH = (
        By.CSS_SELECTOR,
        "input[placeholder*='Search name, SKU, or barcode']",
    )
    CART_HEADING = (By.XPATH, "//h2[normalize-space()='Cart']")
    CHECKOUT = (By.XPATH, "//button[contains(normalize-space(), 'Checkout')]")

    def open(self) -> "PosPage":
        self.driver.get(f"{self.base_url}/pos")
        return self

    def wait_loaded(self) -> "PosPage":
        self.wait.until(EC.visibility_of_element_located(self.CART_HEADING))
        return self

    def search_and_add_first(self, query: str) -> None:
        search = self.wait.until(EC.visibility_of_element_located(self.SEARCH))
        search.clear()
        search.send_keys(query)
        product_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//ul[contains(@class,'divide-y')]//button[not(@disabled)]"),
            ),
        )
        product_btn.click()

    def checkout(self) -> None:
        btn = self.wait.until(EC.element_to_be_clickable(self.CHECKOUT))
        btn.click()

    def wait_receipt_dialog(self) -> None:
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[starts-with(normalize-space(), 'Sale #')]"),
            ),
        )
