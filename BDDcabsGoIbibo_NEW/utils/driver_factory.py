from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


def create_driver(browser_name="chrome", headless=False):
    browser = browser_name.strip().lower()

    if browser == "chrome":
        options = ChromeOptions()
        _add_common_options(options, headless)
        driver = webdriver.Chrome(options=options)
    elif browser == "edge":
        options = EdgeOptions()
        _add_common_options(options, headless)
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}. Use chrome or edge.")

    driver.set_page_load_timeout(70)
    driver.implicitly_wait(0)
    if not headless:
        driver.maximize_window()
    return driver


def _add_common_options(options, headless):
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--lang=en-IN")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2,
        },
    )
