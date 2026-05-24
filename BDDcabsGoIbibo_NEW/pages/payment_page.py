from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from locators.cab_locators import PaymentLocators
from pages.base_page import BasePage


class PaymentPage(BasePage):
    def verify_payment_page_displayed(self):
        def payment_surface_loaded(driver):
            try:
                body = driver.find_element(By.TAG_NAME, "body").text
                return "payments.goibibo.com" in driver.current_url and "Payment Options" in body
            except Exception:
                return False

        WebDriverWait(self.driver, 80).until(payment_surface_loaded)
        self.wait_visible(PaymentLocators.PAYMENT_OPTIONS)
        self.logger.info("Payment page is displayed: %s", self.driver.current_url)

    def select_upi_option(self):
        self.verify_payment_page_displayed()
        candidates = self.visible_elements(PaymentLocators.UPI_OPTION)
        if candidates:
            self.click_element(candidates[0])
        self.wait.until(lambda driver: "UPI" in driver.find_element(By.TAG_NAME, "body").text)
        self.logger.info("UPI payment option is selected or already active.")

    def click_generate_qr(self):
        self.verify_payment_page_displayed()
        self.select_upi_option()
        qr_buttons = self.visible_elements(PaymentLocators.QR_ACTION_BUTTON)
        if qr_buttons:
            button_text = qr_buttons[0].text.strip() or "QR action"
            self.click_element(qr_buttons[0])
            self.logger.info("Clicked UPI QR action button: %s", button_text)
        elif self._qr_modal_visible():
            self.logger.info("UPI QR modal was already visible.")
        else:
            raise AssertionError("No Generate QR or View QR button was visible on the UPI payment page.")

        self.verify_upi_qr_displayed()

    def verify_upi_qr_displayed(self):
        def qr_visible(driver):
            try:
                body = driver.find_element(By.TAG_NAME, "body").text
                if "Scan QR to Pay" in body or "QR expiring in" in body:
                    return True
                qr_images = driver.find_elements(*PaymentLocators.QR_IMAGE)
                return any(image.is_displayed() for image in qr_images)
            except Exception:
                return False

        WebDriverWait(self.driver, 35).until(qr_visible)
        self.wait_visible(PaymentLocators.QR_MODAL_TEXT)
        self.logger.info("UPI QR payment request is displayed.")

    def verify_no_actual_payment_completed(self):
        body = self.body_text()
        forbidden_success_text = [
            "Payment Successful",
            "Booking Confirmed",
            "Payment completed",
            "Thank you for your payment",
        ]
        assert all(text.lower() not in body.lower() for text in forbidden_success_text), (
            "Unexpected payment success state appeared."
        )
        assert "payments.goibibo.com/checkout" in self.driver.current_url, "Browser left checkout unexpectedly."
        assert any(
            text.lower() in body.lower()
            for text in ["UPI", "Scan QR", "VIEW QR", "QR expiring in", "payment link"]
        ), "Payment checkout was not in a UPI/QR state."
        self.logger.info("No actual payment was completed; test stopped at QR request.")

    def _qr_modal_visible(self):
        try:
            return bool(self.visible_elements(PaymentLocators.QR_MODAL_TEXT))
        except TimeoutException:
            return False
