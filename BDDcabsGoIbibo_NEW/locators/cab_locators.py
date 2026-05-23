from selenium.webdriver.common.by import By


class HomeLocators:
    PAGE_HEADING = (By.XPATH, "//h1[normalize-space()='Book Online Cab']")
    PICKUP_INPUT = (By.CSS_SELECTOR, "input[placeholder*='Pickup']")
    DROP_INPUT = (By.CSS_SELECTOR, "input[placeholder*='Drop']")
    SEARCH_CABS_BUTTON = (By.XPATH, "//button[normalize-space()='SEARCH CABS']")
    DATE_BLOCK = (By.XPATH, "//*[contains(@class, 'PickupDate') or normalize-space()='Pickup Date']")
    TIME_BLOCK = (By.XPATH, "//*[contains(@class, 'PickupTime') or normalize-space()='Pickup Time']")
    CALENDAR_WRAPPER = (By.XPATH, "//*[contains(@class, 'CalendarBlockOuterWrapper')]")
    CALENDAR_MONTH_LABEL = (By.CSS_SELECTOR, "[class*='MonthNamePara']")
    CALENDAR_NEXT = (By.CSS_SELECTOR, "[class*='MonthChangeRightArrowDiv']")
    CALENDAR_PREVIOUS = (By.CSS_SELECTOR, "[class*='MonthChangeLeftArrowDiv']")
    TIME_LIST = (By.XPATH, "//ul[.//*[contains(normalize-space(), '00:00 AM')]]")


class ListingLocators:
    FILTERS_LABEL = (By.XPATH, "//*[contains(., 'Filters')]")
    SELECT_CAB_BUTTONS = (By.XPATH, "//button[contains(normalize-space(.), 'SELECT CAB')]")


class ReviewLocators:
    REVIEW_TITLE = (By.XPATH, "//*[contains(normalize-space(.), 'Review booking')]")
    TRAVELLER_DETAILS = (By.XPATH, "//*[contains(normalize-space(.), 'Traveller Details')]")
    PICKUP_LOCATION_INPUT = (By.XPATH, "//input[@label='ENTER PICKUP LOCATION']")
    FULL_NAME_INPUT = (By.XPATH, "//input[@label='FULL NAME']")
    MOBILE_INPUT = (By.CSS_SELECTOR, "input[type='number']")
    EMAIL_INPUT = (By.XPATH, "//input[@label='EMAIL ID' or @type='email']")
    PAY_NOW_BUTTON = (By.XPATH, "//button[contains(normalize-space(.), 'PAY NOW')]")
    LOCATION_SUGGESTION_LIST = (By.XPATH, "//*[@role='listbox']")


class PaymentLocators:
    PAYMENT_OPTIONS = (By.XPATH, "//*[contains(normalize-space(.), 'Payment Options')]")
    UPI_OPTION = (
        By.XPATH,
        "//*[contains(normalize-space(.), 'UPI Options') "
        "and contains(normalize-space(.), 'Pay directly') "
        "and not(self::html) and not(self::body)]",
    )
    QR_ACTION_BUTTON = (
        By.XPATH,
        "//button[contains(translate(normalize-space(.), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'GENERATE QR') "
        "or contains(translate(normalize-space(.), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'VIEW QR')]",
    )
    QR_MODAL_TEXT = (
        By.XPATH,
        "//*[contains(normalize-space(.), 'Scan QR to Pay') "
        "or contains(normalize-space(.), 'QR expiring in') "
        "or contains(normalize-space(.), 'Scan & approve using your UPI app')]",
    )
    QR_IMAGE = (
        By.XPATH,
        "//img[contains(@alt, 'upi-qr-code') or starts-with(@src, 'data:image')]",
    )
    CANCEL_QR_BUTTON = (By.XPATH, "//button[contains(normalize-space(.), 'CANCEL')]")
