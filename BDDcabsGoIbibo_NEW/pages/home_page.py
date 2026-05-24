import time
from datetime import date, datetime

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from locators.cab_locators import HomeLocators, ListingLocators
from pages.base_page import BasePage


class HomePage(BasePage):
    def open(self, base_url):
        self.logger.info("Opening Goibibo cab booking page: %s", base_url)
        self.driver.get(base_url)
        self.wait_for_page_ready()
        self.dismiss_overlays()
        self.wait_visible(HomeLocators.PAGE_HEADING)

    def search_one_way_route(
        self,
        pickup_query,
        pickup_suggestion,
        drop_query,
        drop_suggestion,
        pickup_date,
        pickup_time,
    ):
        self.select_trip_type("Outstation One-way")
        selected_pickup = self.select_pickup_city(pickup_query, pickup_suggestion)
        selected_drop = self.select_drop_city(drop_query, drop_suggestion)
        self.logger.info("Selected route: %s -> %s", selected_pickup, selected_drop)
        self.select_pickup_date(pickup_date)
        self.select_pickup_time(pickup_time)
        self.search_cabs()

    def select_trip_type(self, trip_type):
        normalized = " ".join(trip_type.split())
        mapping = {
            "outstation one-way": (
                "//label[contains(normalize-space(.), 'Outstation') "
                "and contains(normalize-space(.), 'One-way')]"
            ),
            "outstation round trip": (
                "//label[contains(normalize-space(.), 'Outstation') "
                "and contains(normalize-space(.), 'Round trip')]"
            ),
            "airport transfer": (
                "//label[contains(normalize-space(.), 'Airport') "
                "and contains(normalize-space(.), 'transfer')]"
            ),
            "hourly rental": "//label[contains(normalize-space(.), 'Hourly Rental')]",
        }
        locator = mapping.get(normalized.lower())
        if locator is None:
            raise ValueError(f"Unsupported cab trip type: {trip_type}")
        self.click((By.XPATH, locator))
        self.logger.info("Selected trip type: %s", trip_type)

    def select_pickup_city(self, query, suggestion):
        return self._select_city(HomeLocators.PICKUP_INPUT, query, suggestion)

    def select_drop_city(self, query, suggestion):
        return self._select_city(HomeLocators.DROP_INPUT, query, suggestion)

    def select_pickup_date(self, pickup_date):
        target_date = self.parse_date(pickup_date)
        if target_date < date.today():
            raise ValueError(f"Pickup date must not be in the past: {target_date}")

        self._open_date_picker()
        self._move_calendar_to(target_date)
        day_locator = (
            By.XPATH,
            "//div[contains(@class, 'CalendarBlockOuterWrapper')]"
            f"//li[normalize-space()={self.xpath_literal(str(target_date.day))} "
            "and not(contains(@class, 'disabled'))]",
        )
        self.click(day_locator)
        expected = target_date.strftime("%d %b").lstrip("0")
        self.wait.until(
            lambda driver: expected
            in driver.find_element(By.XPATH, "//*[contains(@class, 'PickupDate')]").text
        )
        self.logger.info("Selected pickup date: %s", target_date.isoformat())

    def select_pickup_time(self, pickup_time):
        normalized_time = self.normalize_time(pickup_time)
        self._open_time_picker()
        time_option = (
            By.XPATH,
            "//ul[.//*[contains(normalize-space(), '00:00 AM')]]"
            f"//*[normalize-space()={self.xpath_literal(normalized_time)}]",
        )
        self.click(time_option)
        self.wait.until(
            lambda driver: normalized_time
            in driver.find_element(By.XPATH, "//*[contains(@class, 'PickupTime')]").text
        )
        self.logger.info("Selected pickup time: %s", normalized_time)

    def search_cabs(self):
        self.logger.info("Submitting cab search.")
        self.click(HomeLocators.SEARCH_CABS_BUTTON)
        self.wait.until(
            lambda driver: "/cabs/listing" in driver.current_url
            or len(driver.find_elements(*ListingLocators.SELECT_CAB_BUTTONS)) > 0
        )
        self.wait_for_page_ready()
        self.dismiss_overlays()

    def attempt_invalid_search(self, case_description):
        before_url = self.driver.current_url
        self.logger.info("Attempting invalid search: %s", case_description)
        try:
            self.click(HomeLocators.SEARCH_CABS_BUTTON)
        except TimeoutException:
            self.logger.info("Search button was not clickable for invalid case: %s", case_description)

        time.sleep(3)
        after_url = self.driver.current_url
        body_text = self.body_text()
        blocked = "/cabs/listing" not in after_url and "/cabs/review" not in after_url
        return {
            "case_description": case_description,
            "url_before": before_url,
            "url_after": after_url,
            "blocked": blocked,
            "body_excerpt": body_text[:1000],
        }

    def type_raw_drop_text(self, text):
        for attempt in range(5):
            try:
                field = self.wait_clickable(HomeLocators.DROP_INPUT)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                try:
                    field.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", field)
                time.sleep(0.3)
                field = self.wait_clickable(HomeLocators.DROP_INPUT)
                field.send_keys(Keys.CONTROL, "a")
                field.send_keys(Keys.BACKSPACE)
                field.send_keys(text)
                self.logger.info("Typed drop text without selecting suggestion: %s", text)
                return
            except (StaleElementReferenceException, ElementNotInteractableException):
                if attempt == 4:
                    raise
                time.sleep(0.5)

    def _select_city(self, input_locator, query, suggestion):
        self.logger.info("Selecting city. Query=%s, expected suggestion=%s", query, suggestion)
        typed = False
        for attempt in range(5):
            try:
                field = self.wait_clickable(input_locator)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                try:
                    field.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", field)
                time.sleep(0.3)
                field = self.wait_clickable(input_locator)
                field.send_keys(Keys.CONTROL, "a")
                field.send_keys(Keys.BACKSPACE)
                field.send_keys(query)
                typed = True
                break
            except (StaleElementReferenceException, ElementNotInteractableException):
                if attempt == 4:
                    raise
                time.sleep(0.5)

        if not typed:
            raise TimeoutException(f"Could not type city query: {query}")

        option = self._find_city_option(suggestion)
        selected_text = option.text.strip().replace("\n", " ")
        self.click_element(option)
        self.wait.until(
            lambda driver: (driver.find_element(*input_locator).get_attribute("value") or "").strip() != ""
        )
        return selected_text

    def _find_city_option(self, suggestion):
        exact_locator = (
            By.XPATH,
            "//*[@role='option' and .//*[normalize-space()="
            f"{self.xpath_literal(suggestion)}]]",
        )
        contains_locator = (
            By.XPATH,
            "//*[@role='option' and contains(normalize-space(.), "
            f"{self.xpath_literal(suggestion)})]",
        )
        any_option_locator = (
            By.XPATH,
            "//*[@role='option' and not(contains(normalize-space(.), 'Use Current Location'))]",
        )

        self.wait.until(lambda driver: len(driver.find_elements(*any_option_locator)) > 0)
        for locator in (exact_locator, contains_locator, any_option_locator):
            visible = self.visible_elements(locator)
            if visible:
                return visible[0]
        raise TimeoutException(f"No city suggestion found for: {suggestion}")

    def _open_date_picker(self):
        self.click(HomeLocators.DATE_BLOCK)
        self.wait_visible(HomeLocators.CALENDAR_WRAPPER)

    def _open_time_picker(self):
        self.click(HomeLocators.TIME_BLOCK)
        self.wait_visible(HomeLocators.TIME_LIST)

    def _move_calendar_to(self, target_date):
        target_month = date(target_date.year, target_date.month, 1)

        for _ in range(24):
            visible_month = self._visible_calendar_month()
            if visible_month == target_month:
                return

            arrow_locator = HomeLocators.CALENDAR_NEXT if visible_month < target_month else HomeLocators.CALENDAR_PREVIOUS
            previous_label = self._visible_calendar_label()
            self.click(arrow_locator)
            self.wait.until(lambda _: self._visible_calendar_label() != previous_label)

        raise TimeoutException(f"Could not move calendar to {target_date:%B %Y}")

    def _visible_calendar_month(self):
        label = self._visible_calendar_label()
        return datetime.strptime(label, "%B %Y").date().replace(day=1)

    def _visible_calendar_label(self):
        return self.wait_visible(HomeLocators.CALENDAR_MONTH_LABEL).text.strip()
