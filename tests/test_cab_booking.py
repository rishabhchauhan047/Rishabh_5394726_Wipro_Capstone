import time
import allure
from pages.cab_booking_page import CabBookingPage
from utils.logger import get_logger

logger = get_logger("test_cab_booking")


@allure.feature("Cab Booking")
@allure.story("Search and Select Cab")
@allure.title("Book a cab from Delhi to Agra")
@allure.severity(allure.severity_level.CRITICAL)
def test_cab_booking(driver):

    logger.info("=== TEST START: test_cab_booking ===")

    cab = CabBookingPage(driver)

    with allure.step("Open Goibibo cabs page"):
        logger.info("Opening Goibibo cabs page")
        cab.open_goibibo()

    with allure.step("Close popup if present"):
        logger.info("Attempting to close popup")
        cab.close_popup()

    with allure.step("Enter FROM city: Delhi"):
        logger.info("Entering FROM city: Delhi")
        cab.enter_from_city("Delhi")

    with allure.step("Enter TO city: Agra"):
        logger.info("Entering TO city: Agra")
        cab.enter_to_city("Agra")

    with allure.step("Search for cabs"):
        logger.info("Clicking search cabs")
        cab.search_cabs()

    with allure.step("Select first available cab"):
        logger.info("Selecting first cab")
        cab.select_first_cab()

    logger.info("Waiting for booking confirmation page")
    time.sleep(10)

    logger.info("=== TEST END: test_cab_booking ===")