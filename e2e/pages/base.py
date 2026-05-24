from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: float) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def click_button(self, label: str) -> None:
        button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[normalize-space()='{label}']"),
            ),
        )
        button.click()

    def click_testid(self, test_id: str) -> None:
        element = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-testid='{test_id}']")),
        )
        element.click()

    def fill_input_by_label(self, label: str, value: str) -> None:
        field = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//label[normalize-space()='{label}']/following-sibling::*[self::input or self::textarea or self::select][1]",
                ),
            ),
        )
        field.clear()
        field.send_keys(value)

    def fill_input_by_placeholder(self, placeholder: str, value: str) -> None:
        field = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"[placeholder='{placeholder}']")),
        )
        field.clear()
        field.send_keys(value)

    def select_option_by_label(self, label: str, option_value: str) -> None:
        select_el = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//label[normalize-space()='{label}']/following-sibling::select[1]",
                ),
            ),
        )
        for option in select_el.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == option_value:
                option.click()
                return
        raise TimeoutException(f"Option value '{option_value}' not found for '{label}'")

    def wait_dialog_heading_gone(self, heading: str) -> None:
        self.wait.until(
            EC.invisibility_of_element_located(
                (By.XPATH, f"//h2[normalize-space()='{heading}']"),
            ),
        )

    def wait_page_contains(self, text: str) -> None:
        self.wait.until(lambda d: text in d.page_source)

    def fill_input_for_label_contains(self, label_substring: str, value: str) -> None:
        field = self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//label[contains(normalize-space(), '{label_substring}')]"
                    "/following::input[1]",
                ),
            ),
        )
        field.clear()
        field.send_keys(value)

    def id_from_detail_link(self, list_path: str, link_text: str) -> int:
        """Open a list page, follow the row link, and parse numeric id from the URL."""
        self.driver.get(f"{self.base_url}{list_path}")
        link = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//a[contains(@href,'{list_path}/') and contains(normalize-space(),'{link_text}')]",
                ),
            ),
        )
        href = link.get_attribute("href") or ""
        segment = href.rstrip("/").split("/")[-1]
        return int(segment)
