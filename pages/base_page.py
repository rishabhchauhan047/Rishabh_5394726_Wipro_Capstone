import os
import time
import allure
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.logger = get_logger(self.__class__.__name__)  # each page gets its own named logger

    def take_screenshot(self, name: str):
        """Save screenshot to /screenshots folder and attach it to Allure report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(filename)
        self.logger.info(f"Screenshot saved: {filename}")
        with open(filename, "rb") as f:
            allure.attach(
                f.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
        return filename

    def safe_type(self, locator, value):
        self.logger.debug(f"safe_type → locator={locator}, value='{value}'")
        for attempt in range(3):
            try:
                el = self.wait.until(EC.element_to_be_clickable(locator))
                el.clear()
                el.send_keys(value)
                self.logger.debug(f"safe_type succeeded on attempt {attempt + 1}")
                return
            except Exception as e:
                self.logger.warning(f"safe_type attempt {attempt + 1} failed: {e}")
                continue
        self.logger.error(f"safe_type failed after 3 attempts for locator: {locator}")
        raise Exception(f"Typing failed for locator: {locator}")

    def click(self, locator):
        self.logger.debug(f"click → locator={locator}")
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", element)
        self.logger.debug("click → done")

    def type(self, locator, text):
        self.logger.debug(f"type → locator={locator}, text='{text}'")
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)
        self.logger.debug("type → done")

    def get_all(self, locator):
        self.logger.debug(f"get_all → locator={locator}")
        elements = self.wait.until(EC.presence_of_all_elements_located(locator))
        self.logger.debug(f"get_all → found {len(elements)} elements")
        return elements

    def wait_page(self):
        self.logger.debug("wait_page → waiting for document.readyState == complete")
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1)
        self.logger.debug("wait_page → page ready")