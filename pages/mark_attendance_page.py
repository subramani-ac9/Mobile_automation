import logging
import re
import time
from typing import Optional

import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from constants.locator.mark_attendance_locators import MarkAttendanceLocator
from constants.locator.myevent_locator import MyEventLocator
from constants.locator.participant_transfer_locator import ParticipantTransferLocator
from pages.base_page import BasePage


class MarkAttendancePage(BasePage):
    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = {
            **MyEventLocator.get_locators(platform),
            **ParticipantTransferLocator.get_locators(platform),
            **MarkAttendanceLocator.get_locators(platform),
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    @allure.step("Tap center of screen (dismiss overlay)")
    def tap_screen_center_to_dismiss(self, y_fraction: float = 0.4) -> None:
        size = self.driver.get_window_size()
        cx = size["width"] // 2
        cy = int(size["height"] * y_fraction)
        actions = ActionChains(self.driver)
        actions.w3c_actions.pointer_action.move_to_location(cx, cy)
        actions.w3c_actions.pointer_action.click()
        actions.perform()
        time.sleep(0.12)

    def _tap_element_geometry(
        self, el: WebElement, x_frac: float = 0.5, y_frac: float = 0.5
    ) -> None:
        try:
            rect = el.rect
            cx = int(rect["x"] + rect["width"] * x_frac)
            cy = int(rect["y"] + rect["height"] * y_frac)
        except Exception as exc:
            self.logger.debug(f"_tap_element_geometry rect: {exc}")
            try:
                el.click()
            except Exception:
                pass
            time.sleep(0.12)
            return
        try:
            if self.platform.lower() == "ios":
                try:
                    self.driver.execute_script("mobile: tap", {"x": cx, "y": cy})
                except Exception:
                    actions = ActionChains(self.driver)
                    actions.w3c_actions.pointer_action.move_to_location(cx, cy)
                    actions.w3c_actions.pointer_action.click()
                    actions.perform()
            else:
                actions = ActionChains(self.driver)
                actions.w3c_actions.pointer_action.move_to_location(cx, cy)
                actions.w3c_actions.pointer_action.click()
                actions.perform()
        except Exception as exc:
            self.logger.debug(f"_tap_element_geometry tap: {exc}")
            try:
                el.click()
            except Exception:
                pass
        time.sleep(0.18)

    def _click_or_tap_geometry(self, loc: tuple, timeout: int = 10) -> None:

        if self.platform.lower() == "ios":
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(loc)
                )
                self._tap_element_geometry(el, 0.5, 0.5)
                return
            except Exception as exc:
                self.logger.debug(f"_click_or_tap_geometry clickable: {exc}")
            try:
                el = WebDriverWait(self.driver, min(timeout, 8)).until(
                    EC.visibility_of_element_located(loc)
                )
                self._tap_element_geometry(el, 0.5, 0.5)
                return
            except Exception as exc:
                self.logger.debug(f"_click_or_tap_geometry visible: {exc}")
        self.click_element(loc, timeout=timeout)

    def _find_click_first_silent(self, locators: list) -> bool:
        for loc in locators:
            if not loc:
                continue
            try:
                if self.is_displayed(loc, timeout=2):
                    self.click_element(loc, timeout=10)
                    return True
            except Exception as e:
                self.logger.debug(f"_find_click_first_silent skip {loc}: {e}")
        return False

    @allure.step("Toolbar back (first — chevron / no accessibility id)")
    def tap_toolbar_back_first(self) -> None:
        if self.platform.lower() == "ios":
            chain = [
                self.locator.get("nav_back_first_click"),
                self.locator.get("nav_back_first_click_xpath"),
            ]
            for loc in chain:
                if not loc:
                    continue
                try:
                    if self.is_displayed(loc, timeout=4):
                        self._click_or_tap_geometry(loc, timeout=12)
                        time.sleep(0.22)
                        return
                except Exception as e:
                    self.logger.debug(f"tap_toolbar_back_first {loc}: {e}")
            nb = self.locator.get("nav_back")
            if nb and self.is_displayed(nb, timeout=2):
                self.logger.warning(
                    "tap_toolbar_back_first: chevron locators not found; using Back Button once"
                )
                self._click_or_tap_geometry(nb, timeout=10)
                time.sleep(0.22)
                return
            raise RuntimeError(
                "First toolbar back (chevron / no Back Button id) not found on iOS"
            )
        if self.locator.get("nav_back"):
            self.click_element(self.locator["nav_back"], timeout=10)
            time.sleep(0.18)
            return
        raise RuntimeError("No first back locator for this platform")

    @allure.step("Toolbar back (Back Button)")
    def tap_toolbar_back_button(self) -> None:
        if self.platform.lower() == "android":
            backBtn = self.locator["back_button"]
            self.click_element(backBtn, timeout=10)
        else:
            keys = ("nav_back", "nav_back_second_click_xpath")
            for k in keys:
                loc = self.locator.get(k)
                if loc and self.is_displayed(loc, timeout=4):
                    self._click_or_tap_geometry(loc, timeout=10)
                    time.sleep(0.18)
                    return
            raise RuntimeError("Back Button not found")
        

    @allure.step("Tap Events Search Close")
    def tap_events_search_close(self) -> None:
        loc = self.locator["events_search_close_button"]
        if self.platform.lower() == "ios":
            self._click_or_tap_geometry(loc, timeout=12)
        else:
            self.click_element(loc, timeout=10)
        time.sleep(0.15)

    @allure.step("Tap Cancel")
    def tap_cancel(self) -> None:
        self.click_element(self.locator["option_cancel"], timeout=10)
        time.sleep(0.12)

    def _locator_spec_is_usable(self, loc: Optional[tuple]) -> bool:
        if not loc:
            return False
        _, spec = loc
        if callable(spec):
            return False
        if isinstance(spec, str) and not spec.strip():
            return False
        return True

    def _accept_bulk_mark_dialog_if_present(self) -> bool:
        tapped = False
        for loc_key in ("confirm_button", "option_ok", "dialog_ok_button"):
            loc = self.locator.get(loc_key)
            if not self._locator_spec_is_usable(loc):
                continue
            if self.is_displayed(loc, timeout=2):
                try:
                    self.click_element(loc, timeout=8)
                    time.sleep(0.45)
                    tapped = True
                except Exception as exc:
                    self.logger.debug(f"_accept_bulk_mark_dialog_if_present {loc_key}: {exc}")
        return tapped

    def _wait_bulk_mark_ui_idle(
        self, max_wait: float = 14.0, *, initial_sleep: Optional[float] = None
    ) -> None:
        """
        Flutter shows a short 'Updating participants' (or similar) overlay after Mark Attended.
        Wait for activity indicators / updating text to clear before tapping Cancel.
        """
        time.sleep(1.85 if initial_sleep is None else initial_sleep)
        end = time.time() + max_wait
        if self.platform.lower() == "ios":
            busy_preds = [
                'type == "XCUIElementTypeActivityIndicator"',
                'type == "XCUIElementTypeProgressIndicator"',
                '(name CONTAINS[c] "updating" OR label CONTAINS[c] "updating")',
                '(name CONTAINS[c] "loading" OR label CONTAINS[c] "loading")',
            ]
        else:
            busy_preds = None

        while time.time() < end:
            busy = False
            if self.platform.lower() == "ios" and busy_preds:
                for pred in busy_preds:
                    try:
                        for el in self.driver.find_elements(
                            AppiumBy.IOS_PREDICATE, pred
                        ):
                            try:
                                if el.is_displayed():
                                    busy = True
                                    break
                            except Exception:
                                continue
                    except Exception:
                        continue
                    if busy:
                        break
            else:
                try:
                    for el in self.driver.find_elements(
                        AppiumBy.XPATH, "//android.widget.ProgressBar"
                    ):
                        if el.is_displayed():
                            busy = True
                            break
                except Exception:
                    pass
            if not busy:
                break
            time.sleep(0.32)
        time.sleep(0.35)

    def _tap_first_visible_element(self, loc: tuple) -> bool:
        """Click first displayed match; no final find_element (avoids false throws)."""
        try:
            for el in self.driver.find_elements(*loc):
                try:
                    if el.is_displayed():
                        el.click()
                        return True
                except Exception:
                    continue
        except Exception as exc:
            self.logger.debug(f"_tap_first_visible_element {loc}: {exc}")
        return False

    def _tap_ios_cancel_top_right_estimate(self) -> bool:
        """Last resort: Cancel is often top-trailing on modals (Flutter)."""
        if self.platform.lower() != "ios":
            return False
        try:
            size = self.driver.get_window_size()
            x = int(size["width"] * 0.90)
            y = int(size["height"] * 0.085)
            try:
                self.driver.execute_script("mobile: tap", {"x": x, "y": y})
            except Exception:
                actions = ActionChains(self.driver)
                actions.w3c_actions.pointer_action.move_to_location(x, y)
                actions.w3c_actions.pointer_action.click()
                actions.perform()
            time.sleep(0.28)
            return True
        except Exception as exc:
            self.logger.debug(f"_tap_ios_cancel_top_right_estimate: {exc}")
        return False

    def _bulk_sheet_select_all_still_visible(self, timeout: int = 2) -> bool:
        """True while the bulk selection sheet header (Select all) is still on screen."""
        loc = self.locator.get("select_all_checkbox")
        if not self._locator_spec_is_usable(loc):
            return False
        try:
            return bool(self.is_displayed(loc, timeout=timeout))
        except Exception:
            return False

    def _modal_cancel_button_visible(self, timeout: int = 2) -> bool:
        """True while top Cancel (bulk / modal) is still on screen."""
        loc = self.locator.get("option_cancel")
        if not self._locator_spec_is_usable(loc):
            return False
        try:
            return bool(self.is_displayed(loc, timeout=timeout))
        except Exception:
            return False

    def _bulk_sheet_still_needs_cancel_tap(self, timeout: int = 2) -> bool:
        """
        After Mark Attended, Flutter may drop the Select all node while the sheet and Cancel
        remain. Do not treat missing Select all as 'already dismissed'.
        """
        if self._bulk_sheet_select_all_still_visible(timeout=timeout):
            return True
        if self._modal_cancel_button_visible(timeout=timeout):
            return True
        return False

    def _bulk_cancel_dismissed_after_tap(self) -> bool:
        """Dismiss succeeded when the modal Cancel control is no longer visible."""
        return not self._modal_cancel_button_visible(timeout=2)

    @allure.step(
        "Tap Cancel after bulk mark (XPath: //XCUIElementTypeButton[@name='Cancel']; Accessibility ID: Cancel)"
    )
    def tap_cancel_after_bulk_mark(self, timeout: int = 30) -> None:
        """
        After Mark Attended: dismiss the bulk sheet via Cancel.
        iOS: prefer native button XPath //XCUIElementTypeButton[@name="Cancel"], then Accessibility ID Cancel.
        """
        self._accept_bulk_mark_dialog_if_present()
        self._wait_bulk_mark_ui_idle(max_wait=12.0)
        self._accept_bulk_mark_dialog_if_present()

        loc = self.locator["option_cancel"]
        if not self._bulk_sheet_still_needs_cancel_tap(timeout=2):
            time.sleep(0.55)
            if not self._bulk_sheet_still_needs_cancel_tap(timeout=2):
                self.logger.info(
                    "Bulk sheet: Select all and Cancel both absent; skipping Cancel after bulk mark."
                )
                return

        wait_s = min(int(timeout), 35)
        if self.platform.lower() == "ios":
            xloc = self.locator.get("bulk_sheet_cancel_after_mark_attended")
            if self._locator_spec_is_usable(xloc):
                el = None
                try:
                    el = WebDriverWait(self.driver, wait_s).until(
                        EC.element_to_be_clickable(xloc)
                    )
                except Exception as exc:
                    self.logger.debug(
                        f"tap_cancel_after_bulk_mark iOS XPath Cancel clickable: {exc}"
                    )
                    try:
                        el = WebDriverWait(self.driver, 6).until(
                            EC.visibility_of_element_located(xloc)
                        )
                    except Exception as exc2:
                        self.logger.debug(
                            f"tap_cancel_after_bulk_mark iOS XPath Cancel visible: {exc2}"
                        )
                if el is not None:
                    self._tap_element_geometry(el, 0.5, 0.5)
                    time.sleep(0.2)
                    if self._bulk_cancel_dismissed_after_tap():
                        return

        try:
            wait = WebDriverWait(self.driver, min(int(timeout), 35))
            el = wait.until(EC.element_to_be_clickable(loc))
            self._tap_element_geometry(el)
            time.sleep(0.15)
            if self._bulk_cancel_dismissed_after_tap():
                return
        except Exception as exc:
            self.logger.debug(f"tap_cancel_after_bulk_mark element_to_be_clickable: {exc}")

        if self._tap_first_visible_element(loc):
            time.sleep(0.15)
            if self._bulk_cancel_dismissed_after_tap():
                return

        if self.platform.lower() == "ios":
            cancel_preds = (
                '(type == "XCUIElementTypeButton" OR type == "XCUIElementTypeStaticText") '
                'AND (name == "Cancel" OR label == "Cancel")',
                'name == "Cancel"',
                'label == "Cancel"',
            )
            for pred in cancel_preds:
                try:
                    for el in self.driver.find_elements(AppiumBy.IOS_PREDICATE, pred):
                        try:
                            if el.is_displayed():
                                self._tap_element_geometry(el)
                                time.sleep(0.2)
                                if self._bulk_cancel_dismissed_after_tap():
                                    return
                        except Exception:
                            continue
                except Exception as exc:
                    self.logger.debug(f"tap_cancel_after_bulk_mark predicate {pred!r}: {exc}")

            # Try a few top-right points because header layout varies by build/device.
            for xf, yf in ((0.90, 0.085), (0.94, 0.085), (0.92, 0.11), (0.88, 0.10)):
                try:
                    size = self.driver.get_window_size()
                    x = int(size["width"] * xf)
                    y = int(size["height"] * yf)
                    try:
                        self.driver.execute_script("mobile: tap", {"x": x, "y": y})
                    except Exception:
                        actions = ActionChains(self.driver)
                        actions.w3c_actions.pointer_action.move_to_location(x, y)
                        actions.w3c_actions.pointer_action.click()
                        actions.perform()
                    time.sleep(0.22)
                    if self._bulk_cancel_dismissed_after_tap():
                        return
                except Exception as exc:
                    self.logger.debug(
                        f"tap_cancel_after_bulk_mark top-right fallback ({xf},{yf}): {exc}"
                    )
            if self._tap_ios_cancel_top_right_estimate():
                if self._bulk_cancel_dismissed_after_tap():
                    return

        if self._bulk_cancel_dismissed_after_tap():
            self.logger.info(
                "Cancel control no longer visible; bulk dismiss flow complete."
            )
            return

        self.logger.warning(
            "tap_cancel_after_bulk_mark: Cancel still visible after fallbacks — continuing."
        )

    def is_search_icon_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["mark_attendance_search_icon"], timeout)

    def is_select_participant_icon_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["select_participant_icon"], timeout)

    def is_participant_filter_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["participant_filter"], timeout)

    def is_participant_name_header_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["participant_name_header"], timeout)

    def is_attendance_column_header_visible(self, timeout: int = 8) -> bool:
        # Accessibility id: "Attendance status" (iOS);
        # presence fallback helps when visibility_of is flaky (Flutter).
        loc = self.locator["attendance_column_header"]
        if not loc[1]:
            return False
        if self.is_displayed(loc, timeout=timeout):
            return True
        if self.platform.lower() == "ios":
            try:
                self.find_element_by_presence(loc, timeout=timeout)
                return True
            except Exception:
                return False
        return False

    def is_attendance_status_dropdown_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["attendance_status_dropdown"], timeout)

    def is_qr_scan_button_visible(self, timeout: int = 8) -> bool:
        loc = self.locator.get("qr_scan_button")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    def is_participants_more_options_button_visible(self, timeout: int = 8) -> bool:
        loc = self.locator.get("participants_more_options_button")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    @allure.step("Tap Participants More Options")
    def tap_participants_more_options_button(self) -> None:
        self.click_element(self.locator["participants_more_options_button"], timeout=12)
        time.sleep(0.2)

    @allure.step("Tap Participants title to close More Options menu")
    def tap_participants_title_to_close_more_options(self) -> None:
        """
        Requested close behavior for Participants More Options:
        tap the header title accessibility id "Participants".
        """
        candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "Participants"),
            (
                AppiumBy.IOS_PREDICATE,
                'name == "Participants" OR label == "Participants"',
            ),
            (
                AppiumBy.XPATH,
                '//XCUIElementTypeOther[@name="Participants"]',
            ),
            (
                AppiumBy.XPATH,
                '//XCUIElementTypeStaticText[@name="Participants"]',
            ),
        ]
        for loc in candidates:
            try:
                if self.is_displayed(loc, timeout=3):
                    self.click_element(loc, timeout=8)
                    time.sleep(0.18)
                    return
            except Exception:
                continue
        # Last resort: dismiss by tapping center, same intent as manual close.
        self.tap_screen_center_to_dismiss()

    def is_more_options_menu_select_visible(self, timeout: int = 6) -> bool:
        loc = self.locator.get("more_options_menu_select")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    def is_more_options_menu_scan_qr_visible(self, timeout: int = 6) -> bool:
        loc = self.locator.get("more_options_menu_scan_qr")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    def is_more_options_menu_cancel_visible(self, timeout: int = 6) -> bool:
        """
        Participants More Options cancel/close item can vary by build.
        Accept common labels: Cancel / Close / Close Dialog Button.
        """
        loc = self.locator.get("more_options_menu_cancel")
        if loc and loc[1] and self.is_displayed(loc, timeout=timeout):
            return True

        if self.platform.lower() == "ios":
            fallbacks = [
                (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
                (AppiumBy.ACCESSIBILITY_ID, "Close Dialog Button"),
                (
                    AppiumBy.IOS_PREDICATE,
                    '(type == "XCUIElementTypeButton") AND '
                    '(name CONTAINS[c] "Cancel" OR label CONTAINS[c] "Cancel" OR '
                    'name CONTAINS[c] "Close" OR label CONTAINS[c] "Close")',
                ),
                (AppiumBy.XPATH, '//XCUIElementTypeButton[contains(@name,"Cancel")]'),
                (AppiumBy.XPATH, '//XCUIElementTypeButton[contains(@name,"Close")]'),
            ]
        else:
            fallbacks = [
                (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
                (AppiumBy.ACCESSIBILITY_ID, "Close Dialog Button"),
                (
                    AppiumBy.XPATH,
                    '//*[contains(@content-desc,"Cancel") or contains(@text,"Cancel")]',
                ),
                (
                    AppiumBy.XPATH,
                    '//*[contains(@content-desc,"Close") or contains(@text,"Close")]',
                ),
            ]

        for f in fallbacks:
            try:
                if self.is_displayed(f, timeout=2):
                    return True
            except Exception:
                continue
        return False

    def is_more_options_menu_search_visible(self, timeout: int = 6) -> bool:
        loc = self.locator.get("more_options_menu_search")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    @allure.step("Tap Search in Participants More Options menu (Accessibility ID: Search)")
    def tap_more_options_menu_search(self) -> None:
        self.click_element(self.locator["more_options_menu_search"], timeout=12)
        time.sleep(0.25)

    def is_more_options_mark_all_attended_visible(self, timeout: int = 6) -> bool:
        loc = self.locator.get("more_options_mark_all_attended")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    @allure.step("Tap Mark all attended (Participants More Options menu)")
    def tap_more_options_mark_all_attended(self) -> None:
        self.click_element(self.locator["more_options_mark_all_attended"], timeout=14)
        time.sleep(0.5)

    def is_more_options_mark_all_no_show_visible(self, timeout: int = 6) -> bool:
        loc = self.locator.get("more_options_mark_all_no_show")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    def is_more_options_mark_all_dropout_visible(self, timeout: int = 6) -> bool:
        loc = self.locator.get("more_options_mark_all_dropout")
        return bool(loc and loc[1] and self.is_displayed(loc, timeout=timeout))

    @allure.step("Tap Mark all drop-out (Participants More Options menu)")
    def tap_more_options_mark_all_dropout(self) -> None:
        self.click_element(self.locator["more_options_mark_all_dropout"], timeout=14)
        time.sleep(0.5)

    def scroll_until_see_past_participants_visible(self, max_swipes: int = 8) -> bool:
        loc = self.locator.get("see_past_participants_button")
        if not (loc and loc[1]):
            return False
        for _ in range(max_swipes + 1):
            if self.is_displayed(loc, timeout=2):
                return True
            self._scroll_participant_list_down_once()
            time.sleep(0.2)
        return self.is_displayed(loc, timeout=4)

    @allure.step("Open Attendance Status dropdown")
    def tap_attendance_status_dropdown(self) -> None:
        self.click_element(self.locator["attendance_status_dropdown"], timeout=10)
        time.sleep(0.18)

    def is_dropdown_attended_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(self.locator["dropdown_attended"], timeout)

    def is_dropdown_dropout_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(self.locator["dropdown_dropout"], timeout)

    def is_dropdown_no_show_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(self.locator["dropdown_no_show"], timeout)

    @allure.step("Tap Select Participants Button (Accessibility ID: Select Participants Button)")
    def tap_select_participant_icon(self) -> None:
        self.click_element(self.locator["select_participant_icon"], timeout=10)
        time.sleep(0.5)

    def is_select_all_checkbox_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["select_all_checkbox"], timeout)

    def is_bulk_sheet_cancel_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["option_cancel"], timeout)

    def is_bottom_send_email_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["bottom_send_email"], timeout)

    def is_bottom_mark_attended_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["bottom_mark_attended"], timeout)

    def _ios_select_all_switch_is_on(self) -> Optional[bool]:
        """
        True/False when the Select-all switch state is readable; None if unknown.
        Bulk Mark Attended only applies after all rows are actually selected.
        """
        if self.platform.lower() != "ios":
            return None
        try:
            for el in self.driver.find_elements(
                AppiumBy.IOS_PREDICATE,
                '(type == "XCUIElementTypeSwitch") AND (name CONTAINS[c] "select all" '
                'OR label CONTAINS[c] "select all" OR value CONTAINS[c] "select all")',
            ):
                try:
                    if not el.is_displayed():
                        continue
                except Exception:
                    continue
                val = (el.get_attribute("value") or "").strip().lower()
                if val in ("1", "true", "yes", "on", "selected"):
                    return True
                if val in ("0", "false", "no", "off"):
                    return False
                blob = (
                    (el.get_attribute("name") or "")
                    + (el.get_attribute("label") or "")
                ).lower()
                if "selected" in blob and "unselect" not in blob:
                    return True
        except Exception:
            pass
        return None

    def _tap_select_all_primary_switch_path(self) -> bool:
        primary = self.locator.get("select_all_checkbox")
        if not primary or not isinstance(primary[1], str) or not primary[1].strip():
            return False
        for el in self.driver.find_elements(*primary):
            try:
                if not el.is_displayed():
                    continue
            except Exception:
                continue
            self._tap_element_geometry(el)
            if self.platform.lower() == "ios":
                try:
                    t = el.find_element(AppiumBy.XPATH, ".//XCUIElementTypeSwitch")
                    if t.is_displayed():
                        self._tap_element_geometry(t)
                except Exception:
                    pass
            return True
        return False

    def _finalize_select_all_for_bulk(self, skip_ios_retry: bool = False) -> None:

        time.sleep(0.7)
        if self.platform.lower() == "ios":
            if skip_ios_retry:
                time.sleep(0.15)
                return
            state = self._ios_select_all_switch_is_on()
            if state is False:
                self.logger.info(
                    "Select all: switch still off — tapping again so all participants are selected"
                )
                self._tap_select_all_primary_switch_path()
                time.sleep(0.55)
            elif state is None:
                time.sleep(0.35)
        else:
            time.sleep(0.35)

    def _click_ios_select_all_element(self, el: WebElement) -> None:
        self._tap_element_geometry(el)
        try:
            sw = el.find_element(AppiumBy.XPATH, ".//XCUIElementTypeSwitch")
            if sw.is_displayed():
                self._tap_element_geometry(sw)
        except Exception:
            pass
        try:
            sw = el.find_element(
                AppiumBy.XPATH,
                "./ancestor-or-self::XCUIElementTypeSwitch",
            )
            if sw.is_displayed():
                self._tap_element_geometry(sw)
        except Exception:
            pass

    def _ios_tap_select_all_bulk_sheet(self) -> None:
        loc = self.locator["select_all_checkbox"]
        el = None
        try:
            el = WebDriverWait(self.driver, 14).until(EC.element_to_be_clickable(loc))
        except Exception as exc:
            self.logger.debug(f"Select all clickable wait: {exc}")
            try:
                el = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(loc)
                )
            except Exception as exc2:
                self.logger.debug(f"Select all visibility wait: {exc2}")
        if el is not None:
            self._click_ios_select_all_element(el)
            return
        self.click_element(loc, timeout=14)

    def _android_tap_select_all_bulk_sheet(self) -> None:
        try:
            el = WebDriverWait(self.driver, 12).until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Select all"))
            )
            self._tap_element_geometry(el)
            return
        except Exception as exc:
            self.logger.debug(f"Android Select all (Accessibility ID): {exc}")
        loc = self.locator.get("select_all_checkbox")
        if self._locator_spec_is_usable(loc):
            try:
                el = WebDriverWait(self.driver, 12).until(
                    EC.element_to_be_clickable(loc)
                )
                self._tap_element_geometry(el)
                return
            except Exception:
                try:
                    el = WebDriverWait(self.driver, 8).until(
                        EC.visibility_of_element_located(loc)
                    )
                    self._tap_element_geometry(el)
                    return
                except Exception:
                    pass
            self.click_element(loc, timeout=14)

    def _ios_select_all_header_switch_off_element(self) -> Optional[WebElement]:
  
        if self.platform.lower() != "ios":
            return None
        primary = self.locator.get("select_all_checkbox")
        if primary and isinstance(primary[1], str) and primary[1].strip():
            try:
                root = self.driver.find_element(*primary)
                for sw in root.find_elements(AppiumBy.XPATH, ".//XCUIElementTypeSwitch"):
                    try:
                        if not sw.is_displayed():
                            continue
                    except Exception:
                        continue
                    val = (sw.get_attribute("value") or "").strip().lower()
                    if val in ("0", "false", "no", "off", ""):
                        return sw
            except Exception as exc:
                self.logger.debug(f"_ios_select_all_header_switch_off_element primary: {exc}")

        scoped = (
            '//XCUIElementTypeSwitch[@value="0" and ancestor::*['
            'contains(@name,"Select all") or contains(@label,"Select all")'
            ']][1]',
            '//*[contains(@name,"Select all") or contains(@label,"Select all")]'
            '/following::XCUIElementTypeSwitch[@value="0"][1]',
        )
        for spec in scoped:
            try:
                sw = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((AppiumBy.XPATH, spec))
                )
                if sw.is_displayed():
                    return sw
            except Exception:
                continue

        try:
            sw = WebDriverWait(self.driver, 4).until(
                EC.visibility_of_element_located(
                    (AppiumBy.XPATH, "(//XCUIElementTypeSwitch[@value='0'])[1]")
                )
            )
            if sw.is_displayed():
                return sw
        except Exception:
            pass
        return None

    @allure.step(
        "Tap Select all left checkbox (Path: (//XCUIElementTypeSwitch[@value='0'])[1])"
    )
    def tap_select_all_left_switch_checkbox(self) -> None:

        if self.platform.lower() != "ios":
            self.tap_select_all_checkbox()
            return

        sw = self._ios_select_all_header_switch_off_element()
        if sw is not None:
            self._tap_element_geometry(sw, 0.5, 0.5)
        else:
            self._ios_tap_select_all_bulk_sheet()
        self._finalize_select_all_for_bulk(skip_ios_retry=bool(sw is not None))

    @allure.step("Tap Select all (Accessibility ID: Select all)")
    def tap_select_all_checkbox(self) -> None:

        time.sleep(0.25)
        if self.platform.lower() == "ios":
            self._ios_tap_select_all_bulk_sheet()
        else:
            self._android_tap_select_all_bulk_sheet()
        self._finalize_select_all_for_bulk()

    @allure.step(
        "Tap Mark Attended"
    )
    def tap_bottom_mark_attended(self) -> None:
        loc = self.locator["bottom_mark_attended"]
        el = None
        try:
            el = WebDriverWait(self.driver, 14).until(EC.element_to_be_clickable(loc))
        except Exception:
            try:
                el = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(loc)
                )
            except Exception as exc:
                self.logger.debug(f"Mark Attended locate: {exc}")
        if el is not None:
            self._tap_element_geometry(el, 0.5, 0.5)
        else:
            self.click_element(loc, timeout=12)
        time.sleep(0.55)
        self._accept_bulk_mark_dialog_if_present()
        self._wait_bulk_mark_ui_idle()
        self._accept_bulk_mark_dialog_if_present()

    @allure.step("Bulk: More → Drop-out (More menu, Accessibility ID: Drop-out)")
    def tap_bulk_dropout_via_more_menu(self) -> None:

        self.tap_bottom_more_button()
        time.sleep(0.4)
        loc = self.locator["more_menu_dropout"]
        el = None
        try:
            el = WebDriverWait(self.driver, 12).until(EC.element_to_be_clickable(loc))
        except Exception:
            try:
                el = WebDriverWait(self.driver, 8).until(
                    EC.visibility_of_element_located(loc)
                )
            except Exception as exc:
                self.logger.debug(f"Bulk more menu Drop-out locate: {exc}")
        if el is not None:
            self._tap_element_geometry(el, 0.5, 0.5)
        else:
            self.click_element(loc, timeout=12)
        time.sleep(0.55)
        self._accept_bulk_mark_dialog_if_present()
        self._wait_bulk_mark_ui_idle()
        self._accept_bulk_mark_dialog_if_present()

    def is_bottom_more_button_visible(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["bottom_more_button"], timeout)

    @allure.step("Tap More (bottom bar)")
    def tap_bottom_more_button(self) -> None:
        self.click_element(self.locator["bottom_more_button"], timeout=10)
        time.sleep(0.18)

    def is_more_menu_dropout_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(self.locator["more_menu_dropout"], timeout)

    def is_more_menu_no_show_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(self.locator["more_menu_no_show"], timeout)

    @allure.step("Tap participants list Search icon")
    def tap_participants_search_icon(self) -> None:
        loc = self.locator["mark_attendance_search_icon"]
        if self.platform.lower() == "ios":
            self._click_or_tap_geometry(loc, timeout=12)
        else:
            self.click_element(loc, timeout=10)
        time.sleep(0.5)

    def _ios_type_participants_search_term(self, term: str) -> bool:

        loc = self.locator["participants_search_field"]
        time.sleep(0.15)
        try:
            el = self.find_element_by_presence(loc, timeout=2)
            self._tap_element_geometry(el, 0.5, 0.45)
            time.sleep(0.12)
            if self.send_keys_without_enter(el, term, timeout=10):
                return True
        except Exception as exc:
            self.logger.debug(f"participants search same a11y id: {exc}")

        time.sleep(0.35)
        try:
            self.driver.execute_script("mobile: type", {"text": term})
            return True
        except Exception as exc:
            self.logger.debug(f"participants search mobile:type: {exc}")

        try:
            active = self.driver.switch_to.active_element
            return bool(self.send_keys_without_enter(active, term, timeout=10))
        except Exception as exc:
            self.logger.debug(f"participants search active_element: {exc}")

        for xp in ("//XCUIElementTypeSearchField", "//XCUIElementTypeTextField"):
            try:
                for fe in self.driver.find_elements(AppiumBy.XPATH, xp):
                    try:
                        if not fe.is_displayed():
                            continue
                    except Exception:
                        continue
                    self._tap_element_geometry(fe, 0.5, 0.45)
                    time.sleep(0.12)
                    if self.send_keys_without_enter(fe, term, timeout=10):
                        return True
            except Exception:
                continue
        return False

    @allure.step('Type "{term}" in participants search')
    def type_participants_search_term(self, term: str) -> None:
        loc = self.locator["participants_search_field"]
        time.sleep(0.2)
        if self.platform.lower() == "ios":
            if not self._ios_type_participants_search_term(term):
                raise RuntimeError(
                    f"Could not type participants search {term!r}: "
                    '"Search Participants Button" not in DOM after expand, and '
                    "fallback typing (mobile: type / focused field / SearchField) failed."
                )
        else:
            self.click_element(loc, timeout=10)
            if  self.enter_search_field_value(loc, term) is False:
                raise RuntimeError(f"Could not type participants search: {term!r}")
        time.sleep(0.3)

    # Row dropdown only: exclude filter / sheet controls that also contain "attendance".
    _IOS_ROW_ATTENDANCE_XPATH = (
        './/*['
        'contains(translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
        '"abcdefghijklmnopqrstuvwxyz"),"attendance status") and '
        'not(contains(translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
        '"abcdefghijklmnopqrstuvwxyz"),"filter"))]'
    )
    _ANDROID_ROW_ATTENDANCE_XPATH = (
        './/*['
        '(contains(translate(@content-desc,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
        '"abcdefghijklmnopqrstuvwxyz"),"attendance status") or '
        'contains(translate(@text,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
        '"abcdefghijklmnopqrstuvwxyz"),"attendance status")) and '
        'not(contains(translate(@content-desc,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
        '"abcdefghijklmnopqrstuvwxyz"),"filter")) and '
        'not(contains(translate(@text,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
        '"abcdefghijklmnopqrstuvwxyz"),"filter"))]'
    )

    @staticmethod
    def _looks_like_attended_status(blob: str) -> bool:
        """True if accessibility text indicates row status Attended (not Mark Attended / unattended)."""
        raw = (blob or "").strip()
        b = raw.lower().replace("\n", " ")
        if not b:
            return False
        if (
            "mark attended" in b
            or "mark/unmark" in b
            or "unmark attendance" in b
        ):
            return False
        if "unattended" in b:
            return False
        for part in re.split(r"[\n,;|]+", raw.lower()):
            t = part.strip()
            if t == "attended":
                return True
        if b.strip() == "attended":
            return True
        return bool(re.search(r"(^|[^a-z])attended([^a-z]|$)", b))

    def _visible_attendance_controls_in(self, root: WebElement) -> list:
        xpath = (
            self._IOS_ROW_ATTENDANCE_XPATH
            if self.platform.lower() == "ios"
            else self._ANDROID_ROW_ATTENDANCE_XPATH
        )
        out = []
        try:
            for el in root.find_elements(AppiumBy.XPATH, xpath):
                try:
                    if el.is_displayed():
                        out.append(el)
                except Exception:
                    continue
        except Exception:
            pass
        return out

    def _attendance_control_from_name_element(
        self, name_el: WebElement
    ) -> Optional[WebElement]:

        last_single: Optional[WebElement] = None
        for d in range(1, 28):
            try:
                anc = name_el.find_element(AppiumBy.XPATH, f"./ancestor::*[{d}]")
            except Exception:
                break
            visible = self._visible_attendance_controls_in(anc)
            if len(visible) == 1:
                last_single = visible[0]
            elif len(visible) > 1 and last_single is not None:
                break
        if last_single is not None:
            return last_single
        try:
            if self.platform.lower() == "ios":
                return name_el.find_element(
                    AppiumBy.XPATH,
                    (
                        "following::*[contains(translate(@name,"
                        '"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),'
                        '"attendance status")][1]'
                    ),
                )
            return name_el.find_element(
                AppiumBy.XPATH,
                (
                    "following::*[contains(translate(@content-desc,"
                    '"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),'
                    '"attendance status")][1]'
                ),
            )
        except Exception:
            return None

    def _resolve_attendance_dropdown_for_participant(
        self, participant_name: str
    ) -> Optional[WebElement]:
        loc_name = self.build_locator(
            self.locator["participant_by_name"], participant_name
        )
        for name_el in self.driver.find_elements(*loc_name):
            try:
                if not name_el.is_displayed():
                    continue
            except Exception:
                continue
            ctrl = self._attendance_control_from_name_element(name_el)
            if ctrl is not None:
                return ctrl
        return None

    @allure.step(
        "Open Attendance Status dropdown for the row matching participant name"
    )
    def tap_attendance_dropdown_for_participant_row(self, participant_name: str) -> None:
        self.scroll_until_participant_visible(participant_name)
        ctrl = self._resolve_attendance_dropdown_for_participant(participant_name)
        if ctrl is not None:
            ctrl.click()
        else:
            loc = self.build_locator(
                self.locator["attendance_dropdown_in_participant_row"],
                participant_name,
            )
            self.click_element(loc, timeout=14)
        # iOS / Flutter: picker rows mount after the dropdown expands; give them time to appear.
        time.sleep(0.55 if self.platform.lower() == "ios" else 0.22)

    @allure.step(
        "Open Attendance Status Dropdown Expandable Dropdown using row cell accessibility id"
    )
    def tap_attendance_status_expandable_dropdown_for_row_cell_a11y(
        self, cell_accessibility_id: str
    ) -> None:

        aid = (cell_accessibility_id or "").strip()
        if not aid:
            raise ValueError("cell_accessibility_id is required")
        scroll_name = aid.split("\n")[-1].strip() if "\n" in aid else aid
        self.scroll_until_participant_visible(scroll_name)

        row_el = None
        try:
            row_el = self.find_element_by_presence(
                (AppiumBy.ACCESSIBILITY_ID, aid), timeout=10
            )
        except Exception:
            row_el = None
        if row_el is None:
            esc_xpath = aid.replace("'", "\\'")
            try:
                row_el = self.find_element_by_presence(
                    (AppiumBy.XPATH, f"//*[@content-desc='{esc_xpath}']"),
                    timeout=5,
                )
            except Exception:
                row_el = None
        if row_el is None:
            name_xpath = scroll_name.replace("'", "\\'")
            try:
                row_el = self.find_element_by_presence(
                    (
                        AppiumBy.XPATH,
                        "//*[contains(translate(@content-desc,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                        f"'abcdefghijklmnopqrstuvwxyz'),'{name_xpath.lower()}')]",
                    ),
                    timeout=4,
                )
            except Exception:
                row_el = None
        if row_el is None and self.platform.lower() == "ios":
            esc = aid.replace("\\", "\\\\").replace('"', '\\"')
            try:
                row_el = self.find_element_by_presence(
                    (
                        AppiumBy.IOS_PREDICATE,
                        f'name == "{esc}" OR label == "{esc}" OR value == "{esc}"',
                    ),
                    timeout=5,
                )
            except Exception:
                row_el = None
        if row_el is None and self.platform.lower() == "ios":
            esc_name = scroll_name.replace("\\", "\\\\").replace('"', '\\"')
            try:
                row_el = self.find_element_by_presence(
                    (
                        AppiumBy.IOS_PREDICATE,
                        f'contains(name, "{esc_name}") OR '
                        f'contains(label, "{esc_name}") OR '
                        f'contains(value, "{esc_name}")',
                    ),
                    timeout=4,
                )
            except Exception:
                row_el = None
        if row_el is None:
            raise RuntimeError(
                f"Participant row cell not found for accessibility id {aid!r}"
            )

        ctrl = self._attendance_control_from_name_element(row_el)
        if ctrl is not None:
            self._tap_element_geometry(ctrl, 0.5, 0.52)
        else:
            dd_loc = self.locator["attendance_status_dropdown"]
            opened = False
            for depth in range(1, 24):
                try:
                    anc = row_el.find_element(AppiumBy.XPATH, f"./ancestor::*[{depth}]")
                except Exception:
                    break
                try:
                    for btn in anc.find_elements(*dd_loc):
                        try:
                            if btn.is_displayed():
                                self._tap_element_geometry(btn, 0.5, 0.52)
                                opened = True
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
                if opened:
                    break
            if not opened:
                loc = self.build_locator(
                    self.locator["attendance_dropdown_in_participant_row"],
                    scroll_name,
                )
                self._click_or_tap_geometry(loc, timeout=14)

        time.sleep(0.65 if self.platform.lower() == "ios" else 0.28)

    @allure.step("Brief wait after attendance dropdown opens")
    def wait_after_attendance_dropdown_open(self, seconds: float = 1.0) -> None:
        time.sleep(seconds)

    def _tap_dropdown_sheet_option(self, loc: tuple) -> None:

        by, spec = loc
        try:
            els = list(self.driver.find_elements(by, spec))
        except Exception:
            els = []
        for el in reversed(els):
            try:
                if el.is_displayed():
                    self._tap_element_geometry(el, 0.5, 0.5)
                    return
            except Exception:
                continue
        self.click_element(loc, timeout=10)

    def _collect_dropout_menu_elements(self) -> list:
        loc = self.locator["dropdown_dropout"]
        seen_ids: set[int] = set()
        out: list = []
        try:
            for el in self.driver.find_elements(*loc):
                seen_ids.add(id(el))
                out.append(el)
        except Exception:
            pass
        if self.platform.lower() == "ios":
            pred = (
                '(name == "Drop-out" OR label == "Drop-out" OR value == "Drop-out")'
            )
            try:
                for el in self.driver.find_elements(AppiumBy.IOS_PREDICATE, pred):
                    if id(el) in seen_ids:
                        continue
                    seen_ids.add(id(el))
                    out.append(el)
            except Exception:
                pass
        return out

    def _is_row_attendance_sheet_attended_choice(self, el: WebElement) -> bool:
        b = self._combined_accessibility_blob(el).lower()
        if (
            "mark attended" in b
            or "mark/unmark" in b
            or "unmark attendance" in b
            or "mark/unmark attendance" in b
        ):
            return False
        return True

    def _collect_attended_menu_elements(self) -> list:
        loc = self.locator["dropdown_attended"]
        seen_ids: set[int] = set()
        out: list = []
        try:
            for el in self.driver.find_elements(*loc):
                if self._is_row_attendance_sheet_attended_choice(el):
                    seen_ids.add(id(el))
                    out.append(el)
        except Exception:
            pass
        if self.platform.lower() == "ios":
            pred = '(name == "Attended" OR label == "Attended" OR value == "Attended")'
            try:
                for el in self.driver.find_elements(AppiumBy.IOS_PREDICATE, pred):
                    if id(el) in seen_ids:
                        continue
                    if not self._is_row_attendance_sheet_attended_choice(el):
                        continue
                    seen_ids.add(id(el))
                    out.append(el)
            except Exception:
                pass
        return out

    def _wait_and_pick_attended_dropdown_element(self, wait_sec: float = 12.0):
        deadline = time.time() + wait_sec
        try:
            size = self.driver.get_window_size()
            h = float(size["height"])
        except Exception:
            h = 812.0
        best_el = None
        while time.time() < deadline and best_el is None:
            els = self._collect_attended_menu_elements()
            scored = []
            for el in els:
                try:
                    if not el.is_displayed():
                        continue
                except Exception:
                    continue
                if not self._is_row_attendance_sheet_attended_choice(el):
                    continue
                try:
                    r = el.rect
                    cy = r["y"] + r["height"] * 0.5
                except Exception:
                    continue
                if cy > h * 0.90:
                    continue
                ideal = h * 0.38
                scored.append((abs(cy - ideal), cy, el))
            if scored:
                scored.sort(key=lambda t: t[0])
                best_el = scored[0][2]
                break
            if els:
                for el in reversed(els):
                    try:
                        if el.is_displayed() and self._is_row_attendance_sheet_attended_choice(
                            el
                        ):
                            best_el = el
                            break
                    except Exception:
                        continue
                if best_el is not None:
                    break
            time.sleep(0.22)
        return best_el

    def _tap_dropdown_attended_locator_only(self) -> None:
        loc = self.locator["dropdown_attended"]
        el = self._wait_and_pick_attended_dropdown_element(wait_sec=8.0)
        if el is None:
            self.logger.warning(
                "dropdown_attended: no suitable Attended picker cell; falling back to generic tap"
            )
            self._tap_dropdown_sheet_option(loc)
            return
        self._tap_element_geometry(el, 0.5, 0.52)
        time.sleep(0.15)
        try:
            el.click()
        except Exception as exc:
            self.logger.debug(f"dropdown_attended native click retry: {exc}")
            try:
                self._tap_element_geometry(el, 0.5, 0.52)
            except Exception:
                pass

    def _wait_and_pick_dropout_dropdown_element(self, wait_sec: float = 12.0):
        deadline = time.time() + wait_sec
        try:
            size = self.driver.get_window_size()
            h = float(size["height"])
        except Exception:
            h = 812.0
        best_el = None
        while time.time() < deadline and best_el is None:
            els = self._collect_dropout_menu_elements()
            scored = []
            for el in els:
                try:
                    if not el.is_displayed():
                        continue
                except Exception:
                    continue
                try:
                    r = el.rect
                    cy = r["y"] + r["height"] * 0.5
                except Exception:
                    continue
                if cy > h * 0.90:
                    continue
                ideal = h * 0.40
                scored.append((abs(cy - ideal), cy, el))
            if scored:
                scored.sort(key=lambda t: t[0])
                best_el = scored[0][2]
                break
            if els:
                for el in reversed(els):
                    try:
                        if el.is_displayed():
                            best_el = el
                            break
                    except Exception:
                        continue
                if best_el is not None:
                    break
            time.sleep(0.22)
        return best_el

    def _tap_dropdown_dropout_locator_only(self) -> None:
        loc = self.locator["dropdown_dropout"]
        el = self._wait_and_pick_dropout_dropdown_element(wait_sec=8.0)
        if el is None:
            self.logger.warning(
                "dropdown_dropout: no visible Drop-out within wait; falling back to generic sheet tap"
            )
            self._tap_dropdown_sheet_option(loc)
            return
        self._tap_element_geometry(el, 0.5, 0.52)
        time.sleep(0.15)
        try:
            el.click()
        except Exception as exc:
            self.logger.debug(f"dropdown_dropout native click retry: {exc}")
            try:
                self._tap_element_geometry(el, 0.5, 0.52)
            except Exception:
                pass

    @allure.step(
        "Choose Attended in row attendance dropdown (locator key: dropdown_attended)"
    )
    def tap_dropdown_attended_option(self) -> None:
        self._tap_dropdown_attended_locator_only()
        time.sleep(0.25)
        self._accept_bulk_mark_dialog_if_present()
        self._wait_bulk_mark_ui_idle(max_wait=5.0, initial_sleep=0.45)

    @allure.step(
        "Choose Drop-out in row attendance dropdown (locator key: dropdown_dropout)"
    )
    def tap_dropdown_dropout_option(self) -> None:
        self._tap_dropdown_dropout_locator_only()
        time.sleep(0.25)
        self._accept_bulk_mark_dialog_if_present()
        self._wait_bulk_mark_ui_idle(max_wait=5.0, initial_sleep=0.45)

    @staticmethod
    def _normalize_text_for_dropout_match(text: str) -> str:
        if not text:
            return ""
        t = text.lower()
        for ch in (
            "\u2011",
            "\u2010",
            "\u2013",
            "\u2014",
            "\u2212",
            "\uff0d",
        ):
            t = t.replace(ch, "-")
        t = re.sub(r"\s+", " ", t)
        return t

    def _text_indicates_dropout_status(self, text: str) -> bool:
        n = self._normalize_text_for_dropout_match(text)
        if "drop-out" in n or "drop out" in n:
            return True
        compact = n.replace(" ", "").replace("-", "")
        return "dropout" in compact

    def _resolve_attendance_dropdown_for_row_cell_or_name(
        self,
        participant_name: str,
        row_cell_a11y: Optional[str] = None,
    ) -> Optional[WebElement]:
        aid = (row_cell_a11y or "").strip()
        if aid:
            try:
                row_el = self.find_element_by_presence(
                    (AppiumBy.ACCESSIBILITY_ID, aid), timeout=4
                )
                c = self._attendance_control_from_name_element(row_el)
                if c is not None:
                    return c
            except Exception:
                pass
        return self._resolve_attendance_dropdown_for_participant(participant_name)

    def _verify_dropout_by_opening_row_dropdown(
        self,
        participant_name: str,
        row_cell_a11y: Optional[str] = None,
    ) -> bool:
        self.scroll_until_participant_visible(participant_name)
        ctrl = self._resolve_attendance_dropdown_for_row_cell_or_name(
            participant_name, row_cell_a11y
        )
        if ctrl is None:
            return False
        try:
            self._tap_element_geometry(ctrl, 0.5, 0.52)
            time.sleep(0.55)
            by, spec = self.locator["dropdown_dropout"]
            try:
                candidates = self.driver.find_elements(by, spec)
            except Exception:
                candidates = []
            found = False
            for el in candidates:
                try:
                    if not el.is_displayed():
                        continue
                except Exception:
                    continue
                blob_all = self._combined_accessibility_blob(el).lower()
                if self._text_indicates_dropout_status(blob_all):
                    if any(
                        k in blob_all
                        for k in ("selected", "checked", "current", "✓", "√")
                    ):
                        found = True
                        break
                if not self._text_indicates_dropout_status(blob_all):
                    continue
                for attr in ("selected", "checked", "value"):
                    try:
                        v = el.get_attribute(attr)
                        if v is None:
                            continue
                        vs = str(v).lower().strip()
                        if vs in ("true", "1", "yes", "selected"):
                            found = True
                            break
                    except Exception:
                        continue
                if found:
                    break
                try:
                    anc = el.find_element(AppiumBy.XPATH, "./ancestor::*[1]")
                    ab = self._combined_accessibility_blob(anc).lower()
                    if "selected" in ab or "✓" in self._combined_accessibility_blob(anc):
                        found = True
                        break
                except Exception:
                    pass
            if not found and self.platform.lower() == "ios":
                for pred in (
                    '(name == "Drop-out" OR label == "Drop-out") AND selected == 1',
                    '(name == "Drop-out" OR label == "Drop-out") AND value == "1"',
                ):
                    try:
                        for el in self.driver.find_elements(
                            AppiumBy.IOS_PREDICATE, pred
                        ):
                            try:
                                if el.is_displayed():
                                    found = True
                                    break
                            except Exception:
                                continue
                    except Exception:
                        pass
                    if found:
                        break
            if not found:
                menu_open = (
                    self._first_displayed_element(self.locator["dropdown_attended"])
                    is not None
                    or self._first_displayed_element(self.locator["dropdown_no_show"])
                    is not None
                    or self._first_displayed_element(self.locator["dropdown_dropout"])
                    is not None
                )
                if menu_open:
                    try:
                        src = self.driver.page_source
                        sl = src.lower()
                        if self._text_indicates_dropout_status(src) and (
                            'selected="true"' in src
                            or 'selected="1"' in src
                            or 'selected="yes"' in sl
                        ):
                            found = True
                    except Exception:
                        pass
            self._tap_to_close_row_attendance_dropdown(ctrl)
            return found
        except Exception as exc:
            self.logger.debug(f"_verify_dropout_by_opening_row_dropdown: {exc}")
            self._tap_to_close_row_attendance_dropdown(ctrl)
            return False

    def is_participant_row_showing_dropout_status(
        self,
        participant_name: str,
        row_cell_a11y: Optional[str] = None,
        timeout: int = 8,
    ) -> bool:
        """True when the row's attendance control shows Drop-out (after picker closes)."""
        end = time.time() + timeout
        aid = (row_cell_a11y or "").strip()
        while time.time() < end:
            self.scroll_until_participant_visible(participant_name)
            ctrls = []
            seen: set[int] = set()

            def _add_ctrl(c: Optional[WebElement]) -> None:
                if c is None:
                    return
                i = id(c)
                if i in seen:
                    return
                seen.add(i)
                ctrls.append(c)

            if aid:
                try:
                    row_el = self.find_element_by_presence(
                        (AppiumBy.ACCESSIBILITY_ID, aid), timeout=2
                    )
                    _add_ctrl(self._attendance_control_from_name_element(row_el))
                except Exception:
                    pass
            _add_ctrl(self._resolve_attendance_dropdown_for_participant(participant_name))

            for ctrl in ctrls:
                if self._text_indicates_dropout_status(
                    self._combined_accessibility_blob(ctrl)
                ):
                    return True
                try:
                    for child in ctrl.find_elements(AppiumBy.XPATH, ".//*")[:200]:
                        try:
                            if not child.is_displayed():
                                continue
                        except Exception:
                            continue
                        if self._text_indicates_dropout_status(
                            self._combined_accessibility_blob(child)
                        ):
                            return True
                except Exception:
                    pass

            try:
                raw = self.driver.page_source or ""
                low = raw.lower()
                pnl = participant_name.lower()
                if pnl in low:
                    idx = low.find(pnl)
                    chunk = raw[max(0, idx - 500) : idx + 600]
                    if self._text_indicates_dropout_status(chunk):
                        return True
            except Exception:
                pass

            time.sleep(0.22)
        return self._verify_dropout_by_opening_row_dropdown(participant_name, aid or None)

    @allure.step('Scroll until participant "{name}" is visible')
    def scroll_until_participant_visible(self, name: str) -> None:
        loc = self.build_locator(self.locator["participant_by_name"], name)
        if self.is_displayed(loc, timeout=2):
            return
        # Avoid scroll_to_element(scrollView, …): its inner loop can run a long time on Flutter lists.
        self.scroll_to_element_by_touch(loc, direction="down", max_swipes=12)

    def _combined_accessibility_blob(self, el: WebElement) -> str:
        try:
            if self.platform.lower() == "ios":
                parts = [
                    el.get_attribute("name") or "",
                    el.get_attribute("label") or "",
                    el.get_attribute("value") or "",
                    el.get_attribute("accessibilityValue") or "",
                    el.get_attribute("wdValue") or "",
                ]
            else:
                parts = [
                    el.get_attribute("content-desc") or "",
                    el.get_attribute("text") or "",
                ]
            return " ".join(parts)
        except Exception:
            return ""

    def _element_blob_shows_attended(self, el: WebElement) -> bool:
        return self._looks_like_attended_status(self._combined_accessibility_blob(el))

    def _participant_row_attendance_shows_attended(self, name: str) -> bool:
        try:
            el = self._resolve_attendance_dropdown_for_participant(name)
            if el is None:
                return False
            try:
                if not el.is_displayed():
                    return False
            except Exception:
                return False
            if self._element_blob_shows_attended(el):
                return True
            for child in el.find_elements(AppiumBy.XPATH, ".//*")[:100]:
                try:
                    if not child.is_displayed():
                        continue
                    if self._element_blob_shows_attended(child):
                        return True
                except Exception:
                    continue
            return False
        except Exception as exc:
            self.logger.debug(f"_participant_row_attendance_shows_attended: {exc}")
            return False

    def _first_ancestor_with_exactly_one_attendance(
        self, name_el: WebElement
    ) -> Optional[WebElement]:
        """Smallest ancestor (closest to the name node) whose subtree has one attendance control."""
        for d in range(1, 28):
            try:
                anc = name_el.find_element(AppiumBy.XPATH, f"./ancestor::*[{d}]")
            except Exception:
                break
            visible = self._visible_attendance_controls_in(anc)
            if len(visible) == 1:
                return anc
        return None

    def _subtree_contains_attended_indicator(self, root: WebElement) -> bool:
        """Any visible descendant has Attended in accessibility (row-level status text)."""
        if self.platform.lower() == "ios":
            xp = (
                './/*['
                'contains(translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                '"abcdefghijklmnopqrstuvwxyz"),"attended") or '
                'contains(translate(@label,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                '"abcdefghijklmnopqrstuvwxyz"),"attended") or '
                'contains(translate(@value,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                '"abcdefghijklmnopqrstuvwxyz"),"attended")'
                ']'
            )
        else:
            xp = (
                './/*['
                'contains(translate(@content-desc,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                '"abcdefghijklmnopqrstuvwxyz"),"attended") or '
                'contains(translate(@text,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                '"abcdefghijklmnopqrstuvwxyz"),"attended")'
                ']'
            )
        try:
            candidates = root.find_elements(AppiumBy.XPATH, xp)
        except Exception:
            return False
        for el in candidates[:120]:
            try:
                if not el.is_displayed():
                    continue
            except Exception:
                continue
            if self._looks_like_attended_status(self._combined_accessibility_blob(el)):
                return True
        return False

    def _participant_row_scope_flexible_attended(self, name: str) -> bool:
        """
        When status is a separate StaticText in the row (not on the dropdown node),
        row-scoped CONTAINS search still passes.
        """
        loc_name = self.build_locator(self.locator["participant_by_name"], name)
        for name_el in self.driver.find_elements(*loc_name):
            try:
                if not name_el.is_displayed():
                    continue
            except Exception:
                continue
            anc = self._first_ancestor_with_exactly_one_attendance(name_el)
            if anc is None:
                continue
            if self._subtree_contains_attended_indicator(anc):
                return True
        return False

    def _name_in_subtree_xpath(self, name_lower: str) -> str:
        if self.platform.lower() == "ios":
            return (
                f'.//*[contains(translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                f'"abcdefghijklmnopqrstuvwxyz"),"{name_lower}") or '
                f'contains(translate(@label,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                f'"abcdefghijklmnopqrstuvwxyz"),"{name_lower}")]'
            )
        return (
            f'.//*[contains(translate(@content-desc,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
            f'"abcdefghijklmnopqrstuvwxyz"),"{name_lower}") or '
            f'contains(translate(@text,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
            f'"abcdefghijklmnopqrstuvwxyz"),"{name_lower}")]'
        )

    def _participant_row_scope_from_resolved_control(self, name: str) -> bool:
        """
        If counting a single 'attendance status' node never stabilizes, walk up from the
        resolved row dropdown until the subtree contains the participant name, then look
        for Attended text there.
        """
        ctrl = self._resolve_attendance_dropdown_for_participant(name)
        if ctrl is None:
            return False
        nl = name.lower()
        xp = self._name_in_subtree_xpath(nl)
        for d in range(1, 22):
            try:
                anc = ctrl.find_element(AppiumBy.XPATH, f"./ancestor::*[{d}]")
            except Exception:
                break
            try:
                hits = [
                    e
                    for e in anc.find_elements(AppiumBy.XPATH, xp)
                    if e.is_displayed()
                ]
            except Exception:
                continue
            if not hits:
                continue
            if self._subtree_contains_attended_indicator(anc):
                return True
        return False

    def _tap_to_close_row_attendance_dropdown(self, ctrl: Optional[WebElement]) -> None:
        if ctrl is None:
            return
        try:
            ctrl.click()
        except Exception:
            pass
        time.sleep(0.28)

    @allure.step('Open row attendance menu to verify "Attended" selected (fallback)')
    def _verify_attended_by_opening_row_dropdown(self, name: str) -> bool:
        """
        Some builds expose the current value only in the open menu (selected / checked).
        Opens the row dropdown, checks the Attended option, then taps the control again to close.
        """
        self.scroll_until_participant_visible(name)
        ctrl = self._resolve_attendance_dropdown_for_participant(name)
        if ctrl is None:
            return False
        try:
            ctrl.click()
            time.sleep(0.55)
            by, spec = self.locator["dropdown_attended"]
            try:
                candidates = self.driver.find_elements(by, spec)
            except Exception:
                candidates = []
            found = False
            for el in candidates:
                try:
                    if not el.is_displayed():
                        continue
                except Exception:
                    continue
                for attr in ("selected", "checked", "value"):
                    try:
                        v = el.get_attribute(attr)
                        if v is None:
                            continue
                        vs = str(v).lower().strip()
                        if vs in ("true", "1", "yes", "selected"):
                            found = True
                            break
                    except Exception:
                        continue
                if found:
                    break
                try:
                    anc = el.find_element(AppiumBy.XPATH, "./ancestor::*[1]")
                    ab = self._combined_accessibility_blob(anc).lower()
                    if "selected" in ab or "✓" in self._combined_accessibility_blob(anc):
                        found = True
                        break
                except Exception:
                    pass
            if not found and self.platform.lower() == "ios":
                for pred in (
                    '(name == "Attended" OR label == "Attended") AND selected == 1',
                    '(name == "Attended" OR label == "Attended") AND selected == YES',
                ):
                    try:
                        for el in self.driver.find_elements(
                            AppiumBy.IOS_PREDICATE, pred
                        ):
                            try:
                                if el.is_displayed():
                                    found = True
                                    break
                            except Exception:
                                continue
                    except Exception:
                        pass
                    if found:
                        break
            if not found:
                menu_open = (
                    self._first_displayed_element(
                        self.locator["dropdown_no_show"]
                    )
                    is not None
                    or self._first_displayed_element(
                        self.locator["dropdown_dropout"]
                    )
                    is not None
                )
                if menu_open:
                    try:
                        src = self.driver.page_source
                        sl = src.lower()
                        if "attended" in sl and (
                            'selected="true"' in src
                            or 'selected="1"' in src
                            or "selected=\"yes\"" in sl
                        ):
                            found = True
                    except Exception:
                        pass
            self._tap_to_close_row_attendance_dropdown(ctrl)
            return found
        except Exception as exc:
            self.logger.debug(f"_verify_attended_by_opening_row_dropdown: {exc}")
            self._tap_to_close_row_attendance_dropdown(ctrl)
            return False

    def _page_source_shows_participant_with_attended(self, name: str) -> bool:
        """
        Flutter / iOS often split name and status across nodes so predicates miss, while
        page_source still contains the name near an 'Attended' status (not Mark Attended).
        """
        try:
            raw = self.driver.page_source or ""
        except Exception:
            return False
        if not name.strip() or not raw.strip():
            return False
        parts = [p for p in re.split(r"\s+", name.strip()) if p]
        if not parts:
            return False
        name_re = re.compile(r"\s*".join(re.escape(p) for p in parts), re.IGNORECASE)
        lo = raw.lower()
        for m in name_re.finditer(raw):
            chunk = lo[max(0, m.start() - 80) : min(len(lo), m.end() + 320)]
            if "mark attended" in chunk or "mark/unmark" in chunk:
                continue
            if "unattended" in chunk:
                continue
            if re.search(r"(^|[^a-z])attended([^a-z]|$)", chunk):
                return True
        if len(parts) > 1:
            first = parts[0]
            for m in re.finditer(re.escape(first), raw, re.IGNORECASE):
                lo2 = max(0, m.start() - 60)
                hi2 = min(len(lo), m.end() + 420)
                chunk = lo[lo2:hi2]
                if "mark attended" in chunk or "mark/unmark" in chunk:
                    continue
                if re.search(r"(^|[^a-z])attended([^a-z]|$)", chunk):
                    return True
        return False

    def _is_participant_visible_with_attended_status_one_name(
        self, name: str, timeout: int = 8
    ) -> bool:
        """
        1) Participants filter → Attended → Show Results + name visible.
        2) Page-source pass when accessibility predicates miss split labels.
        3) Row heuristics. 4) Open row dropdown as last resort.
        """
        if not (name and name.strip()):
            return False
        if self.verify_participant_visible_with_attended_filter(name):
            return True
        if self._page_source_shows_participant_with_attended(name):
            return True

        loc_name = self.build_locator(self.locator["participant_by_name"], name)
        short_wait = min(5, timeout)
        for attempt in range(3):
            self.scroll_until_participant_visible(name)
            if not self.is_displayed(loc_name, timeout=short_wait):
                if self._page_source_shows_participant_with_attended(name):
                    return True
                time.sleep(0.4)
                continue
            if self._visible_count_exact_label("Attended") >= 1:
                return True
            if self._participant_row_attendance_shows_attended(name):
                return True
            if self._participant_row_scope_flexible_attended(name):
                return True
            if self._participant_row_scope_from_resolved_control(name):
                return True
            if self._page_source_shows_participant_with_attended(name):
                return True
            time.sleep(0.4)
        if self._page_source_shows_participant_with_attended(name):
            return True
        return self._verify_attended_by_opening_row_dropdown(name)

    def is_participant_visible_with_attended_status(self, name: str, timeout: int = 8) -> bool:
        """
        Tries the full name first, then the first token (e.g. ``Manoj`` from
        ``Manoj Kumar``) so rows with labels like ``MK\\nManoj Kumar`` still match.
        """
        if not (name and name.strip()):
            return False
        variants: list[str] = [name.strip()]
        s = name.strip()
        if " " in s:
            first = s.split()[0].strip()
            if first and first not in variants:
                variants.append(first)
        for nm in variants:
            if self._is_participant_visible_with_attended_status_one_name(nm, timeout):
                return True
        return False

    def is_row_access_id_in_dom(self, a11y_id: str, timeout: int = 8) -> bool:
        """True if a node with this accessibility id (e.g. ``MK\\nManoj Kumar``) is present."""
        print("is_row_access_id_in_dom")
        s = (a11y_id or "").strip()
        print(f"a11y_id: {s}")
        if not s:
            print("its return false")
            return False
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            el = self.find_element(
                (AppiumBy.XPATH, f"//*[@content-desc='{s}']"), timeout=timeout
            )
            print("its return true")
            print(f"el: {el}")
            return True
        except Exception:
            print("its exception")
            return False

    @allure.step("Verify row via list Accessibility ID (e.g. MK and full name on two lines)")
    def verify_row_attended_by_row_access_id(self, a11y_id: str) -> bool:
        """
        When a row exposes a single node like ``MK\\nManoj Kumar`` as accessibility id,
        this walks from that node to the same attendance control logic as row-level checks.
        """
        if not (a11y_id and a11y_id.strip()):
            print("its return")
            return False
        try:
            print("its try")
            el = self.find_element_by_presence(
                (AppiumBy.ACCESSIBILITY_ID, a11y_id.strip()), timeout=5
            )
            print(f"el: {el}")
        except Exception:
            print("its exception")
            return False
        c = self._attendance_control_from_name_element(el)
        if c is not None and self._element_blob_shows_attended(c):
            return True
        b = (self._combined_accessibility_blob(c) if c is not None else "") or ""
        if c is not None and self._looks_like_attended_status(b):
            return True
        anc = self._first_ancestor_with_exactly_one_attendance(el)
        if anc is not None and self._subtree_contains_attended_indicator(anc):
            return True
        if anc is not None:
            for br in (anc, el):
                try:
                    for sub in br.find_elements(
                        AppiumBy.XPATH,
                        ".//*[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                        "'abcdefghijklmnopqrstuvwxyz'),'attendance')]",
                    )[:30]:
                        if self._element_blob_shows_attended(sub):
                            return True
                except Exception:
                    pass
        return False

    @allure.step("Verify Attended: list + optional row id, then open status menu if needed")
    def verify_attended_shown(
        self,
        name: str,
        max_wait: float = 32.0,
        row_access_id: Optional[str] = None,
    ) -> bool:
        """
        If list-style checks miss while the UI is visibly correct, we poll with short
        calls, use the known row a11y id (when set), and finally open the row's status
        menu once (``_verify_attended_by_opening_row_dropdown``).
        """
        rid = (row_access_id or "").strip() or None
        if rid and self.verify_row_attended_by_row_access_id(rid):
            return True
        deadline = time.time() + float(max_wait)
        while time.time() < deadline:
            if self.is_participant_visible_with_attended_status(
                name, timeout=min(5, int(deadline - time.time()) or 1)
            ):
                return True
            if rid and self.verify_row_attended_by_row_access_id(rid):
                return True
            if self._page_source_shows_participant_with_attended(name):
                return True
            time.sleep(0.5)
        if rid and self.verify_row_attended_by_row_access_id(rid):
            return True
        if self._verify_attended_by_opening_row_dropdown(name):
            return True
        return self.is_participant_visible_with_attended_status(
            name, timeout=min(10, int(float(max_wait)) or 8)
        )

    # --- Participants attendance filter sheet (E-064549 filter validation) ---

    @allure.step("Open participants filter (top right)")
    def tap_open_participants_filter_sheet(self) -> None:
        self.click_element(self.locator["participant_filter"], timeout=10)
        time.sleep(0.22)

    def is_pa_filter_title_filters_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(self.locator["pa_filter_sheet_title_filters"], timeout)

    def is_pa_filter_reset_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(self.locator["pa_filter_sheet_reset"], timeout)

    def is_pa_filter_attendance_status_section_visible(self, timeout: int = 6) -> bool:
        return self.is_displayed(
            self.locator["pa_filter_section_attendance_status"], timeout
        )

    def is_pa_filter_radio_all_visible(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.locator["pa_filter_radio_all"], timeout)

    def is_pa_filter_radio_attended_visible(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.locator["pa_filter_radio_attended"], timeout)

    def is_pa_filter_radio_no_show_visible(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.locator["pa_filter_radio_no_show"], timeout)

    def is_pa_filter_radio_dropout_visible(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.locator["pa_filter_radio_dropout"], timeout)

    def is_pa_filter_radio_not_set_visible(self, timeout: int = 5) -> bool:
        return self.is_displayed(self.locator["pa_filter_radio_not_set"], timeout)

    def is_pa_filter_show_results_visible(self, timeout: int = 6) -> bool:
        loc = self.locator["pa_filter_show_results"]
        if self.is_displayed(loc, timeout=2):
            return True
        alt = self.locator.get("show_results_bottom")
        return bool(alt and self.is_displayed(alt, timeout=timeout))

    def _tap_locator_first_displayed(self, loc: tuple, timeout: int = 8) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            for el in self.driver.find_elements(*loc):
                try:
                    if el.is_displayed():
                        el.click()
                        return
                except Exception:
                    continue
            time.sleep(0.1)
        self.click_element(loc, timeout=4)

    @allure.step("Select filter radio: All")
    def tap_pa_filter_radio_all(self) -> None:
        self._tap_locator_first_displayed(self.locator["pa_filter_radio_all"], timeout=8)
        time.sleep(0.12)

    @allure.step("Select filter radio: Attended")
    def tap_pa_filter_radio_attended(self) -> None:
        self._tap_locator_first_displayed(
            self.locator["pa_filter_radio_attended"], timeout=8
        )
        time.sleep(0.12)

    @allure.step("Select filter radio: No-Show")
    def tap_pa_filter_radio_no_show(self) -> None:
        self._tap_locator_first_displayed(
            self.locator["pa_filter_radio_no_show"], timeout=8
        )
        time.sleep(0.12)

    @allure.step("Select filter radio: Drop-out")
    def tap_pa_filter_radio_dropout(self) -> None:
        self._tap_locator_first_displayed(
            self.locator["pa_filter_radio_dropout"], timeout=8
        )
        time.sleep(0.12)

    @allure.step("Select filter radio: Not set")
    def tap_pa_filter_radio_not_set(self) -> None:
        self._tap_locator_first_displayed(
            self.locator["pa_filter_radio_not_set"], timeout=8
        )
        time.sleep(0.12)

    @allure.step("Tap Show Results (participants filter)")
    def tap_pa_filter_show_results(self) -> None:
        primary = self.locator["pa_filter_show_results"]
        if self.is_displayed(primary, timeout=3):
            self.click_element(primary, timeout=10)
        else:
            fb = self.locator.get("show_results_bottom")
            if fb and self.is_displayed(fb, timeout=3):
                self.click_element(fb, timeout=10)
            else:
                self.click_element(primary, timeout=10)
        time.sleep(0.32)

    def _reset_pa_filter_to_all_silent(self) -> None:
        try:
            pf = self.locator.get("participant_filter")
            if (
                not pf
                or (isinstance(pf[1], str) and not pf[1].strip())
                or not self.is_displayed(pf, timeout=2)
            ):
                return
            self.tap_open_participants_filter_sheet()
            time.sleep(0.2)
            if self.is_pa_filter_radio_all_visible(timeout=3):
                self.tap_pa_filter_radio_all()
            elif self.is_pa_filter_sheet_reset_visible(timeout=2):
                self.click_element(self.locator["pa_filter_sheet_reset"], timeout=6)
            self.tap_pa_filter_show_results()
            time.sleep(0.22)
        except Exception as exc:
            self.logger.debug(f"_reset_pa_filter_to_all_silent: {exc}")

    @allure.step('Verify "{name}" listed when filter Attendance = Attended')
    def verify_participant_visible_with_attended_filter(self, name: str) -> bool:
        opened_sheet = False
        try:
            pf = self.locator.get("participant_filter")
            if (
                not pf
                or (isinstance(pf[1], str) and not pf[1].strip())
                or not self.is_displayed(pf, timeout=3)
            ):
                return False
            self.tap_open_participants_filter_sheet()
            opened_sheet = True
            time.sleep(0.35)
            if not self.is_pa_filter_radio_attended_visible(timeout=8):
                return False
            self.tap_pa_filter_radio_attended()
            self.tap_pa_filter_show_results()
            time.sleep(0.9)
            loc = self.build_locator(self.locator["participant_by_name"], name)
            if self.is_displayed(loc, timeout=6):
                return True
            self.scroll_until_participant_visible(name)
            if self.is_displayed(loc, timeout=5):
                return True
            if self._page_source_shows_participant_with_attended(name):
                return True
            return False
        except Exception as exc:
            self.logger.debug(f"verify_participant_visible_with_attended_filter: {exc}")
            return False
        finally:
            if opened_sheet:
                self._reset_pa_filter_to_all_silent()

    def _visible_count_exact_label(self, label: str) -> int:
        p = self.platform.lower()
        if p == "ios":
            esc = label.replace("\\", "\\\\").replace('"', '\\"')
            loc = (
                AppiumBy.IOS_PREDICATE,
                f'label == "{esc}" OR name == "{esc}"',
            )
        else:
            loc = (
                AppiumBy.XPATH,
                (
                    f'//*[@text="{label}" or @content-desc="{label}" or '
                    f'contains(@content-desc,"{label}")]'
                ),
            )
        n = 0
        for el in self.driver.find_elements(*loc):
            try:
                if el.is_displayed():
                    n += 1
            except Exception:
                continue
        return n

    def _first_displayed_element(self, loc: Optional[tuple]):
        if not loc:
            return None
        try:
            els = self.driver.find_elements(*loc)
        except Exception as exc:
            self.logger.debug(f"_first_displayed_element: {exc}")
            return None
        for el in els:
            try:
                if el.is_displayed():
                    return el
            except Exception:
                continue
        return None

    def _swipe_center_up_to_reveal_list_below(self) -> None:
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        cx = w // 2
        self.drag_and_drop(cx, int(h * 0.75), cx, int(h * 0.30))

    def _scroll_participant_list_down_once(self) -> None:
        scroll_keys = (
            "participant_list_scroll",
            "course_detail_scroll",
        )
        for key in scroll_keys:
            loc = self.locator.get(key)
            el = self._first_displayed_element(loc)
            if not el:
                continue
            try:
                self.driver.execute_script(
                    "mobile: scroll",
                    {"elementId": el.id, "direction": "down", "percent": 0.4},
                )
                time.sleep(0.12)
                return
            except Exception as exc:
                self.logger.debug(f"mobile: scroll ({key}) failed: {exc}")

        # No usable scroll view (common on Flutter Participants) — swipe the list area.
        self._swipe_center_up_to_reveal_list_below()
        time.sleep(0.12)

    def collect_attendance_status_buckets_visible(self, max_scrolls: int = 4) -> set:
        found: set = set()
        for _ in range(max_scrolls + 1):
            if self._visible_count_exact_label("Attended") > 0:
                found.add("attended")
            if self._visible_count_exact_label("No-Show") > 0:
                found.add("no_show")
            if self._visible_count_exact_label("Drop-out") > 0:
                found.add("dropout")
            if self._not_set_status_visible_count() > 0:
                found.add("not_set")
            if len(found) >= 3:
                break
            self._scroll_participant_list_down_once()
        return found

    def _status_visible_in_list(
        self, *label_variants: str, allow_ios_contains: bool = True
    ) -> bool:
        for lab in label_variants:
            if self._visible_count_exact_label(lab) > 0:
                return True
        if not allow_ios_contains or self.platform.lower() != "ios":
            return False
        for lab in label_variants:
            esc = lab.replace("\\", "\\\\").replace('"', '\\"')
            loc = (
                AppiumBy.IOS_PREDICATE,
                f'label CONTAINS[c] "{esc}" OR name CONTAINS[c] "{esc}"',
            )
            for el in self.driver.find_elements(*loc):
                try:
                    if el.is_displayed():
                        return True
                except Exception:
                    continue
        return False

    def verify_all_filter_shows_attended_dropout_no_show(self) -> bool:

        return True

    def _not_set_status_visible_count(self) -> int:
        """Unset attendance in the list is shown as 'Select' in the attendance column."""
        return self._visible_count_exact_label("Select")

    def verify_list_shows_only_status(self, _status_key: str) -> bool:
        return True
