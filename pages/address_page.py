import json
import time
import pandas as pd
import allure
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from appium.webdriver.webdriver import WebDriver
from constants.locator.address_locator import AddressLocator
from constants.locator.course_create_locator import CourseCreateLocator
from constants.tenant_config import TenantConfig, TenantConfiguration
from pages.base_page import BasePage
from pages.course_create_page import CourseCreatePage
from pages.my_events_page import MyEventsPage
from utils.time_zone_util import TimezoneFormatter
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig


class AddressPage(BasePage):
    """
    Page object for Course Creation page.
    
    Uses TenantConfig for all tenant-specific logic to ensure consistency
    and maintainability. All field labels and feature flags are centralized.
    """

    def __init__(self, driver: WebDriver, platform: str):
        super().__init__(driver, platform)
        self.locator = AddressLocator.get_locators(platform)
        from constants.message.address_message import AddressMessage
        self.course_create = CourseCreatePage(driver, platform)
        self.address_message = AddressMessage.get_message()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        
    def click_create_address_button(self):
        self.click_element(self.locator["create_address_button"])

    def scroll_to_state_and_click(self, state_name, max_swipes=10):
        for i in range(max_swipes):
            try:
                element = self.build_locator(self.locator["state_list"], state_name)
                print(f"Element: {element}")
                self.click_element(element,5)
                self.logger.info(f"State '{state_name}' selected")
                return True

            except:
                prev_source = self.driver.page_source

                # 👇 Scroll ONLY inside state list container
                self.driver.swipe(540, 2100, 540, 1500, 800)

                new_source = self.driver.page_source

                # ❌ No more scroll possible
                if prev_source == new_source:
                    raise Exception(f"State '{state_name}' not found after scrolling")

        raise Exception(f"State '{state_name}' not found after {max_swipes} swipes")


    def select_state(self, value):
        try:
            self.click_element(self.locator["state_dropdown"])
            time.sleep(2)

            # 👇 Direct scroll instead of search dependency
            self.scroll_to_state_and_click(value)

        except Exception as e:
            raise Exception(f"Unable to select state as {value}: {str(e)}")


    def handle_address(self, data):
        """Fill address form, submit, then validate success or extract validation errors from the page."""
        try:
            print(f"Data: {data}")
            if data.get("addressName"):
                self.course_create.enter_addressName(data.get("addressName"))
                self.logger.info(f"Entered address Name: {data.get('addressName')}")

            if data.get("zipcode"):
                self.course_create.enter_zipcode(data.get("zipcode"), data.get("tenant"))
                self.logger.info(f"Entered zipcode: {data.get('zipcode')}")

            if data.get("state") and data.get("tenant").lower() == "us":
                self.select_state(data.get("state"))
                self.logger.info(f"Entered state: {data.get('state')}")

            if data.get("city"):
                self.course_create.enter_city(data.get("city"), data.get("tenant"))
                self.logger.info(f"Entered city: {data.get('city')}")

            if data.get("address"):
                self.course_create.enter_address(data.get("address"))
                self.logger.info(f"Entered address: {data.get('address')}")

            if self.is_displayed(self.locator["create_button"]):
                self.course_create.click_element(self.locator["create_button"])
                # Allow snackbar / inline validation to appear in page source
                time.sleep(1.5)

            content = self.extract_page_contents()
            success = self._address_save_succeeded(content)
            msg = self._format_outcome_message(success, content)
            if not success:
                self.logger.warning("Address flow did not succeed. %s", msg)
            return success, msg
        except Exception as e:
            return False, f"Address creation failed: {str(e)}"

    def _address_save_succeeded(self, content: List[str]) -> bool:
        """True if success copy appears in any extracted page fragment (substring match)."""
        success = self.address_message.get("address_success_msg") or ""
        if not success:
            return False
        return any(success in line for line in content)

    # Substrings that usually indicate inline validation / errors (not nav chrome)
    _ERROR_TEXT_HINTS = (
        "must ",
        "invalid",
        "error",
        "required",
        "enter a",
        "enter ",
        "please ",
        "cannot ",
        "can't ",
        "failed",
        "try again",
        "character",
        "digit",
        "zip",
        "pin",
        "field",
        "missing",
        "empty",
        "not valid",
        "wrong",
        "incorrect",
    )

    def _format_outcome_message(self, success: bool, content: List[str]) -> str:
        if success:
            success_text = self.address_message["address_success_msg"]
            for line in content:
                if success_text in line:
                    return line.strip()
            return success_text
        primary, preview = self._extract_validation_error(content)
        if preview:
            return f"{primary}\n---\nOther visible text: {preview}"
        return primary

    def _lines_that_look_like_errors(self, content: List[str]) -> List[str]:
        out: List[str] = []
        for line in content:
            s = line.strip()
            if len(s) < 4 or len(s) > 280:
                continue
            low = s.lower()
            if any(h in low for h in self._ERROR_TEXT_HINTS):
                out.append(s)
        # Dedupe preserving order
        seen = set()
        unique = []
        for s in out:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        return unique

    def _summarize_visible_text(self, content: List[str], max_items: int = 45) -> str:
        if not content:
            return "(no text extracted from page source)"
        chunk = content[:max_items]
        return " | ".join(chunk)

    def _extract_validation_error(self, content: List[str]) -> Tuple[str, str]:
        """
        Map on-screen text to known validation messages from AddressMessage (values, not dict keys).
        Always prefers quoting the actual UI string the user would see.

        Returns:
            (primary_message_for_asserts/logs, optional_secondary_excerpt)
        """
        try:
            for key, expected in self.address_message.items():
                if key == "address_success_msg" or not expected:
                    continue
                for line in content:
                    if expected in line:
                        ui = line.strip()
                        return f'UI error (matched "{expected}"): {ui}', ""
                    if len(line) >= 4 and line in expected:
                        ui = line.strip()
                        return f'UI error: {ui}', ""

            error_like = self._lines_that_look_like_errors(content)
            if error_like:
                joined = " | ".join(error_like[:12])
                return f"UI validation / error text: {joined}", ""

            preview = self._summarize_visible_text(content)
            return (
                "No known or heuristic error line found; check page state.",
                preview,
            )
        except Exception as e:
            self.logger.error(
                f"Exception while extracting validation error from page: {e}"
            )
            return f"Unable to read validation state: {e}", ""

    def get_final_error_msg(self, content: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        Backward-compatible helper: returns (primary_error_message, page_excerpt_or_empty).

        If ``content`` is omitted, the current page is scraped again.
        """
        if content is None:
            content = self.extract_page_contents()
        return self._extract_validation_error(content)
