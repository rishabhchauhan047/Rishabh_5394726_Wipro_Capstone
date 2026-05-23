import json
import time
from pathlib import Path

import allure
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logger import get_logger


class BasePage:
    def type_into_first_visible(self, locators, element_name, value, timeout=20, attempts=5):
        last_error = None

        for _ in range(attempts):
            try:
                element = self.find_first_visible(
                    locators,
                    element_name,
                    timeout=timeout,
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element,
                )
                self.pause(0.4)

                element.click()
                element.send_keys(Keys.CONTROL, "a")
                element.send_keys(Keys.BACKSPACE)

                for char in value:
                    element.send_keys(char)
                    time.sleep(0.08)

                return element

            except StaleElementReferenceException as exc:
                last_error = exc
                self.pause(1)

            except WebDriverException as exc:
                last_error = exc
                self.pause(1)

        raise TimeoutException(
            f"Could not type into {element_name}. Last error: {last_error}"
        )

    def press_first_suggestion_by_keyboard(self, input_locators, element_name):
        last_error = None

        for _ in range(5):
            try:
                active_element = self.driver.switch_to.active_element
                active_element.send_keys(Keys.ARROW_DOWN)
                self.pause(0.5)
                active_element.send_keys(Keys.ENTER)
                self.pause(1)
                return

            except StaleElementReferenceException as exc:
                last_error = exc
                self.pause(1)

                try:
                    input_box = self.find_first_visible(
                        input_locators,
                        element_name,
                        timeout=5,
                    )
                    input_box.send_keys(Keys.ARROW_DOWN)
                    self.pause(0.5)
                    input_box.send_keys(Keys.ENTER)
                    self.pause(1)
                    return
                except Exception as inner_exc:
                    last_error = inner_exc

        raise TimeoutException(
            f"Could not select first suggestion for {element_name}. Last error: {last_error}"
        )


    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)
        self.observations = []

    def wait(self, seconds=None):
        return WebDriverWait(self.driver, seconds or self.timeout)

    def pause(self, seconds=0.8):
        time.sleep(seconds)

    def log_step(self, message):
        self.logger.info(message)
        print(f"[STEP] {message}")
        allure.attach(message, name="Step", attachment_type=allure.attachment_type.TEXT)

    def add_observation(self, message):
        self.logger.warning(message)
        print(f"[OBSERVATION] {message}")
        self.observations.append(message)
        allure.attach(message, name="Observation", attachment_type=allure.attachment_type.TEXT)

    def save_observations(self):
        Path("reports").mkdir(exist_ok=True)
        Path("reports/observations.json").write_text(
            json.dumps({"observations": self.observations}, indent=2),
            encoding="utf-8",
        )

    def take_screenshot(self, name):
        Path("screenshots").mkdir(exist_ok=True)

        screenshot = self.driver.get_screenshot_as_png()

        screenshot_path = Path(f"screenshots/{name}.png")
        screenshot_path.write_bytes(screenshot)

        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )

        self.logger.info(f"Screenshot captured: {screenshot_path}")

    def wait_for_page_loaded(self):
        self.wait(60).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def visible_elements(self, by, locator):
        try:
            return [
                element for element in self.driver.find_elements(by, locator)
                if element.is_displayed()
            ]
        except StaleElementReferenceException:
            return []

    def safe_click(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element,
        )
        self.pause(0.3)

        try:
            element.click()
        except WebDriverException:
            self.driver.execute_script("arguments[0].click();", element)

        self.pause(0.8)

    def click_first(self, locators, element_name, required=True, timeout=15):
        last_error = None

        for by, locator in locators:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, locator))
                )
                self.safe_click(element)
                return element
            except Exception as exc:
                last_error = exc

        message = f"Could not click {element_name}. Last error: {last_error}"

        if required:
            raise TimeoutException(message)

        self.add_observation(message)
        return None

    def find_first_visible(self, locators, element_name, required=True, timeout=20):
        end_time = time.time() + timeout

        while time.time() < end_time:
            for by, locator in locators:
                elements = self.visible_elements(by, locator)
                if elements:
                    return elements[0]

            time.sleep(0.5)

        message = f"Could not find visible element: {element_name}"

        if required:
            raise TimeoutException(message)

        self.add_observation(message)
        return None

    def slow_type(self, element, value, delay=0.08):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element,
        )
        element.click()
        element.clear()

        for char in value:
            element.send_keys(char)
            time.sleep(delay)

    def press_escape(self):
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass

    def click_by_visible_text(self, text, element_name=None, required=True):
        element_name = element_name or text

        script = """
        const wanted = arguments[0].trim().toLowerCase();
        const all = Array.from(document.querySelectorAll('a,button,div,span,p,label'));
        const visible = all.filter(el => {
            const box = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return box.width > 0 &&
                   box.height > 0 &&
                   style.visibility !== 'hidden' &&
                   style.display !== 'none' &&
                   el.innerText &&
                   el.innerText.trim().toLowerCase() === wanted;
        });

        for (const el of visible) {
            let current = el;
            for (let i = 0; i < 6 && current; i++) {
                const tag = current.tagName.toLowerCase();
                const role = current.getAttribute('role');
                const style = window.getComputedStyle(current);
                const box = current.getBoundingClientRect();

                if (
                    box.width > 10 &&
                    box.height > 10 &&
                    (
                        tag === 'a' ||
                        tag === 'button' ||
                        role === 'button' ||
                        current.onclick ||
                        style.cursor === 'pointer'
                    )
                ) {
                    current.scrollIntoView({block: 'center'});
                    return current;
                }

                current = current.parentElement;
            }
        }

        return visible[0] || null;
        """

        end_time = time.time() + self.timeout

        while time.time() < end_time:
            element = self.driver.execute_script(script, text)
            if element:
                self.safe_click(element)
                return element
            time.sleep(0.5)

        message = f"Could not click visible text: {element_name}"

        if required:
            raise TimeoutException(message)

        self.add_observation(message)
        return None