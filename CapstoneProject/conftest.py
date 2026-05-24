from pathlib import Path

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="function")
def driver():
    Path("screenshots").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("allure-results").mkdir(exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--lang=en-US")

    browser = webdriver.Chrome(options=chrome_options)
    browser.set_page_load_timeout(60)

    yield browser

    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )