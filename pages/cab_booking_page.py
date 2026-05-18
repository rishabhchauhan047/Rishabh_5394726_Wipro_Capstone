import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class CabBookingPage(BasePage):
    CABS_MENU = (By.XPATH, "//a[contains(@href,'/cars/') or contains(.,'Cabs')]")
    FROM_INPUT = (By.XPATH, "//input[@type='text']")
    TO_INPUT   = (By.XPATH, "(//input[@type='text'])[2]")
    SEARCH_BUTTON = (By.XPATH, "//button[contains(.,'SEARCH CABS')]")

    @allure.step("Open Goibibo Cabs page")
    def open_goibibo(self):
        self.logger.info("Navigating to https://www.goibibo.com/cars/")
        self.driver.get("https://www.goibibo.com/cars/")
        self.driver.maximize_window()
        time.sleep(8)
        self.logger.debug("Page loaded, window maximised")

    @allure.step("Close popup if present")
    def close_popup(self):
        try:
            popup = self.driver.find_element(By.XPATH, "//span[@role='presentation']")
            popup.click()
            self.logger.info("Popup closed")
        except Exception:
            self.logger.debug("No popup found, continuing")

        time.sleep(5)

        cabs_menu = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href,'/cars/') or contains(.,'Cabs')]")
            )
        )
        self.driver.execute_script("arguments[0].click();", cabs_menu)
        self.logger.info("Cabs menu clicked")
        time.sleep(5)

    @allure.step("Enter From city: {city}")
    def enter_from_city(self, city):
        self.logger.info(f"Entering FROM city: {city}")
        time.sleep(3)
        from_input = self.driver.find_elements(By.XPATH, "//input[@type='text']")[0]
        self.driver.execute_script("arguments[0].click();", from_input)
        time.sleep(2)
        from_input = self.driver.find_elements(By.XPATH, "//input[@type='text']")[0]
        from_input.send_keys(city)
        time.sleep(4)
        suggestion = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//li[contains(.,'{city}')]"))
        )
        self.driver.execute_script("arguments[0].click();", suggestion)
        self.logger.debug(f"FROM city '{city}' selected from suggestions")
        self.take_screenshot(f"from_city_{city}")
        time.sleep(3)

    @allure.step("Enter To city: {city}")
    def enter_to_city(self, city):
        self.logger.info(f"Entering TO city: {city}")
        time.sleep(3)
        to_input = self.driver.find_elements(By.XPATH, "//input[@type='text']")[1]
        self.driver.execute_script("arguments[0].click();", to_input)
        time.sleep(2)
        to_input = self.driver.find_elements(By.XPATH, "//input[@type='text']")[1]
        to_input.send_keys(city)
        time.sleep(4)
        suggestion = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//li[contains(.,'{city}')]"))
        )
        self.driver.execute_script("arguments[0].click();", suggestion)
        self.logger.debug(f"TO city '{city}' selected from suggestions")
        self.take_screenshot(f"to_city_{city}")
        time.sleep(3)

    @allure.step("Click Search Cabs")
    def search_cabs(self):
        self.logger.info("Clicking SEARCH CABS button")
        time.sleep(5)
        search_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'SEARCH CABS')]"))
        )
        self.driver.execute_script("arguments[0].click();", search_button)
        self.logger.info("Search button clicked — waiting for results")
        self.take_screenshot("search_results")
        time.sleep(10)

    @allure.step("Select first available cab")
    def select_first_cab(self):
        self.logger.info("Looking for SELECT CAB buttons")
        time.sleep(10)
        self.driver.execute_script("window.scrollBy(0,800)")
        time.sleep(5)
        buttons = self.driver.find_elements(By.XPATH, "//button[contains(.,'SELECT CAB')]")
        self.logger.info(f"Cab buttons found: {len(buttons)}")

        if buttons:
            self.driver.execute_script("arguments[0].click();", buttons[0])
            self.logger.info("First cab selected successfully")
            self.take_screenshot("cab_selected")
        else:
            self.logger.warning("No SELECT CAB button found on the page")
            self.take_screenshot("no_cab_found")