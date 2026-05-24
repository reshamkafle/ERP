from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base import BasePage


class CrmPage(BasePage):
    def open(self) -> "CrmPage":
        self.driver.get(f"{self.base_url}/crm")
        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[contains(normalize-space(),'Customer Relationship')]"),
            ),
        )
        return self

    def create_lead(self, *, company_name: str) -> None:
        self._open_pipeline_leads()
        self.click_button("Add lead")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New lead']")),
        )
        self.fill_input_for_label_contains("Company *", company_name)
        self.click_button("Save")
        self.wait_dialog_heading_gone("New lead")

    def create_opportunity(self, *, title: str, customer_id: int) -> None:
        self._open_pipeline_opportunities()
        self.click_button("Add opportunity")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New opportunity']")),
        )
        self.fill_input_for_label_contains("Opportunity name *", title)
        customer_select = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//label[normalize-space()='Customer *']/following::select[1]"),
            ),
        )
        self.wait.until(
            lambda d: any(
                o.get_attribute("value") == str(customer_id)
                for o in customer_select.find_elements(By.TAG_NAME, "option")
            ),
        )
        Select(customer_select).select_by_value(str(customer_id))
        self.click_button("Save")
        self.wait_dialog_heading_gone("New opportunity")

    def add_module_record(self, *, feature_button: str, title: str) -> None:
        feature_btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[normalize-space()='{feature_button}']"),
            ),
        )
        feature_btn.click()
        self.click_button("Add record")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[contains(normalize-space(),'record')]")),
        )
        self.fill_input_for_label_contains("Title *", title)
        self.click_button("Save")
        self.wait.until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//h2[contains(normalize-space(),'record')]"),
            ),
        )

    def _open_pipeline_leads(self) -> None:
        self.open()
        pipeline = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Sales Pipeline']")),
        )
        pipeline.click()
        leads = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Leads']")),
        )
        leads.click()

    def _open_pipeline_opportunities(self) -> None:
        self.open()
        pipeline = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Sales Pipeline']")),
        )
        pipeline.click()
        opps = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Opportunities']")),
        )
        opps.click()
