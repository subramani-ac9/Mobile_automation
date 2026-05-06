import time
import allure
from selenium.webdriver import ActionChains

from pages.base_page import BasePage
from constants.locator.quotes_locator import QuotesLocator
from constants.locator.myevent_locator import MyEventLocator


class QuotesPage(BasePage):
    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = QuotesLocator.get_locators(platform)
        self._nav = MyEventLocator.get_locators(platform)

    @allure.step("Navigate to Home tab")
    def navigate_to_home(self) -> None:
        self.click_element(self._nav["home_icon"])
        self.wait_for_page_load()

    def _quote_elements_visible(self) -> bool:
        return self.is_displayed(self.locator["jai_gurudev_title"], 2) and self.is_displayed(
            self.locator["quote_more_options"], 2
        )

    def is_quote_section_ready_within(self, max_seconds: float = 8.0) -> bool:
        deadline = time.perf_counter() + max_seconds
        while time.perf_counter() < deadline:
            if self._quote_elements_visible():
                return True
            time.sleep(0.25)
        return False

    def is_preparing_quote_message_displayed(self, timeout: int = 2) -> bool:
        return self.is_displayed(self.locator["preparing_quote_share"], timeout)

    @allure.step(
        "Verify quote section appears quickly after Home (title + more options)"
    )
    def assert_quote_loads_without_delay(self, max_seconds: float = 8.0) -> None:
        deadline = time.perf_counter() + max_seconds
        while time.perf_counter() < deadline:
            if self._quote_elements_visible():
                return
            time.sleep(0.25)
        raise AssertionError(
            f"Quote section (title + Quote More Options) not ready within {max_seconds}s"
        )

    @allure.step('Verify "Jai Gurudev!" title is displayed')
    def is_jai_gurudev_title_displayed(self, timeout: int = 10) -> bool:
        return self.is_displayed(self.locator["jai_gurudev_title"], timeout)

    @allure.step("Verify Quote More Options Button is displayed")
    def is_quote_more_options_displayed(self, timeout: int = 10) -> bool:
        return self.is_displayed(self.locator["quote_more_options"], timeout)

    @allure.step("Tap Quote More Options")
    def click_quote_more_options(self) -> None:
        self.click_element(self.locator["quote_more_options"])

    @allure.step("Verify Edit / Share / Download quote menu items are visible")
    def are_quote_menu_actions_displayed(self) -> dict[str, bool]:
        timeout = 8
        return {
            "edit": self.is_displayed(self.locator["edit_quote_menu"], timeout),
            "share": self.is_displayed(self.locator["share_quote_menu"], timeout),
            "download": self.is_displayed(self.locator["download_quote_menu"], timeout),
        }

    # @allure.step("Dismiss quote menu by tapping away from the sheet")
    # def dismiss_quote_menu_by_tapping_outside(self) -> None:
    #     size = self.driver.get_window_size()
    #     x = int(size["width"] * 0.5)
    #     y = int(size["height"] * 0.12)
    #     try:
    #         self.driver.execute_script("mobile: tap", {"x": x, "y": y})
    #     except Exception as e:
    #         self.logger.warning("mobile: tap failed, falling back to title tap: %s", e)
    #         if self.is_jai_gurudev_title_displayed(timeout=3):
    #             self.click_element(self.locator["jai_gurudev_title"])
    #     time.sleep(0.4)

    @allure.step("Dismiss quote menu by tapping away from the sheet")
    def dismiss_quote_menu_by_tapping_outside(self) -> None:
        size = self.driver.get_window_size()
        x = int(size["width"] * 0.5)
        y = int(size["height"] * 0.12)
        try:
            platform = self.driver.capabilities.get("platformName", "").lower()
            print(f"Platform: {platform}")
            if platform == "ios":
                self.driver.execute_script("mobile: tap", {"x": x, "y": y})
            else:
                self.driver.tap([(x, y)])
        except Exception as e:
            self.logger.warning(
                "Tap failed, falling back to title tap: %s", e
            )
            if self.is_jai_gurudev_title_displayed(timeout=3):
                self.click_element(self.locator["jai_gurudev_title"])
        time.sleep(0.4)

    @allure.step("Tap Share in quote overflow menu")
    def click_share_quote_menu_item(self) -> None:
        self.click_element(self.locator["share_quote_menu"])

    @allure.step("Tap Download in quote overflow menu")
    def click_download_quote_menu_item(self) -> None:
        self.click_element(self.locator["download_quote_menu"])

    def _page_source_has_downloading_quote(self) -> bool:
        return "downloading quote" in (self.driver.page_source or "").lower()

    @allure.step(
        'Wait for optional "Downloading quote..."'
    )
    def wait_for_downloading_quote_message_optional(self, timeout: float = 8.0) -> bool:
        loc = self.locator.get("downloading_quote")
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            if loc and loc[1] and self.is_displayed(loc, 1):
                return True
            if self._page_source_has_downloading_quote():
                return True
            time.sleep(0.1)
        self.logger.info(
            "Downloading-quote UI not detected within %.1fs — continuing", timeout
        )
        return False

    def _page_source_has_quote_saved_gallery(self) -> bool:
        s = (self.driver.page_source or "").lower()
        if "quote saved" not in s:
            return False
        return "gallery" in s or "tap to open" in s

    @allure.step(
        'Wait for "Quote saved to your phone. Tap to open gallery."'
    )
    def wait_for_quote_saved_to_gallery_message(self, timeout: float = 28.0) -> None:
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            if self._page_source_has_quote_saved_gallery():
                return
            time.sleep(0.15)
        raise AssertionError(
            'Expected quote saved + gallery / "tap to open" hint within timeout'
        )

    @allure.step("Fixed delay (seconds)")
    def wait_seconds(self, seconds: float) -> None:
        time.sleep(float(seconds))

    @allure.step(
        'Wait for "Preparing quote for sharing..." to appear'
    )
    def wait_for_preparing_quote_message(self, timeout: float = 12.0) -> None:
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            if self.is_displayed(self.locator["preparing_quote_share"], 1):
                return
            time.sleep(0.12)
        raise AssertionError(
            f'"Preparing quote for sharing..." not shown within {timeout}s'
        )

    @allure.step(
        'Wait briefly for optional "Preparing quote for sharing..." '
        "(may not show on repeat share / cached asset)"
    )
    def wait_for_preparing_quote_message_optional(self, timeout: float = 8.0) -> bool:
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            if self.is_displayed(self.locator["preparing_quote_share"], 1):
                return True
            time.sleep(0.12)
        self.logger.info(
            "Preparing-quote toast not shown within %.1fs — continuing (repeat share / fast path)",
            timeout,
        )
        return False

    @allure.step("Wait for preparing message to clear (share sheet opening)")
    def wait_for_preparing_quote_message_gone(self, timeout: float = 20.0) -> None:
        deadline = time.perf_counter() + timeout
        while time.perf_counter() < deadline:
            if not self.is_displayed(self.locator["preparing_quote_share"], 1):
                return
            time.sleep(0.15)
        raise AssertionError(
            "Preparing-quote message did not disappear — share flow may be stuck"
        )

    @allure.step("Brief pause for OS share UI to finish presenting")
    def wait_for_share_sheet_animation(self, seconds: float = 0.6) -> None:
        time.sleep(seconds)

    def _tap_coordinate(self, x: int, y: int) -> None:
        x, y = int(x), int(y)
        try:
            chains = ActionChains(self.driver)
            chains.w3c_actions.pointer_action.move_to_location(x, y)
            chains.w3c_actions.pointer_action.pointer_down()
            chains.w3c_actions.pointer_action.pause(0.05)
            chains.w3c_actions.pointer_action.pointer_up()
            chains.perform()
        except Exception as e:
            self.logger.debug("W3C tap (%s,%s) failed: %s", x, y, e)
        for script_name in ("mobile: tap", "mobile: clickGesture"):
            try:
                self.driver.execute_script(script_name, {"x": x, "y": y})
                return
            except Exception as e:
                self.logger.debug("%s failed at (%s,%s): %s", script_name, x, y, e)

    def tap_anywhere_to_dismiss_share_sheet(self, rounds: int = 2) -> None:
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        points_pct = (
            (0.50, 0.06),
            (0.50, 0.12),
            (0.50, 0.20),
            (0.50, 0.30),
            (0.18, 0.14),
            (0.82, 0.14),
            (0.50, 0.42),
            (0.22, 0.38),
            (0.78, 0.38),
            (0.50, 0.55),
        )
        for _ in range(rounds):
            for xp, yp in points_pct:
                self._tap_coordinate(int(w * xp), int(h * yp))
                time.sleep(0.07)

    def _swipe_down_to_dismiss_modal_sheet(self) -> None:
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        cx = w // 2
        segments = (
            (0.40, 0.88),
            (0.48, 0.92),
            (0.55, 0.94),
        )
        for y0_pct, y1_pct in segments:
            y0, y1 = int(h * y0_pct), int(h * y1_pct)
            try:
                self.driver.swipe(cx, y0, cx, y1, 320)
            except Exception as e:
                self.logger.debug("driver.swipe dismiss failed: %s", e)
            try:
                self.drag_and_drop(cx, y0, cx, y1, steps=6, pause=0.02)
            except Exception as e:
                self.logger.debug("drag_and_drop dismiss failed: %s", e)
            time.sleep(0.12)

    def _apply_share_sheet_dismiss_gestures_once(self) -> None:
        plat = str(self.platform).lower()
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        cx = w // 2

        def _home_restored() -> bool:
            return self.is_quote_more_options_displayed(1)

        self.tap_anywhere_to_dismiss_share_sheet(rounds=1)
        if _home_restored():
            return

        for y_pct in (0.04, 0.07, 0.10, 0.14, 0.18, 0.22):
            self._tap_coordinate(cx, int(h * y_pct))
            time.sleep(0.06)
            if _home_restored():
                return

        self._tap_coordinate(int(w * 0.05), int(h * 0.20))
        self._tap_coordinate(int(w * 0.95), int(h * 0.20))
        if _home_restored():
            return

        self._swipe_down_to_dismiss_modal_sheet()
        if _home_restored():
            return

        if plat == "android":
            for key in (4, 4):
                try:
                    self.driver.press_keycode(key)
                    time.sleep(0.22)
                except Exception as e:
                    self.logger.debug("press_keycode BACK: %s", e)
                if _home_restored():
                    return
            try:
                self.driver.press_keycode(111)
                time.sleep(0.2)
            except Exception as e:
                self.logger.debug("press_keycode ESC: %s", e)

    @allure.step(
        "Dismiss system share sheet until Home quote control is available again"
    )
    def dismiss_system_share_sheet(self, timeout: float = 25.0) -> None:
        plat = str(self.platform).lower()
        deadline = time.perf_counter() + timeout

        while time.perf_counter() < deadline:
            if self.is_quote_more_options_displayed(2):
                self.logger.info(
                    "Share sheet dismissed — Quote More Options visible again"
                )
                time.sleep(0.4)
                return

            self._apply_share_sheet_dismiss_gestures_once()
            time.sleep(0.45)

        self._apply_share_sheet_dismiss_gestures_once()
        if self.is_quote_more_options_displayed(6):
            time.sleep(0.35)
            return

        raise TimeoutError(
            f"Could not dismiss system share sheet within {timeout}s; "
            "Quote More Options did not become available — check device OS share UI."
        )

    @allure.step("Quote overflow → Share → preparing toast → dismiss OS share UI")
    def share_quote_open_sheet_and_dismiss(self) -> None:
        self.click_quote_more_options()
        time.sleep(0.35)
        self.click_share_quote_menu_item()
        self.wait_for_preparing_quote_message_optional(timeout=8.0)
        self.wait_for_preparing_quote_message_gone(timeout=22.0)
        self.wait_for_share_sheet_animation(1.0)
        self.dismiss_system_share_sheet()
        self.dismiss_quote_menu_by_tapping_outside()
