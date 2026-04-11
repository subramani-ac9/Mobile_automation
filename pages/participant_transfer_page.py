import logging
import time

import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage
from constants.locator.myevent_locator import MyEventLocator
from constants.locator.participant_transfer_locator import ParticipantTransferLocator


class ParticipantTransferPage(BasePage):
    """UI flow for participant transfer (Events search → Participants → eligible programs)."""

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = {
            **MyEventLocator.get_locators(platform),
            **ParticipantTransferLocator.get_locators(platform),
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    def _events_search_button(self):
        return self.locator.get("search_button") or self.locator.get("events_search_button")

    @allure.step("Tap Events search icon (top right)")
    def tap_events_search_icon(self) -> None:
        btn = self._events_search_button()
        if not btn:
            raise RuntimeError("No Events search button locator for this platform")
        self.click_element(btn, timeout=14)
        time.sleep(0.28)

    @allure.step('Type "{term}" in Events search field')
    def type_events_search_term(self, term: str) -> None:
        field = self.locator["events_search_field"]
        self.click_element(field, timeout=12)
        if self.send_keys_without_enter(field, term, timeout=12) is False:
            raise RuntimeError(f"Could not type Events search term: {term}")
        time.sleep(0.5)

    @allure.step('Open Events search and type "{term}"')
    def open_events_search_and_type(self, term: str) -> None:
        self.tap_events_search_icon()
        self.type_events_search_term(term)

    @allure.step('Open first event row matching "{code}"')
    def click_event_row_containing(self, code: str) -> None:
        loc = self.build_locator(self.locator["event_row_contains"], code)
        self.scroll_to_element_by_touch(loc, max_swipes=20)
        self.click_element(loc, timeout=14)

    def _participants_section_locator_keys(self):
        keys = ["participants_section"]
        for k in (
            "participants_section_alt_1",
            "participants_section_alt_2",
            "participants_section_alt_3",
        ):
            if k in self.locator:
                keys.append(k)
        return keys

    @allure.step("Scroll to Participants and open")
    def open_participants_section(self) -> None:
        scroll = self.locator["course_detail_scroll"]
        last_err = None
        for key in self._participants_section_locator_keys():
            target = self.locator[key]
            try:
                self.scroll_to_element(scroll, target, direction="down")
                if self.is_displayed(target, timeout=10):
                    self.click_element(target, timeout=15)
                    self.logger.info(f"Opened Participants using locator key: {key}")
                    return
            except Exception as e:
                last_err = e
                self.logger.debug(f"Participants try {key} (scroll): {e}")
        for key in self._participants_section_locator_keys():
            target = self.locator[key]
            try:
                self.scroll_to_element_by_touch(target, direction="down", max_swipes=20)
                if self.is_displayed(target, timeout=8):
                    self.click_element(target, timeout=15)
                    self.logger.info(
                        f"Opened Participants using locator key: {key} (touch scroll)"
                    )
                    return
            except Exception as e:
                last_err = e
                self.logger.debug(f"Participants try {key} (touch): {e}")
        raise RuntimeError(
            "Could not open Participants. Set the correct locator in "
            "`constants/locator/participant_transfer_locator.py` under `ios` "
            f"(keys: {self._participants_section_locator_keys()}). Last error: {last_err}"
        )

    @allure.step('Open participant "{name}"')
    def open_participant_by_name(self, name: str) -> None:
        loc = self.build_locator(self.locator["participant_by_name"], name)
        # scroll = self.locator["course_detail_scroll"]
        self.scroll_to_element_by_touch(loc, direction="down", max_swipes=20)
        self.click_element(loc, timeout=15)

    @allure.step("Verify Transfer and Notes are visible")
    def transfer_and_notes_visible(self, timeout: int = 12) -> bool:
        t_ok = self.is_displayed(self.locator["transfer_button"], timeout)
        n_ok = self.is_displayed(self.locator["notes_button"], timeout)
        return t_ok and n_ok

    @allure.step("Tap Transfer (participant detail)")
    def tap_transfer_on_participant_detail(self) -> None:
        self.click_element(self.locator["transfer_button"], timeout=15)

    @allure.step("Tap Confirm")
    def tap_confirm(self) -> None:
        self.click_element(self.locator["confirm_button"], timeout=15)

    @allure.step('Enter transfer reason: "{message}"')
    def enter_transfer_reason(self, message: str) -> None:
        field = self.locator["transfer_reason_field"]
        self.click_element(field, timeout=10)
        if self.send_keys_without_enter(field, message, timeout=15) is False:
            raise RuntimeError("Could not type transfer reason")

    @allure.step("Tap Transfer (top-right) — first: eligible-program picker (id: Transfer)")
    def tap_transfer_top_right(self) -> None:
        self.click_element(self.locator["transfer_top_right"], timeout=15)

    @allure.step(
        "Tap Transfer (top-right) — second: target program screen (id: Transfer Button)"
    )
    def tap_transfer_top_right_after_eligible_selection(self) -> None:
        loc = self.locator.get("transfer_top_right_2")
        if not loc:
            self.click_element(self.locator["transfer_top_right"], timeout=15)
            return
        if self.is_displayed(loc, timeout=4):
            self.click_element(loc, timeout=15)
            return
        self.logger.debug("transfer_top_right_2 not visible; trying transfer_top_right")
        self.click_element(self.locator["transfer_top_right"], timeout=15)

    def _click_first_matching_text(self, labels: list[str], step_name: str) -> None:
        """Tap first visible control matching any of the given accessibility / label strings."""
        for text in labels:
            if not text:
                continue
            esc = text.replace("\\", "\\\\").replace('"', '\\"')
            if self.platform.lower() == "ios":
                candidates = [
                    (AppiumBy.ACCESSIBILITY_ID, text),
                    (
                        AppiumBy.IOS_PREDICATE,
                        f'label == "{esc}" OR name == "{esc}" OR value == "{esc}"',
                    ),
                    (
                        AppiumBy.IOS_PREDICATE,
                        f'label CONTAINS[c] "{esc}" OR name CONTAINS[c] "{esc}"',
                    ),
                ]
                for loc in candidates:
                    try:
                        if self.is_displayed(loc, timeout=1):
                            self.click_element(loc, timeout=12)
                            self.logger.info(f"{step_name}: tapped {text!r}")
                            return
                    except Exception as e:
                        self.logger.debug(f"{step_name} try {loc!r}: {e}")
            else:
                xp = (
                    AppiumBy.XPATH,
                    f'//*[@content-desc="{text}" or @text="{text}"]',
                )
                xp2 = (
                    AppiumBy.XPATH,
                    f'//*[contains(@content-desc,"{text}") or contains(@text,"{text}")]',
                )
                for loc in (xp, xp2):
                    try:
                        if self.is_displayed(loc, timeout=1):
                            self.click_element(loc, timeout=12)
                            self.logger.info(f"{step_name}: tapped {text!r}")
                            return
                    except Exception as e:
                        self.logger.debug(f"{step_name} try {loc!r}: {e}")
        raise RuntimeError(
            f"{step_name}: no matching control for labels {labels!r}. "
            "Update participant_transfer_locator.py or label list."
        )

    @allure.step(
        "Eligible programs: filter → Teachers → Any One Event Teacher → Show Results"
    )
    def apply_eligible_programs_teacher_filter(self) -> None:
        self.click_element(self.locator["eligible_programs_filter"], timeout=15)
        time.sleep(0.22)
        if "filter_teachers_option" in self.locator:
            loc = self.locator["filter_teachers_option"]
            if self.is_displayed(loc, timeout=3):
                self.click_element(loc, timeout=12)
            else:
                self._click_first_matching_text(
                    ParticipantTransferLocator.teacher_filter_row_labels(self.platform),
                    "Teachers filter row",
                )
        else:
            self._click_first_matching_text(
                ParticipantTransferLocator.teacher_filter_row_labels(self.platform),
                "Teachers filter row",
            )
        time.sleep(0.22)
        if "teacher_filter_any_one_event" in self.locator:
            self.click_element(self.locator["teacher_filter_any_one_event"], timeout=12)
        else:
            self._click_first_matching_text(
                [
                    "Any One Event Teacher",
                    "Any one event teacher",
                    "Any One event Teacher",
                ],
                "Teacher option",
            )
        time.sleep(0.22)
        self.tap_show_results()

    def tap_show_results(self) -> None:
        key = "show_results_bottom"
        if key in self.locator and self.is_displayed(self.locator[key], timeout=8):
            self.click_element(self.locator[key])
            return
        if "show_result" in self.locator:
            self.click_element(self.locator["show_result"])
            return
        raise RuntimeError("No Show Results control found")

    @allure.step(
        "Long-press visible eligible rows until target {target_code} is found, then open it"
    )
    def long_press_until_target_program(self, target_code: str, max_passes: int = 25) -> None:
        target = self.build_locator(self.locator["event_row_contains"], target_code)
        scroll = self.locator.get("scroll") or self.locator["course_detail_scroll"]
        for _ in range(max_passes):
            if self.is_displayed(target, timeout=2):
                self.click_element(target)
                return
            rows = self.find_elements(self.locator["eligible_event_row"], timeout=3)
            for row in rows[:5]:
                try:
                    self.long_click_element(row)
                    time.sleep(0.26)
                except Exception as e:
                    self.logger.debug(f"Long-press row skipped: {e}")
            if self.is_displayed(target, timeout=2):
                self.click_element(target)
                return
            try:
                self.scroll_on_the_element(scroll, direction="down", percent=0.45)
            except Exception:
                self.scroll_to_element_by_touch(target, max_swipes=2)
            time.sleep(0.2)
        raise RuntimeError(f"Target program row not found: {target_code}")

    def _find_click_first_silent(self, locators: list) -> bool:
        """Click first matching element without find_element() (avoids ERROR log noise)."""
        for loc in locators:
            if not loc:
                continue
            try:
                els = self.driver.find_elements(*loc)
                if els:
                    els[0].click()
                    return True
            except Exception as e:
                self.logger.debug(f"Silent tap skip {loc!r}: {e}")
        return False

    def _ios_nav_back_step1_locators(self) -> list:
        """First toolbar back (QA app chevron chain / xpath)."""
        return [
            self.locator.get("nav_back_first_click"),
            self.locator.get("nav_back_first_click_xpath"),
        ]

    def _ios_nav_back_step2_locators(self) -> list:
        """Second back (Back Button)."""
        return [
            self.locator.get("nav_back"),
            self.locator.get("nav_back_second_click_xpath"),
        ]

    def _ios_nav_back_locators(self) -> list:
        """General recovery: prefer Back Button, then first-click chain, then generic."""
        return [
            self.locator.get("nav_back"),
            self.locator.get("nav_back_second_click_xpath"),
            self.locator.get("nav_back_first_click"),
            self.locator.get("nav_back_first_click_xpath"),
            (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Back"]'),
            (AppiumBy.XPATH, '//XCUIElementTypeNavigationBar//XCUIElementTypeButton[1]'),
            (
                AppiumBy.IOS_PREDICATE,
                '(type == "XCUIElementTypeButton" OR type == "XCUIElementTypeImage") '
                'AND (label == "Back" OR name == "Back" OR label == "Back Button" '
                'OR name == "Back Button")',
            ),
        ]

    def _android_nav_back_locators(self) -> list:
        return [
            self.locator.get("nav_back"),
            (
                AppiumBy.XPATH,
                '//android.widget.ImageButton[@content-desc="Back"]',
            ),
        ]

    def _try_nav_back_once(self) -> bool:
        """Tap hardware-style back if found; always try driver.back() as well on iOS stack."""
        if self.platform.lower() == "ios":
            if self._find_click_first_silent(self._ios_nav_back_locators()):
                return True
        else:
            if self._find_click_first_silent(self._android_nav_back_locators()):
                return True
        try:
            self.driver.back()
            return True
        except Exception as e:
            self.logger.debug(f"driver.back failed: {e}")
            return False

    @allure.step("Navigate back repeatedly (iOS/Android toolbar + system fallbacks)")
    def tap_back_with_platform_fallbacks(self, count: int = 2) -> None:
        """
        Prefer silent multi-locator back (chevron, Back, Back Button, etc.) and
        ``driver.back()`` when no toolbar control matches. Use after share sheet or
        any screen where a single accessibility id like ``Back Button`` is absent.
        """
        for _ in range(max(1, count)):
            self._try_nav_back_once()
            time.sleep(0.35)

    def _events_main_visible(self) -> bool:
        for key in ("event_template", "search_button", "advance_filter"):
            loc = self.locator.get(key)
            if loc and self.is_displayed(loc, timeout=1.5):
                return True
        return False

    def _ios_search_close_locators(self) -> list:
        return [
            self.locator.get("events_search_close_button"),
            (
                AppiumBy.IOS_PREDICATE,
                'label == "Events Search Close Button" OR name == "Events Search Close Button"',
            ),
            (
                AppiumBy.IOS_PREDICATE,
                'label CONTAINS "Search Close" OR name CONTAINS "Search Close"',
            ),
            (
                AppiumBy.IOS_PREDICATE,
                '(label CONTAINS[c] "Close" OR name CONTAINS[c] "Close") AND '
                '(label CONTAINS[c] "Search" OR name CONTAINS[c] "Search" OR '
                'label CONTAINS[c] "Event" OR name CONTAINS[c] "Event")',
            ),
            (AppiumBy.XPATH, '//XCUIElementTypeButton[contains(@name,"Close")]'),
            (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
        ]

    def _android_search_close_locators(self) -> list:
        return [
            self.locator.get("events_search_close_button"),
            (
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Close") and contains(@content-desc,"Search")]',
            ),
            (AppiumBy.XPATH, '//*[contains(@content-desc,"Events Search") and contains(@content-desc,"Close")]'),
        ]

    def _try_tap_events_search_close(self) -> bool:
        locs = (
            self._ios_search_close_locators()
            if self.platform.lower() == "ios"
            else self._android_search_close_locators()
        )
        return self._find_click_first_silent(locs)

    def _my_events_tab_locators(self) -> list:
        return [
            self.locator.get("my_events_icon"),
            (AppiumBy.ACCESSIBILITY_ID, "bottom_nav_My Events\nMy Events"),
            (
                AppiumBy.IOS_PREDICATE,
                '(label CONTAINS[c] "My Events" OR name CONTAINS[c] "My Events") '
                'AND (type == "XCUIElementTypeButton" OR type == "XCUIElementTypeImage")',
            ),
        ]

    def _try_my_events_tab(self) -> bool:
        if self.platform.lower() == "ios":
            return self._find_click_first_silent(self._my_events_tab_locators())
        return self._find_click_first_silent(
            [
                self.locator.get("my_events_icon"),
                (
                    AppiumBy.XPATH,
                    '//android.widget.ImageView[@content-desc="My Events Button"]',
                ),
                (
                    AppiumBy.XPATH,
                    '//android.widget.ImageView[@content-desc="My Events"]',
                ),
            ]
        )

    @allure.step("Assert Transfer Initiated and dismiss")
    def assert_transfer_initiated_and_ok(self) -> None:
        msg = self.locator["transfer_initiated_message"]
        assert self.is_displayed(msg, timeout=25), "Transfer Initiated message not shown"
        print("\n========== OUTPUT: Transfer Initiated ==========\n")
        self.logger.info("OUTPUT: Transfer Initiated")
        self.click_element(self.locator["dialog_ok_button"], timeout=10)

    @allure.step("Back (top-left) until Events screen (repeat until Events template or cap)")
    def navigate_back_to_events(self, steps: int = 5) -> None:
        """Prefer visible back control; fall back to driver.back()."""
        for i in range(steps):
            self._try_nav_back_once()
            time.sleep(0.32)
            if self._events_main_visible():
                self.logger.info("Events main screen reached")
                return
        self.navigate_to_events_tab()

    @allure.step(
        "Back twice, close Events search if shown, until Events main is visible"
    )
    def back_twice_then_close_events_search(self) -> None:
        """Two toolbar backs (iOS: first chevron chain, then Back Button), then search close / recovery."""
        self.logger.info("Backing twice and closing events search")
        for i in range(2):
            if self.platform.lower() == "ios":
                locs = (
                    self._ios_nav_back_step1_locators()
                    if i == 0
                    else self._ios_nav_back_step2_locators()
                )
                ok = self._find_click_first_silent([x for x in locs if x])
            else:
                ok = self._find_click_first_silent(self._android_nav_back_locators())
            if not ok:
                try:
                    self.driver.back()
                    self.logger.info("Used system back after toolbar back was not found")
                except Exception as e:
                    self.logger.debug(f"System back: {e}")
            else:
                self.logger.info("Toolbar back tapped")
            time.sleep(0.35)

        if self._try_tap_events_search_close():
            self.logger.info("Tapped Events search close (or equivalent)")
            time.sleep(0.22)
        else:
            self.logger.debug("No Events search close control matched; continuing")

        if self._events_main_visible():
            self.logger.info("Events main visible")
            return

        for j in range(5):
            self._try_nav_back_once()
            time.sleep(0.28)
            if self._events_main_visible():
                self.logger.info("Events main visible after extra navigation")
                return

        if self._try_my_events_tab():
            time.sleep(0.38)
            if self.is_displayed(self.locator["event_template"], timeout=5):
                self.click_element(self.locator["event_template"])
            time.sleep(0.32)

        if not self._events_main_visible():
            raise RuntimeError(
                "Events main not visible after back twice and search close. "
                "Confirm back chevron and close control labels in Appium Inspector."
            )

    @allure.step(
        "Close Events search if shown and recover to Events main (backs already done)"
    )
    def finish_return_to_events_main_after_backs(self) -> None:
        """Use after poster flow (or any flow) that already tapped back twice explicitly."""
        if self._try_tap_events_search_close():
            self.logger.info("Tapped Events search close (or equivalent)")
            time.sleep(0.22)
        else:
            self.logger.debug("No Events search close control matched; continuing")

        if self._events_main_visible():
            self.logger.info("Events main visible")
            return

        for j in range(5):
            self._try_nav_back_once()
            time.sleep(0.28)
            if self._events_main_visible():
                self.logger.info("Events main visible after extra navigation")
                return

        if self._try_my_events_tab():
            time.sleep(0.38)
            if self.is_displayed(self.locator["event_template"], timeout=5):
                self.click_element(self.locator["event_template"])
            time.sleep(0.32)

        if not self._events_main_visible():
            self.logger.info(
                "Events main still not visible; trying navigate_to_events_tab()"
            )
            try:
                self.navigate_to_events_tab()
                time.sleep(0.5)
            except Exception as e:
                self.logger.warning("navigate_to_events_tab recovery failed: %s", e)

        if self._events_main_visible():
            self.logger.info("Events main visible after bottom-nav / tab recovery")
            return

        if not self._events_main_visible():
            raise RuntimeError(
                "Events main not visible after search close / recovery. "
                "Confirm Events search close and My Events tab in Appium Inspector."
            )

    @allure.step("Ensure Events tab from bottom navigation")
    def navigate_to_events_tab(self) -> None:
        if not self._try_my_events_tab():
            self.logger.warning("Could not tap My Events tab; trying plain driver.back()")
            try:
                self.driver.back()
            except Exception:
                pass
        time.sleep(0.32)
        if self.is_displayed(self.locator["event_template"], timeout=6):
            self.click_element(self.locator["event_template"])
        time.sleep(0.55)

    @allure.step('Verify participant "{name}" visible on Participants')
    def is_participant_visible(self, name: str) -> bool:
        loc = self.build_locator(self.locator["participant_by_name"], name)
        scroll = self.locator["course_detail_scroll"]
        try:
            self.scroll_to_element_by_touch(loc, direction="down", max_swipes=20)
        except Exception:
            self.scroll_to_element_by_touch(loc, max_swipes=12)
        return self.is_displayed(loc, timeout=10)
