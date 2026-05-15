from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base import BasePage


class LoginPage(BasePage):
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    HEADING = (By.XPATH, "//h1[normalize-space()='Sign in']")

    def open(self) -> "LoginPage":
        self.driver.get(f"{self.base_url}/login")
        return self

    def wait_loaded(self) -> "LoginPage":
        self.wait.until(EC.visibility_of_element_located(self.HEADING))
        return self

    def login(self, email: str, password: str) -> None:
        email_el = self.wait.until(EC.visibility_of_element_located(self.EMAIL))
        email_el.clear()
        email_el.send_keys(email)
        password_el = self.driver.find_element(*self.PASSWORD)
        password_el.clear()
        password_el.send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
