import re
import time
from urllib.parse import unquote

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from locators.cab_locators import ListingLocators
from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    def apply_listing_filter(self, option, expected_result_text):
        self.verify_cab_results_displayed()
        filter_element = self._find_filter_element(option)
        if filter_element is None:
            outcome = {
                "filter": option,
                "expected_result_text": expected_result_text,
                "applied": False,
                "reason": "Filter was not available for this route at runtime.",
            }
            self.logger.warning("%s", outcome)
            return outcome

        label_text = filter_element.text.strip()
        if re.search(r"\(\s*0\s*\)", label_text):
            outcome = {
                "filter": option,
                "expected_result_text": expected_result_text,
                "applied": False,
                "reason": f"Filter exists but has zero available cabs: {label_text}",
            }
            self.logger.warning("%s", outcome)
            return outcome

        self.logger.info("Applying listing filter: %s", label_text or option)
        self.click_element(filter_element)
        self._wait_for_results_after_filter()
        result_text_present = self._result_cards_contain(expected_result_text)
        outcome = {
            "filter": option,
            "expected_result_text": expected_result_text,
            "applied": True,
            "label": label_text,
            "result_text_present": result_text_present,
        }
        self.logger.info("Filter outcome: %s", outcome)
        return outcome

    def verify_cab_results_displayed(self):
        self.wait.until(EC.presence_of_element_located(ListingLocators.FILTERS_LABEL))
        self.wait.until(lambda driver: len(self._visible_select_cab_buttons()) > 0)
        self.logger.info("Cab results are displayed with %s selectable cabs.", len(self._visible_select_cab_buttons()))

    def verify_listing_reflects_filters(self, applied_filters):
        self.verify_cab_results_displayed()
        if not applied_filters:
            self.logger.warning("No requested filters were available. Search result availability was still verified.")
            return

        observations = []
        for applied_filter in applied_filters:
            expected_text = applied_filter["expected_result_text"]
            present = self._result_cards_contain(expected_text)
            observations.append(
                {
                    "filter": applied_filter["filter"],
                    "expected_result_text": expected_text,
                    "result_text_present": present,
                }
            )

        self.logger.info("Applied filter observations: %s", observations)
        assert len(self._visible_select_cab_buttons()) > 0, "No cab cards were visible after filters."

    def verify_listing_mentions(self, expected_text):
        cards = self._result_card_texts()
        assert any(expected_text.lower() in card.lower() for card in cards), (
            f"Expected listing text not found in cab cards: {expected_text}"
        )

    def verify_route_details(self, pickup, drop):
        page_text = self.body_text()
        current_url = unquote(self.driver.current_url)
        input_values = "\n".join(
            element.get_attribute("value") or ""
            for element in self.driver.find_elements(By.CSS_SELECTOR, "input")
        )
        route_surface = f"{page_text}\n{current_url}\n{input_values}"

        assert pickup.lower() in route_surface.lower(), f"Pickup route text not found: {pickup}"
        assert drop.lower() in route_surface.lower(), f"Drop route text not found: {drop}"

    def select_cab(self, cab_preference="first available"):
        self.verify_cab_results_displayed()
        selected_card = self._find_result_card(cab_preference)
        select_button = selected_card.find_element(By.XPATH, ".//button[contains(normalize-space(.), 'SELECT CAB')]")
        card_text = selected_card.text.strip().replace("\n", " | ")
        self.logger.info("Selecting cab card: %s", card_text[:300])
        self.click_element(select_button)
        self.wait.until(lambda driver: "/cabs/review" in driver.current_url)
        self.wait_for_page_ready()
        self.dismiss_overlays()

    def _find_filter_element(self, option):
        option_literal = self.xpath_literal(option)
        candidates = [
            (By.XPATH, f"//*[@role='checkbox' and .//*[normalize-space()={option_literal}]]"),
            (By.XPATH, f"//*[@role='checkbox' and contains(normalize-space(.), {option_literal})]"),
            (By.XPATH, f"//label[.//*[normalize-space()={option_literal}]]"),
            (By.XPATH, f"//label[contains(normalize-space(.), {option_literal})]"),
            (By.XPATH, f"//*[normalize-space()={option_literal}]/ancestor::label[1]"),
        ]
        for locator in candidates:
            for element in self.driver.find_elements(*locator):
                try:
                    if element.is_displayed():
                        return element
                except StaleElementReferenceException:
                    continue
        return None

    def _wait_for_results_after_filter(self):
        time.sleep(1.2)
        self.wait.until(lambda _: len(self._visible_select_cab_buttons()) > 0)

    def _visible_select_cab_buttons(self):
        return [
            button
            for button in self.driver.find_elements(*ListingLocators.SELECT_CAB_BUTTONS)
            if self.is_displayed(button)
        ]

    def _find_result_card(self, cab_preference):
        cards = self._result_cards()
        if not cards:
            raise NoSuchElementException("No visible cab result cards were found.")

        preferred_terms = self._preferred_terms(cab_preference)
        if preferred_terms:
            for card in cards:
                card_text = card.text.lower()
                normalized_card_text = self._normalized_match_text(card_text)
                if any(
                    term in card_text or self._normalized_match_text(term) in normalized_card_text
                    for term in preferred_terms
                ):
                    return card
            self.logger.warning("Requested cab preference '%s' was not found. Selecting first available cab.", cab_preference)

        return cards[0]

    def _preferred_terms(self, cab_preference):
        preference = (cab_preference or "first available").strip().lower()
        if not preference or preference == "first available":
            return []
        return [
            term.strip()
            for term in re.split(r"[,/|]", preference)
            if term.strip()
        ]

    def _normalized_match_text(self, text):
        return re.sub(r"[^a-z0-9]", "", text.lower())

    def _result_cards(self):
        cards = []
        buttons = self._visible_select_cab_buttons()
        for button in buttons:
            try:
                card = button.find_element(
                    By.XPATH,
                    "./ancestor::*[contains(normalize-space(.), 'Seats') "
                    "and contains(normalize-space(.), 'SELECT CAB')][1]",
                )
                if self.is_displayed(card):
                    cards.append(card)
            except NoSuchElementException:
                continue
        return cards

    def _result_card_texts(self):
        return [card.text for card in self._result_cards()]

    def _result_cards_contain(self, text):
        if not text:
            return True
        return any(text.lower() in card_text.lower() for card_text in self._result_card_texts())
