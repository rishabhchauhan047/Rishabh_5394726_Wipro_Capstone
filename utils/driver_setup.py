from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():

    chrome_options = Options()

    chrome_options.add_argument("--start-maximized")

    chrome_options.add_argument("--disable-notifications")

    chrome_options.add_argument("--disable-popup-blocking")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument("--remote-debugging-port=9222")

    chrome_options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    chrome_options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    driver.implicitly_wait(10)

    return driver