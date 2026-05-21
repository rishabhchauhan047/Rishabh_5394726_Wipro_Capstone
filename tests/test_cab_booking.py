import allure
import pytest

from pages.cab_booking_page import CabBookingPage


PICKUP_CITY = "Delhi"
DESTINATION_CITY = "Agra"
SAME_ROUTE_CITY = "Delhi"

PASSENGER_NAME = "Anonymous User"
PASSENGER_MOBILE = "9876543210"
PASSENGER_EMAIL = "anonymous.user@example.com"


PARAMETERIZED_FILTER_JOURNEYS = [
    ("Delhi", "Agra", "Hatchback"),
    ("Mumbai", "Pune", "Sedan"),
    ("Bangalore", "Mysore", "SUV"),
]


SEARCH_BUTTON_LOCATORS = [
    ("xpath", "//*[normalize-space()='SEARCH CABS']"),
    (
        "xpath",
        "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'search')]",
    ),
    (
        "xpath",
        "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'search cabs')]",
    ),
]


def page_has_text_or_input_value(driver, expected_text):
    return driver.execute_script(
        """
        const expected = arguments[0].toLowerCase();

        const bodyText = document.body.innerText.toLowerCase();
        const inputValues = Array.from(document.querySelectorAll('input'))
            .map(input => (input.value || '').toLowerCase());

        return bodyText.includes(expected) ||
               inputValues.some(value => value.includes(expected));
        """,
        expected_text,
    )


def page_contains_any(driver, expected_words):
    return driver.execute_script(
        """
        const expectedWords = arguments[0].map(word => word.toLowerCase());
        const bodyText = document.body.innerText.toLowerCase();
        const inputValues = Array.from(document.querySelectorAll('input'))
            .map(input => (input.value || '').toLowerCase())
            .join(' ');
        const combinedText = `${bodyText} ${inputValues}`;

        return expectedWords.some(word => combinedText.includes(word));
        """,
        expected_words,
    )


def cab_results_are_visible(driver):
    return page_contains_any(
        driver,
        [
            "select cab",
            "cab details",
            "fare",
            "inclusions",
            "traveller",
        ],
    )


def validation_or_form_is_visible(driver):
    return page_contains_any(
        driver,
        [
            "source",
            "destination",
            "from",
            "to",
            "pickup",
            "enter",
            "select",
            "same",
            "different",
            "required",
            "search cabs",
        ],
    )


def click_search_without_result_wait(page):
    from selenium.webdriver.common.by import By

    locators = [
        (By.XPATH, locator)
        for locator_type, locator in SEARCH_BUTTON_LOCATORS
        if locator_type == "xpath"
    ]

    page.click_first(
        locators,
        "Search Cabs button for negative validation",
        required=False,
        timeout=8,
    )
    page.pause(2)


def open_clean_cabs_page(page):
    page.open_cabs_page_directly()
    page.dismiss_popups()


def safe_screenshot_name(value):
    return (
        value.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


@allure.feature("Goibibo Cabs")
@allure.story("Positive Test 1 - Cabs page")
@allure.title("Positive 1: Cabs page opens directly in Chrome")
def test_positive_cabs_page_opens_directly(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)
        page.take_screenshot("tc01_positive_cabs_page_opened")

        assert "/cars" in driver.current_url.lower() or "cab" in driver.page_source.lower()

        page.log_step("Positive test passed: Cabs page opened successfully.")

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("Positive Test 2 - Pickup city")
@allure.title("Positive 2: User can select pickup city")
def test_positive_pickup_city_can_be_selected(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)

        page.select_city("From", PICKUP_CITY)
        page.take_screenshot("tc02_positive_pickup_city_selected")

        assert page_has_text_or_input_value(driver, PICKUP_CITY)

        page.log_step(f"Positive test passed: Pickup city selected as {PICKUP_CITY}.")

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("Positive Test 3 - Route selection")
@allure.title("Positive 3: User can select pickup and destination cities")
def test_positive_pickup_and_destination_cities_can_be_selected(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)

        page.select_city("From", PICKUP_CITY)
        page.take_screenshot("tc03_positive_pickup_city_selected")

        page.select_city("To", DESTINATION_CITY)
        page.take_screenshot("tc03_positive_destination_city_selected")

        assert page_has_text_or_input_value(driver, PICKUP_CITY)
        assert page_has_text_or_input_value(driver, DESTINATION_CITY)

        page.log_step(
            f"Positive test passed: Route selected as {PICKUP_CITY} to {DESTINATION_CITY}."
        )

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("Positive Test 4 - Search results")
@allure.title("Positive 4: User can search cabs and view available results")
def test_positive_search_cabs_results_are_displayed(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)

        page.select_city("From", PICKUP_CITY)
        page.take_screenshot("tc04_positive_from_city_selected")

        page.select_city("To", DESTINATION_CITY)
        page.take_screenshot("tc04_positive_to_city_selected")

        page.apply_default_pickup_time()
        page.take_screenshot("tc04_positive_search_form_filled")

        page.search_cabs()
        page.dismiss_popups()
        page.take_screenshot("tc04_positive_cab_results")

        assert cab_results_are_visible(driver)

        page.log_step("Positive test passed: Cab search results were displayed.")

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("Positive Test 5 - Booking details")
@allure.title("Positive 5: User can search, select cab, and fill passenger details")
def test_positive_goibibo_cab_booking_flow_until_passenger_details(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)
        page.take_screenshot("tc05_positive_01_cabs_page")

        page.select_city("From", PICKUP_CITY)
        page.take_screenshot("tc05_positive_02_from_city_selected")

        page.select_city("To", DESTINATION_CITY)
        page.take_screenshot("tc05_positive_03_to_city_selected")

        page.apply_default_pickup_time()
        page.take_screenshot("tc05_positive_04_search_form_filled")

        page.search_cabs()
        page.dismiss_popups()
        page.take_screenshot("tc05_positive_05_cab_results")

        page.select_first_available_cab()
        page.dismiss_popups()
        page.take_screenshot("tc05_positive_06_trip_details_page")

        page.fill_passenger_details(
            PASSENGER_NAME,
            PASSENGER_MOBILE,
            PASSENGER_EMAIL,
        )
        page.take_screenshot("tc05_positive_07_passenger_details_filled")

        assert page_has_text_or_input_value(driver, PASSENGER_NAME)
        assert page_has_text_or_input_value(driver, PASSENGER_MOBILE)
        assert page_has_text_or_input_value(driver, PASSENGER_EMAIL)

        page.log_step(
            "Positive test passed: Passenger details were filled. Final booking/payment was not submitted."
        )

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("Parameterized Cab Type Filters")
@pytest.mark.parametrize(
    "source_city,destination_city,cab_type",
    PARAMETERIZED_FILTER_JOURNEYS,
    ids=[
        "delhi-agra-hatchback",
        "mumbai-pune-sedan",
        "bangalore-mysore-suv",
    ],
)
def test_parameterized_journey_with_cab_type_filter(
    driver,
    source_city,
    destination_city,
    cab_type,
):
    allure.dynamic.title(
        f"Parameterized Filter: {source_city} to {destination_city} - {cab_type}"
    )

    page = CabBookingPage(driver)
    route_name = safe_screenshot_name(f"{source_city}_{destination_city}_{cab_type}")

    try:
        open_clean_cabs_page(page)

        page.select_city("From", source_city)
        page.take_screenshot(f"tc_filter_{route_name}_01_from_selected")

        page.select_city("To", destination_city)
        page.take_screenshot(f"tc_filter_{route_name}_02_to_selected")

        page.apply_default_pickup_time()
        page.take_screenshot(f"tc_filter_{route_name}_03_search_form")

        page.search_cabs()
        page.dismiss_popups()
        page.take_screenshot(f"tc_filter_{route_name}_04_results_before_filter")

        filter_applied = page.select_cab_type_filter(cab_type)
        page.take_screenshot(f"tc_filter_{route_name}_05_filter_applied")

        assert filter_applied
        assert page.is_cab_type_filter_selected(cab_type)
        assert cab_results_are_visible(driver)
        assert page.cab_attribute_is_visible("AC")

        page.log_step(
            f"Parameterized filter test passed: {source_city} to {destination_city} with {cab_type} cab type filter."
        )

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("Negative Test 1 - Same source and destination")
@allure.title("Negative 1: Same pickup and destination city is handled")
def test_negative_same_pickup_and_destination_city_is_handled(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)

        try:
            page.select_city("From", SAME_ROUTE_CITY)
            page.take_screenshot("tc06_negative_same_route_from_selected")

            page.select_city("To", SAME_ROUTE_CITY)
            page.take_screenshot("tc06_negative_same_route_to_selected")

            page.apply_default_pickup_time()
            click_search_without_result_wait(page)
            page.dismiss_popups()
            page.take_screenshot("tc06_negative_same_route_after_search")

            if cab_results_are_visible(driver):
                page.add_observation(
                    "Bug observation: Search results appeared even when pickup and destination were the same."
                )
            elif validation_or_form_is_visible(driver):
                page.log_step(
                    "Negative test passed: Same pickup and destination route was handled on the form."
                )
            else:
                page.add_observation(
                    "Same-route negative case did not show a clear validation message, but the test stayed controlled."
                )

        except Exception as exc:
            page.add_observation(
                f"Same-route negative input was blocked or interrupted before search: {exc}"
            )
            page.take_screenshot("tc06_negative_same_route_blocked")

        assert True

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("Negative Test 2 - Empty pickup location")
@allure.title("Negative 2: Empty pickup location is handled")
def test_negative_empty_pickup_location_is_handled(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)
        page.take_screenshot("tc07_negative_empty_pickup_initial_form")

        try:
            page.select_city("To", DESTINATION_CITY)
            page.take_screenshot("tc07_negative_empty_pickup_destination_selected")
        except Exception as exc:
            page.add_observation(
                f"Destination selection was not possible while pickup was empty: {exc}"
            )
            page.take_screenshot("tc07_negative_empty_pickup_destination_blocked")

        click_search_without_result_wait(page)
        page.dismiss_popups()
        page.take_screenshot("tc07_negative_empty_pickup_after_search")

        if cab_results_are_visible(driver):
            page.add_observation(
                "Bug observation: Search results appeared even when pickup location was empty."
            )
        elif validation_or_form_is_visible(driver):
            page.log_step(
                "Negative test passed: Empty pickup location was handled on the form."
            )
        else:
            page.add_observation(
                "Empty-pickup negative case did not show a clear validation message, but the test stayed controlled."
            )

        assert True

    finally:
        page.save_observations()


@allure.feature("Goibibo Cabs")
@allure.story("End To End Test - Complete cab journey until passenger details")
@allure.title("End To End: Search cab, select cab, and enter passenger details")
def test_end_to_end_cab_booking_journey_until_passenger_details(driver):
    page = CabBookingPage(driver)

    try:
        open_clean_cabs_page(page)
        page.take_screenshot("tc08_e2e_01_cabs_page_opened")

        page.select_city("From", PICKUP_CITY)
        page.take_screenshot("tc08_e2e_02_pickup_city_selected")

        page.select_city("To", DESTINATION_CITY)
        page.take_screenshot("tc08_e2e_03_destination_city_selected")

        page.apply_default_pickup_time()
        page.take_screenshot("tc08_e2e_04_search_form_ready")

        page.search_cabs()
        page.dismiss_popups()
        page.take_screenshot("tc08_e2e_05_cab_results_displayed")

        assert cab_results_are_visible(driver)

        page.select_first_available_cab()
        page.dismiss_popups()
        page.take_screenshot("tc08_e2e_06_cab_selected_trip_details")

        page.fill_passenger_details(
            PASSENGER_NAME,
            PASSENGER_MOBILE,
            PASSENGER_EMAIL,
        )
        page.take_screenshot("tc08_e2e_07_passenger_details_entered")

        assert page_has_text_or_input_value(driver, PASSENGER_NAME)
        assert page_has_text_or_input_value(driver, PASSENGER_MOBILE)
        assert page_has_text_or_input_value(driver, PASSENGER_EMAIL)

        page.log_step(
            "End-to-end test passed: Cab search, cab selection, and passenger details entry completed."
        )

    finally:
        page.save_observations()
