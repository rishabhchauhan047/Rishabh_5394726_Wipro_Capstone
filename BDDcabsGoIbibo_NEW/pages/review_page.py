from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from locators.cab_locators import ReviewLocators
from pages.base_page import BasePage


class ReviewPage(BasePage):
    def verify_review_page_displayed(self):
        self.wait.until(lambda driver: "/cabs/review" in driver.current_url)
        self.wait_visible(ReviewLocators.REVIEW_TITLE)
        self.wait_visible(ReviewLocators.TRAVELLER_DETAILS)
        self.logger.info("Cab review page is displayed.")

    def fill_anonymous_traveller_details(self, pickup_location, full_name, mobile, email):
        self.verify_review_page_displayed()
        self.fill_pickup_location(pickup_location)
        self.fill_input(self.wait_visible(ReviewLocators.FULL_NAME_INPUT), full_name)
        self.fill_input(self.wait_visible(ReviewLocators.MOBILE_INPUT), mobile)
        self.fill_input(self.wait_visible(ReviewLocators.EMAIL_INPUT), email)
        self.logger.info(
            "Filled pickup and anonymous traveller details: pickup=%s, name=%s, mobile=%s, email=%s",
            pickup_location,
            full_name,
            mobile,
            email,
        )

    def fill_pickup_location(self, pickup_location):
        pickup_input = self.wait_visible(ReviewLocators.PICKUP_LOCATION_INPUT)
        pickup_query = pickup_location.split(",")[0].strip() or pickup_location
        self.type_and_select_suggestion(pickup_input, pickup_query, expected_text=pickup_location)
        self.wait_for_transient_overlays_to_clear()
        self.logger.info("Selected exact pickup location suggestion: %s", pickup_location)

    def verify_anonymous_traveller_details(self, pickup_location, full_name, mobile, email):
        values = [element.get_attribute("value") or "" for element in self.driver.find_elements(By.CSS_SELECTOR, "input")]
        body_and_url = f"{self.body_text()}\n{self.driver.current_url}\n" + "\n".join(values)
        pickup_key = pickup_location.split(",")[0].strip()
        assert pickup_key.lower() in body_and_url.lower(), "Pickup location did not remain selected."
        assert full_name in "\n".join(values), "Anonymous full name did not remain filled."
        assert mobile in "\n".join(values), "Anonymous mobile did not remain filled."
        assert email in "\n".join(values), "Anonymous email did not remain filled."
        self.logger.info("Anonymous traveller details remain filled.")

    def continue_to_payment(self):
        self.verify_review_page_displayed()
        self.click(ReviewLocators.PAY_NOW_BUTTON)
        self.logger.info("Clicked PAY NOW to continue to payment page.")

        def payment_loaded(driver):
            try:
                body = driver.find_element(By.TAG_NAME, "body").text
                return "payments.goibibo.com" in driver.current_url or "UPI Options" in body
            except Exception:
                return False

        try:
            WebDriverWait(self.driver, 80).until(payment_loaded)
        except TimeoutException as exc:
            body = self.body_text()
            validation_lines = [
                line
                for line in body.splitlines()
                if "Please enter" in line or "We need" in line or "required" in line.lower()
            ]
            raise AssertionError(
                "Payment page did not open after PAY NOW. Review validation still visible: "
                + " | ".join(validation_lines[:8])
            ) from exc
