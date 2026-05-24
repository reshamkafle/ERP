from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class DocumentsPage(BasePage):
    def open_type(self, document_type: str) -> "DocumentsPage":
        self.driver.get(f"{self.base_url}/documents?type={document_type}")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Documents']")))
        return self

    def create_document(self, *, title: str, reference: str) -> None:
        try:
            self.click_testid("new-document")
        except Exception:
            self.click_button("New document")
        self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//h2[normalize-space()='New document']")),
        )
        self.fill_input_by_label("Title", title)
        self.fill_input_by_label("Reference number", reference)
        try:
            self.click_testid("document-create")
        except Exception:
            self.click_button("Create")
        self.wait_dialog_heading_gone("New document")
