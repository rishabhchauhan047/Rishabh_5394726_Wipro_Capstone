import json

from pages.home_page import HomePage
from pages.payment_page import PaymentPage
from pages.review_page import ReviewPage
from pages.search_results_page import SearchResultsPage


class GoibiboCabBooking:
    def __init__(self, driver, base_url, timeout=30):
        self.driver = driver
        self.base_url = base_url
        self.home_page = HomePage(driver, timeout)
        self.search_results_page = SearchResultsPage(driver, timeout)
        self.review_page = ReviewPage(driver, timeout)
        self.payment_page = PaymentPage(driver, timeout)
        self.latest_negative_observation = {}

    def open_home_page(self):
        self.home_page.open(self.base_url)

    def search_one_way_route(self, pickup_query, pickup_suggestion, drop_query, drop_suggestion, pickup_date, pickup_time):
        self.home_page.search_one_way_route(
            pickup_query,
            pickup_suggestion,
            drop_query,
            drop_suggestion,
            pickup_date,
            pickup_time,
        )

    def select_trip_type(self, trip_type):
        self.home_page.select_trip_type(trip_type)

    def apply_listing_filter(self, option, expected_result_text):
        return self.search_results_page.apply_listing_filter(option, expected_result_text)

    def verify_cab_results_displayed(self):
        self.search_results_page.verify_cab_results_displayed()

    def verify_listing_reflects_filters(self, applied_filters):
        self.search_results_page.verify_listing_reflects_filters(applied_filters)

    def verify_listing_mentions(self, expected_text):
        self.search_results_page.verify_listing_mentions(expected_text)

    def verify_route_details(self, pickup, drop):
        self.search_results_page.verify_route_details(pickup, drop)

    def select_cab(self, cab_preference="first available"):
        self.search_results_page.select_cab(cab_preference)

    def verify_review_page_displayed(self):
        self.review_page.verify_review_page_displayed()

    def fill_anonymous_traveller_details(self, pickup_location, full_name, mobile, email):
        self.review_page.fill_anonymous_traveller_details(pickup_location, full_name, mobile, email)

    def verify_anonymous_traveller_details(self, pickup_location, full_name, mobile, email):
        self.review_page.verify_anonymous_traveller_details(pickup_location, full_name, mobile, email)

    def continue_to_payment(self):
        self.review_page.continue_to_payment()

    def select_upi_payment_option(self):
        self.payment_page.select_upi_option()

    def click_generate_qr(self):
        self.payment_page.click_generate_qr()

    def verify_upi_qr_displayed(self):
        self.payment_page.verify_upi_qr_displayed()

    def verify_no_actual_payment_completed(self):
        self.payment_page.verify_no_actual_payment_completed()

    def attempt_search_without_drop_city(self, pickup_query, pickup_suggestion, pickup_date, pickup_time):
        self.home_page.select_trip_type("Outstation One-way")
        self.home_page.select_pickup_city(pickup_query, pickup_suggestion)
        self.home_page.select_pickup_date(pickup_date)
        self.home_page.select_pickup_time(pickup_time)
        self.latest_negative_observation = self.home_page.attempt_invalid_search("missing drop city")
        return self.latest_negative_observation

    def attempt_search_with_unselected_drop_city(self, pickup_query, pickup_suggestion, invalid_drop_text, pickup_date, pickup_time):
        self.home_page.select_trip_type("Outstation One-way")
        self.home_page.select_pickup_city(pickup_query, pickup_suggestion)
        self.home_page.type_raw_drop_text(invalid_drop_text)
        self.home_page.select_pickup_date(pickup_date)
        self.home_page.select_pickup_time(pickup_time)
        self.latest_negative_observation = self.home_page.attempt_invalid_search(
            f"unselected drop city: {invalid_drop_text}"
        )
        return self.latest_negative_observation

    def record_negative_outcome(self, context, case_name):
        observation = dict(self.latest_negative_observation)
        observation["case_name"] = case_name
        observation["scenario"] = context.scenario.name
        context.negative_report_data = observation
        self.home_page.logger.info("Negative test observation: %s", json.dumps(observation, indent=2))

    def verify_listing_not_opened(self):
        observation = self.latest_negative_observation
        assert observation.get("blocked") is True, (
            "Invalid search unexpectedly opened listing page. "
            f"Observed URL: {self.driver.current_url}"
        )
        self.home_page.logger.info("Invalid search was blocked as expected.")
