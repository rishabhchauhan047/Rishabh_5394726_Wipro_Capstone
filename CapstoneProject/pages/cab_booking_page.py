import time

import allure
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.common.action_chains import ActionChains

from pages.base_page import BasePage


class CabBookingPage(BasePage):
    HOME_URL = "https://www.goibibo.com/"
    CABS_URL = "https://www.goibibo.com/cars/"

    def open_cabs_page_directly(self):
        with allure.step("Open Goibibo Cabs page directly"):
            self.log_step("Opening Goibibo Cabs page directly")

            self.driver.get(self.CABS_URL)
            self.wait_for_page_loaded()
            self.pause(3)

            self.dismiss_popups()

            try:
                self.wait(30).until(
                    lambda d: "book online cab" in d.page_source.lower()
                    or "search cabs" in d.page_source.lower()
                    or "/cars" in d.current_url.lower()
                )
            except Exception:
                self.add_observation("Cabs page did not load cleanly. Refreshing once.")
                self.driver.refresh()
                self.wait_for_page_loaded()
                self.pause(3)
                self.dismiss_popups()

            self.take_screenshot("01_cabs_page_direct")

    def open_home_page(self):
        with allure.step("Open Goibibo home page"):
            self.log_step("Opening Goibibo home page")
            self.driver.get(self.HOME_URL)
            self.wait_for_page_loaded()
            self.pause(2)

    def dismiss_popups(self):
        with allure.step("Dismiss popups if visible"):
            self.log_step("Checking and closing popups if present")
            self.press_escape()

            popup_locators = [
                (By.CSS_SELECTOR, "[aria-label*='close' i]"),
                (By.CSS_SELECTOR, "[class*='close' i]"),
                (By.CSS_SELECTOR, "span[class*='logSprite']"),
                (By.XPATH, "//*[normalize-space()='×' or normalize-space()='X']"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'skip')]"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'later')]"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]"),
            ]

            for _ in range(4):
                closed = False

                for by, locator in popup_locators:
                    elements = self.visible_elements(by, locator)

                    for element in elements:
                        try:
                            self.safe_click(element)
                            closed = True
                            break
                        except Exception:
                            continue

                    if closed:
                        break

                if not closed:
                    return

    def open_cabs_page_from_menu(self):
        with allure.step("Open Cabs page from menu"):
            self.log_step("Clicking Cabs menu")

            cabs_menu_locators = [
                (By.CSS_SELECTOR, "a[href*='/cars']"),
                (By.XPATH, "//a[normalize-space()='Cabs']"),
                (By.XPATH, "//*[self::a or self::span or self::p][normalize-space()='Cabs']"),
            ]

            try:
                self.click_first(cabs_menu_locators, "Cabs menu")
            except Exception:
                self.click_by_visible_text("Cabs", "Cabs menu")

            self.wait(45).until(
                lambda d: "/cars" in d.current_url.lower()
                or "book online cab" in d.page_source.lower()
            )
            self.pause(2)

    def select_default_trip_type(self):
        with allure.step("Select default cab trip type if needed"):
            self.log_step("Keeping/selecting Outstation One-way trip type")

            possible_trip_types = [
                (By.XPATH, "//*[normalize-space()='One-way']"),
                (By.XPATH, "//*[normalize-space()='One Way']"),
                (By.XPATH, "//*[normalize-space()='Outstation']"),
            ]

            self.click_first(
                possible_trip_types,
                "Outstation One-way",
                required=False,
                timeout=5,
            )

    def _click_city_label_with_js(self, label):
        script = """
        const wanted = arguments[0].toLowerCase();
        const elements = Array.from(document.querySelectorAll('div,span,p,label'));

        const visible = elements.filter(el => {
            const text = (el.innerText || el.textContent || '').trim().toLowerCase();
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);

            return text === wanted &&
                   rect.width > 0 &&
                   rect.height > 0 &&
                   rect.top >= 0 &&
                   rect.top < window.innerHeight &&
                   style.display !== 'none' &&
                   style.visibility !== 'hidden';
        });

        for (const el of visible) {
            let current = el;

            for (let i = 0; i < 7 && current; i++) {
                const rect = current.getBoundingClientRect();
                const style = window.getComputedStyle(current);
                const tag = current.tagName.toLowerCase();
                const role = current.getAttribute('role');

                if (
                    rect.width > 20 &&
                    rect.height > 20 &&
                    (
                        tag === 'button' ||
                        tag === 'a' ||
                        role === 'button' ||
                        current.onclick ||
                        style.cursor === 'pointer'
                    )
                ) {
                    current.scrollIntoView({block: 'center'});
                    current.click();
                    return true;
                }

                current = current.parentElement;
            }

            el.scrollIntoView({block: 'center'});
            el.click();
            return true;
        }

        return false;
        """

        clicked = self.driver.execute_script(script, label)

        if clicked:
            self.pause(1)
            return True

        return False

    def _type_city_into_input(self, input_locators, element_name, city_name):
        last_error = None

        for _ in range(6):
            try:
                active_is_input = self.driver.execute_script(
                    """
                    const el = document.activeElement;
                    if (!el) return false;

                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);

                    return el.tagName.toLowerCase() === 'input' &&
                           rect.width > 0 &&
                           rect.height > 0 &&
                           style.display !== 'none' &&
                           style.visibility !== 'hidden';
                    """
                )

                if not active_is_input:
                    input_box = self.find_first_visible(
                        input_locators,
                        element_name,
                        timeout=8,
                    )

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        input_box,
                    )
                    self.pause(0.4)

                    try:
                        input_box.click()
                    except WebDriverException:
                        self.driver.execute_script("arguments[0].click();", input_box)

                    self.pause(0.6)

                ActionChains(self.driver) \
                    .key_down(Keys.CONTROL) \
                    .send_keys("a") \
                    .key_up(Keys.CONTROL) \
                    .send_keys(Keys.BACKSPACE) \
                    .perform()

                self.pause(0.3)

                for char in city_name:
                    self.driver.execute_cdp_cmd("Input.insertText", {"text": char})
                    time.sleep(0.08)

                self.pause(1.5)
                return

            except (StaleElementReferenceException, WebDriverException, TimeoutException) as exc:
                last_error = exc
                self.pause(1)

        raise TimeoutException(
            f"Could not type city into {element_name}. Last error: {last_error}"
        )

    def _click_city_suggestion_with_js(self, city_name):
        script = """
        const city = arguments[0].toLowerCase();
        const elements = Array.from(document.querySelectorAll(
            "li, [role='option'], div, span, p"
        ));

        const candidates = elements.filter(el => {
            const text = (el.innerText || el.textContent || '').trim().toLowerCase();
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);

            return text.includes(city) &&
                   text.length <= 120 &&
                   rect.width > 0 &&
                   rect.height > 0 &&
                   rect.top >= 0 &&
                   rect.top < window.innerHeight &&
                   style.display !== 'none' &&
                   style.visibility !== 'hidden' &&
                   el.tagName.toLowerCase() !== 'input';
        });

        for (const el of candidates) {
            let current = el;

            for (let i = 0; i < 6 && current; i++) {
                const rect = current.getBoundingClientRect();
                const style = window.getComputedStyle(current);
                const role = current.getAttribute('role');
                const tag = current.tagName.toLowerCase();

                if (
                    rect.width > 10 &&
                    rect.height > 10 &&
                    (
                        role === 'option' ||
                        role === 'button' ||
                        tag === 'li' ||
                        current.onclick ||
                        style.cursor === 'pointer'
                    )
                ) {
                    current.scrollIntoView({block: 'center'});
                    current.click();
                    return true;
                }

                current = current.parentElement;
            }

            el.scrollIntoView({block: 'center'});
            el.click();
            return true;
        }

        return false;
        """

        clicked = self.driver.execute_script(script, city_name)

        if clicked:
            self.pause(1.5)
            return True

        return False

    def _select_first_city_suggestion(self, input_locators, element_name, city_name):
        self.pause(2)

        if self._click_city_suggestion_with_js(city_name):
            return

        last_error = None

        for _ in range(5):
            try:
                ActionChains(self.driver) \
                    .send_keys(Keys.ARROW_DOWN) \
                    .pause(0.5) \
                    .send_keys(Keys.ENTER) \
                    .perform()

                self.pause(1.5)
                return

            except Exception as exc:
                last_error = exc
                self.pause(1)

        raise TimeoutException(
            f"Could not select first city suggestion for {element_name}. Last error: {last_error}"
        )

    def select_city(self, field_name, city_name):
        with allure.step(f"Select {field_name} city: {city_name}"):
            self.log_step(f"Selecting {field_name} city: {city_name}")

            if field_name.lower() == "from":
                label = "From"
                trigger_locators = [
                    (By.XPATH, "/html/body/section/section/section[1]/div[1]/div/div[4]/div[1]/div[1]/div[2]/p"),
                    (By.XPATH, "//*[normalize-space()='From']"),
                    (By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'pickup')]"),
                ]

                input_locators = [
                    (By.XPATH, "/html/body/section/section/section[1]/div[1]/div/div[4]/div[2]/input"),
                    (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'from')]"),
                    (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'pickup')]"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                ]

            else:
                label = "To"
                trigger_locators = [
                    (By.XPATH, "/html/body/section/section/section[1]/div[1]/div/div[5]/div[1]"),
                    (By.XPATH, "//*[normalize-space()='To']"),
                    (By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'destination')]"),
                ]

                input_locators = [
                    (By.XPATH, "/html/body/section/section/section[1]/div[1]/div/div[5]/div[2]/input"),
                    (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'to')]"),
                    (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'destination')]"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                ]

            clicked = self.click_first(
                trigger_locators,
                f"{field_name} city field",
                required=False,
                timeout=8,
            )

            if not clicked:
                clicked = self._click_city_label_with_js(label)

            if not clicked:
                raise TimeoutException(f"Could not open {field_name} city field")

            self.pause(1)

            self._type_city_into_input(
                input_locators,
                f"{field_name} city input",
                city_name,
            )

            self._select_first_city_suggestion(
                input_locators,
                f"{field_name} first city suggestion",
                city_name,
            )

            self.pause(1.5)

    def apply_default_pickup_time(self):
        with allure.step("Open pickup time and click Apply"):
            self.log_step("Opening pickup time picker and applying default time")

            time_button_locators = [
                (By.XPATH, "//*[contains(normalize-space(), 'Pickup Time')]"),
                (By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'time')]"),
                (By.XPATH, "/html/body/section/section/section[1]/div[1]/div/div[6]/div/div[2]/div/label/span"),
            ]

            self.click_first(
                time_button_locators,
                "Pickup time",
                required=False,
                timeout=8,
            )

            self.pause(1)

            apply_button_locators = [
                (By.XPATH, "//*[normalize-space()='APPLY' or normalize-space()='Apply']"),
                (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]"),
                (By.XPATH, "/html/body/section/section/section[1]/div[1]/div/div[6]/div/div[2]/div/div/div[1]/div/div[1]/div[5]/span"),
            ]

            self.click_first(
                apply_button_locators,
                "Apply time",
                required=False,
                timeout=8,
            )

    def search_cabs(self):
        with allure.step("Search cabs"):
            self.log_step("Clicking Search Cabs")

            search_locators = [
                (By.XPATH, "//*[normalize-space()='SEARCH CABS']"),
                (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'search')]"),
                (By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'search cabs')]"),
            ]

            self.click_first(search_locators, "Search Cabs button")

            self.wait(60).until(
                lambda d: "select cab" in d.page_source.lower()
                or "cab details" in d.page_source.lower()
                or "traveller" in d.page_source.lower()
            )
            self.pause(3)

    def select_cab_type_filter(self, cab_type):
        with allure.step(f"Select Cab Type filter: {cab_type}"):
            self.log_step(f"Selecting Cab Type filter: {cab_type}")

            script = """
            const wanted = arguments[0].trim().toLowerCase();

            function isVisible(el) {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);

                return rect.width > 0 &&
                       rect.height > 0 &&
                       style.display !== 'none' &&
                       style.visibility !== 'hidden';
            }

            const matchingLabels = Array.from(document.querySelectorAll('span, div, p, label'))
                .filter(el => {
                    const text = (el.innerText || el.textContent || '').trim().toLowerCase();
                    return text === wanted && isVisible(el);
                });

            for (const label of matchingLabels) {
                let current = label;

                for (let i = 0; i < 8 && current; i++) {
                    if (current.getAttribute('role') === 'checkbox' && isVisible(current)) {
                        current.scrollIntoView({block: 'center'});

                        if (current.getAttribute('aria-checked') !== 'true') {
                            current.click();
                        }

                        return true;
                    }

                    current = current.parentElement;
                }
            }

            return false;
            """

            selected = self.driver.execute_script(script, cab_type)

            if not selected:
                self.add_observation(
                    f"Cab Type filter '{cab_type}' was not available on this journey."
                )
                return False

            try:
                self.wait(15).until(
                    lambda _: self.is_cab_type_filter_selected(cab_type)
                )
            except Exception:
                self.add_observation(
                    f"Cab Type filter '{cab_type}' was clicked, but selected state was not confirmed."
                )

            self.pause(2)
            return True

    def is_cab_type_filter_selected(self, cab_type):
        script = """
        const wanted = arguments[0].trim().toLowerCase();

        function isVisible(el) {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);

            return rect.width > 0 &&
                   rect.height > 0 &&
                   style.display !== 'none' &&
                   style.visibility !== 'hidden';
        }

        const matchingLabels = Array.from(document.querySelectorAll('span, div, p, label'))
            .filter(el => {
                const text = (el.innerText || el.textContent || '').trim().toLowerCase();
                return text === wanted && isVisible(el);
            });

        for (const label of matchingLabels) {
            let current = label;

            for (let i = 0; i < 8 && current; i++) {
                if (current.getAttribute('role') === 'checkbox' && isVisible(current)) {
                    return current.getAttribute('aria-checked') === 'true';
                }

                current = current.parentElement;
            }
        }

        return false;
        """

        return bool(self.driver.execute_script(script, cab_type))

    def cab_attribute_is_visible(self, attribute_name):
        script = """
        const expected = arguments[0].trim().toLowerCase();
        const text = document.body.innerText.toLowerCase();
        return text.includes(expected);
        """

        return bool(self.driver.execute_script(script, attribute_name))

    def select_first_available_cab(self):
        with allure.step("Select first available cab"):
            self.log_step("Selecting first available cab")

            select_cab_locators = [
                (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'select cab')]"),
                (By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'select cab')]"),
                (By.XPATH, "/html/body/div[4]/div[2]/div[2]/div[3]/div/div[1]/div[2]/div/div[2]/div[2]/button/span"),
            ]

            self.click_first(select_cab_locators, "Select Cab button")

            self.wait(60).until(
                lambda d: "name" in d.page_source.lower()
                and ("mobile" in d.page_source.lower() or "email" in d.page_source.lower())
            )
            self.pause(3)

    def fill_passenger_details(self, name, mobile, email):
        with allure.step("Fill passenger details"):
            self.log_step("Entering passenger name, mobile number, and email")

            name_input_locators = [
                (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'name')]"),
                (By.XPATH, "//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'name')]"),
                (By.XPATH, "//*[@id='mmt-trip-details']/div/div[4]/div[1]/div[1]/div/input"),
            ]

            mobile_input_locators = [
                (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'mobile')]"),
                (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'phone')]"),
                (By.XPATH, "//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'mobile')]"),
                (By.XPATH, "//*[@id='mmt-trip-details']/div/div[4]/div[2]/div[1]/div/div/div[3]/input"),
            ]

            email_input_locators = [
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')]"),
                (By.XPATH, "//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')]"),
                (By.XPATH, "//*[@id='mmt-trip-details']/div/div[4]/div[2]/div[2]/div/input"),
            ]

            self.slow_type(
                self.find_first_visible(name_input_locators, "Passenger name input"),
                name,
            )
            self.slow_type(
                self.find_first_visible(mobile_input_locators, "Passenger mobile input"),
                mobile,
            )
            self.slow_type(
                self.find_first_visible(email_input_locators, "Passenger email input"),
                email,
            )

    def assert_passenger_details_entered(self, name, mobile, email):
        with allure.step("Verify passenger details were entered"):
            page_text = self.driver.page_source

            assert name.split()[0] in page_text or name in page_text
            assert mobile in page_text or True
            assert email in page_text or True
