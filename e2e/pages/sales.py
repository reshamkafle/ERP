from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class SalesPage(BasePage):
    def open(self) -> "SalesPage":
        self.driver.get(f"{self.base_url}/sales")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Sales orders']")))
        return self

    def create_sales_order(
        self,
        *,
        customer_id: int,
        product_sku: str,
        customer_po_number: str = "PO-E2E-001",
        sales_organization: str = "1000",
        payment_terms: str = "Net 30",
    ) -> None:
        try:
            self.click_testid("new-sales-order")
        except Exception:
            self.click_button("New sales order")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New sales order']")),
        )
        self.click_button("Order header")
        self.fill_input_by_label("Customer PO number", customer_po_number)
        self.fill_input_by_label("Sales organization", sales_organization)
        self.select_option_by_label("Payment terms", payment_terms)
        self.click_button("Customer")
        self.select_option_by_label("Customer (Sold-To)", str(customer_id))
        self.click_button("Line items")
        self.fill_input_by_placeholder("Search products by SKU or name", product_sku)
        product_button = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    (
                        "//h2[normalize-space()='New sales order']/ancestor::form[1]"
                        "//button[contains(@class,'hover:bg-muted') "
                        f"and contains(., '{product_sku}')]"
                    ),
                ),
            ),
        )
        product_button.click()
        try:
            self.click_testid("save-draft")
        except Exception:
            self.click_button("Save draft")
        self.wait_dialog_heading_gone("New sales order")
