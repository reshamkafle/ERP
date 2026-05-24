from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class ProcurementPage(BasePage):
    def open(self, *, feature: str = "purchase_requisitions") -> "ProcurementPage":
        self.driver.get(f"{self.base_url}/procurement?feature={feature}")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[contains(normalize-space(),'Procurement')]"),
            ),
        )
        return self

    def open_purchase_requisitions(self) -> "ProcurementPage":
        return self.open(feature="purchase_requisitions")

    def create_procurement_record(self, *, title: str) -> None:
        self.click_button("Add record")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[normalize-space()='New procurement record']"),
            ),
        )
        self.fill_input_by_label("Title / summary", title)
        self.click_button("Create record")
        self.wait_dialog_heading_gone("New procurement record")

    def create_purchase_requisition(self, *, title: str) -> None:
        self.create_procurement_record(title=title)
