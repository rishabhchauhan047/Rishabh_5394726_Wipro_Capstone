import logging
import re
import time
from datetime import date, datetime, timedelta

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(
            driver,
            timeout,
            ignored_exceptions=(StaleElementReferenceException,),
        )
        self.short_wait = WebDriverWait(
            driver,
            6,
            ignored_exceptions=(StaleElementReferenceException,),
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def wait_for_page_ready(self):
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    def wait_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def visible_elements(self, locator):
        return [element for element in self.driver.find_elements(*locator) if self.is_displayed(element)]

    def visible_inputs(self, css_selector="input"):
        return [
            element
            for element in self.driver.find_elements(By.CSS_SELECTOR, css_selector)
            if self.is_displayed(element) and element.is_enabled()
        ]

    def click(self, locator):
        return self.click_element(self.wait_clickable(locator))

    def click_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.2)
        try:
            element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.driver.execute_script("arguments[0].click();", element)
        return element

    def fill_input(self, element, value, slow=False):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.2)
        try:
            self.click_element(element)
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
            if slow:
                for character in value:
                    element.send_keys(character)
                    time.sleep(0.04)
            else:
                element.send_keys(value)
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
            self.set_input_value(element, value)
        time.sleep(0.4)

    def set_input_value(self, element, value):
        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];
            element.scrollIntoView({block: 'center'});
            const prototype = element.tagName === 'TEXTAREA'
                ? HTMLTextAreaElement.prototype
                : HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
            setter.call(element, value);
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
            element.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true, key: 'a'}));
            """,
            element,
            value,
        )
        time.sleep(0.4)

    def input_by_label(self, label):
        label_literal = self.xpath_literal(label)
        locator = (By.XPATH, f"//input[@label={label_literal}]")
        return self.wait_visible(locator)

    def type_and_select_suggestion(self, input_element, query, expected_text=None):
        self.fill_input(input_element, query, slow=True)
        self.wait.until(
            lambda driver: any(
                self.is_displayed(element)
                for element in driver.find_elements(By.XPATH, "//*[@role='listbox']")
            )
        )

        try:
            input_element.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.2)
            input_element.send_keys(Keys.ENTER)
            if self._suggestion_list_closed():
                self.wait_for_transient_overlays_to_clear()
                return input_element
        except StaleElementReferenceException:
            self.wait_for_transient_overlays_to_clear()
            return input_element

        expected = expected_text or query
        candidates = [
            (
                By.XPATH,
                "//*[@role='listbox']//*[contains(normalize-space(.), "
                f"{self.xpath_literal(expected)}) and not(self::html) and not(self::body)]",
            ),
            (
                By.XPATH,
                "//*[@role='listbox']//*[contains(normalize-space(.), "
                f"{self.xpath_literal(query)}) and not(self::html) and not(self::body)]",
            ),
            (By.XPATH, "//*[@role='listbox']//*[not(self::html) and not(self::body)]"),
        ]

        for locator in candidates:
            try:
                for element in self.visible_elements(locator):
                    self.click_element(element)
                    if self._suggestion_list_closed():
                        self.wait_for_transient_overlays_to_clear()
                        return element
            except (StaleElementReferenceException, TimeoutException):
                self.wait_for_transient_overlays_to_clear()
                return input_element

        if self._click_first_visible_suggestion_row():
            self.wait_for_transient_overlays_to_clear()
            return input_element
        raise TimeoutException(f"No selectable suggestion was found for: {expected}")

    def _suggestion_list_closed(self):
        try:
            WebDriverWait(self.driver, 5, ignored_exceptions=(StaleElementReferenceException,)).until(
                lambda driver: all(
                    not self.is_displayed(element)
                    for element in driver.find_elements(By.XPATH, "//*[@role='listbox']")
                )
            )
            return True
        except TimeoutException:
            return False

    def _click_first_visible_suggestion_row(self):
        rows = self.driver.find_elements(
            By.XPATH,
            "//*[@role='listbox']//*[self::span or self::div][normalize-space(.) != '']",
        )
        for row in rows:
            if not self.is_displayed(row):
                continue
            try:
                self.click_element(row)
                if self._suggestion_list_closed():
                    return True
            except Exception:
                continue
        return False

    def wait_for_transient_overlays_to_clear(self):
        def overlays_are_gone(driver):
            overlays = driver.find_elements(By.XPATH, "//*[contains(@class, 'popup') or @role='dialog']")
            return all(not self.is_displayed(overlay) for overlay in overlays)

        try:
            WebDriverWait(self.driver, 12, ignored_exceptions=(StaleElementReferenceException,)).until(
                overlays_are_gone
            )
        except TimeoutException:
            self.logger.info("Transient overlay remained visible; continuing with resilient clicks.")
        time.sleep(0.6)

    def dismiss_overlays(self):
        close_locators = [
            (By.XPATH, "//button[contains(@aria-label, 'close') or contains(@aria-label, 'Close')]"),
            (By.XPATH, "//*[normalize-space()='x' or normalize-space()='X' or normalize-space()='×']"),
        ]
        for locator in close_locators:
            for element in self.driver.find_elements(*locator):
                try:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        time.sleep(0.4)
                except Exception:
                    continue

    def body_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text

    def parse_date(self, value):
        cleaned = value.strip().lower()
        if cleaned == "today":
            return date.today()
        if cleaned == "tomorrow":
            return date.today() + timedelta(days=1)

        relative_match = re.fullmatch(r"today\s*\+\s*(\d+)\s*days?", cleaned)
        if relative_match:
            return date.today() + timedelta(days=int(relative_match.group(1)))

        for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue

        raise ValueError(
            f"Unsupported date '{value}'. Use tomorrow, today + 4 days, 25 May 2026, or 2026-05-25."
        )

    def normalize_time(self, value):
        for fmt in ("%I:%M %p", "%H:%M"):
            try:
                return datetime.strptime(value.strip().upper(), fmt).strftime("%I:%M %p")
            except ValueError:
                continue
        raise ValueError(f"Unsupported pickup time: {value}. Use a value like 10:00 AM.")

    @staticmethod
    def is_displayed(element):
        try:
            return element.is_displayed()
        except StaleElementReferenceException:
            return False

    @staticmethod
    def xpath_literal(text):
        if "'" not in text:
            return f"'{text}'"
        if '"' not in text:
            return f'"{text}"'
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in text.split("'")) + ")"
