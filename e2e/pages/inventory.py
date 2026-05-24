from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base import BasePage


class InventoryPage(BasePage):
    def open(self, *, item_type: str | None = None) -> "InventoryPage":
        url = f"{self.base_url}/inventory"
        if item_type:
            url = f"{url}?item_type={item_type}"
        self.driver.get(url)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Inventory']")))
        return self

    def create_item(self, *, sku: str, name: str, item_type: str) -> None:
        try:
            self.click_testid("add-inventory-item")
        except Exception:
            self.click_button("Add item")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New item']")),
        )
        self.fill_input_for_label_contains("SKU / Item code", sku)
        self.fill_input_for_label_contains("Item name", name)
        if item_type != "TRADING":
            classification_tab = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Classification']")),
            )
            classification_tab.click()
            type_select = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//label[contains(normalize-space(),'Item type')]/following::select[1]"),
                ),
            )
            Select(type_select).select_by_value(item_type)
        try:
            self.click_testid("inventory-create")
        except Exception:
            self.click_button("Create item")
        self.wait_dialog_heading_gone("New item")
