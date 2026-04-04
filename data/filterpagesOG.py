from pages.base_page import BasePage
from constants.locator.filters_locator import FiltersLocator
import logging
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FiltersPage(BasePage):
    """
    Two independent scroll surfaces (must not mix gestures):

    - **Left category rail** — only `scroll_category_rail_to_desc` / `_touch_scroll_left_category_rail`.
    - **Right options list** — only `scroll_filter_options_to_desc` / inner option scrollers / right-edge swipes.

    Never use full-screen touch for categories (it moves the options list first).
    Never use `UiScrollable.instance(N)` for options (N can be the category rail).
    """

    # Horizontal center of a scroll container below this fraction of screen width ⇒ treat as left rail only.
    _LEFT_RAIL_MAX_CENTER_X_RATIO = 0.38
    # Short visibility poll during scroll loops (default is_displayed waits are too long per iteration).
    _VIS_TIMEOUT = 0.45
    _OPTION_ANCHOR_WAIT = 3

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locators = FiltersLocator.get_locators(platform)
        self.logger = logging.getLogger(__name__)

    def _is_visible_quick(self, locator: tuple, timeout: float | None = None) -> bool:
        t = self._VIS_TIMEOUT if timeout is None else timeout
        try:
            return self.is_displayed(locator, timeout=t)
        except Exception:
            return False

    def _horizontal_center_x(self, element) -> float:
        r = element.rect
        return r["x"] + r["width"] / 2.0

    def _is_left_rail_scroll_container(self, scroll_el) -> bool:
        """True if this scrollable sits over the narrow left column — must not be used to scroll options."""
        try:
            w = self.driver.get_window_size()["width"]
            return self._horizontal_center_x(scroll_el) < w * self._LEFT_RAIL_MAX_CENTER_X_RATIO
        except Exception:
            return False

    # --- Category rail (left column only) ---

    def _fast_vertical_swipe(self, x: int, y0: int, y1: int) -> None:
        """Fewer steps than default drag_and_drop — much faster per swipe."""
        self.drag_and_drop(x, y0, x, y1, steps=3, pause=0.03)

    def _touch_scroll_left_category_rail(self, target: tuple, max_swipes: int = 10) -> None:
        """Vertical swipes over the **left** strip so the right options column is not scrolled."""
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        x = int(w * 0.20)
        y_lo, y_hi = int(h * 0.78), int(h * 0.22)
        for _ in range(max_swipes):
            if self._is_visible_quick(target):
                return
            self._fast_vertical_swipe(x, y_lo, y_hi)
            time.sleep(0.08)
        for _ in range(max_swipes):
            if self._is_visible_quick(target):
                return
            self._fast_vertical_swipe(x, y_hi, y_lo)
            time.sleep(0.08)

    def scroll_category_rail_to_desc(self, content_desc: str):
        """Scroll **only** the left category list until the category button is visible."""
        target = (AppiumBy.ACCESSIBILITY_ID, content_desc)
        plat = (self.platform or "").lower()

        if self._is_visible_quick(target):
            return self.find_element(target)

        if plat == "ios":
            self._touch_scroll_left_category_rail(target)
            return self.find_element(target)

        category_scroller = (AppiumBy.XPATH, FiltersLocator.ANDROID_CATEGORY_RAIL_SCROLLER_XPATH)
        self._bounded_scroll_gesture(category_scroller, target, "down", max_gestures=5)
        if not self._is_visible_quick(target):
            self._bounded_scroll_gesture(category_scroller, target, "up", max_gestures=5)
        if not self._is_visible_quick(target):
            self.logger.info("Left-rail touch scroll for category: %s", content_desc)
            self._touch_scroll_left_category_rail(target)
        return self.find_element(target)

    # --- Options column (right side only) ---

    def _wait_for_any_option_checkbox(self, timeout: int | None = None) -> None:
        t = self._OPTION_ANCHOR_WAIT if timeout is None else timeout
        anchor = (AppiumBy.XPATH, FiltersLocator.ANDROID_OPTIONS_CHECKBOX_XPATH)
        WebDriverWait(self.driver, t).until(EC.presence_of_element_located(anchor))

    def _bounded_scroll_gesture(
        self, scroll_locator: tuple, target: tuple, direction: str, max_gestures: int = 5
    ) -> bool:
        """Like scroll_to_element but capped gestures + fast visibility checks (avoids long base_page loops)."""
        try:
            el = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(scroll_locator))
        except Exception as e:
            self.logger.debug("Scroller not found %s: %s", scroll_locator, e)
            return self._is_visible_quick(target)
        cmd = "mobile: scrollGesture"
        for _ in range(max_gestures):
            if self._is_visible_quick(target):
                return True
            try:
                can = self.driver.execute_script(
                    cmd,
                    {"elementId": el.id, "direction": direction, "percent": 0.68},
                )
            except Exception as e:
                self.logger.debug("scrollGesture: %s", e)
                break
            if not can:
                break
            time.sleep(0.035)
        return self._is_visible_quick(target)

    def _scroll_gesture_on_web_element(self, scroll_el, target: tuple, direction: str, max_swipes: int = 8) -> bool:
        cmd = "mobile: scrollGesture"
        for _ in range(max_swipes):
            if self._is_visible_quick(target):
                return True
            try:
                can = self.driver.execute_script(
                    cmd,
                    {"elementId": scroll_el.id, "direction": direction, "percent": 0.72},
                )
            except Exception as e:
                self.logger.debug("scrollGesture failed: %s", e)
                break
            if not can:
                break
            time.sleep(0.035)
        return self._is_visible_quick(target)

    def _option_checkbox_scroll_containers(self):
        """
        Scrollable ancestors of the first **right-column** option checkbox.
        Drops any container whose center lies in the left rail (same scroll surface as categories).
        """
        xpath = f"({FiltersLocator.ANDROID_OPTIONS_CHECKBOX_XPATH})[1]/ancestor::*[@scrollable='true']"
        scrollers = self.driver.find_elements(AppiumBy.XPATH, xpath)
        filtered = [el for el in scrollers if not self._is_left_rail_scroll_container(el)]
        self.logger.debug(
            "Option scroll containers: %d total, %d after removing left-rail",
            len(scrollers),
            len(filtered),
        )
        return filtered

    def _scroll_inner_options_lists(self, target: tuple) -> bool:
        try:
            self._wait_for_any_option_checkbox()
        except Exception as e:
            self.logger.warning("No option checkbox yet: %s", e)
            return self._is_visible_quick(target)

        for sc_el in self._option_checkbox_scroll_containers():
            if self._is_visible_quick(target):
                return True
            for direction in ("down", "up"):
                if self._scroll_gesture_on_web_element(sc_el, target, direction):
                    return True
        return self._is_visible_quick(target)

    def _touch_scroll_right_options_column(self, target: tuple, max_swipes: int = 12) -> None:
        """Vertical swipes over the **right** strip — does not scroll the category rail."""
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        x = int(w * 0.74)
        y_lo, y_hi = int(h * 0.78), int(h * 0.22)
        for _ in range(max_swipes):
            if self._is_visible_quick(target):
                return
            self._fast_vertical_swipe(x, y_lo, y_hi)
            time.sleep(0.08)
        for _ in range(max_swipes):
            if self._is_visible_quick(target):
                return
            self._fast_vertical_swipe(x, y_hi, y_lo)
            time.sleep(0.08)

    def _fast_fullscreen_touch_scroll(self, target: tuple, max_swipes: int = 10) -> None:
        """Last-resort scroll — faster than base_page.scroll_to_element_by_touch (shorter waits & drags)."""
        size = self.driver.get_window_size()
        cx = size["width"] // 2
        h = size["height"]
        y_lo, y_hi = int(h * 0.82), int(h * 0.18)
        for _ in range(max_swipes):
            if self._is_visible_quick(target):
                return
            self._fast_vertical_swipe(cx, y_lo, y_hi)
            time.sleep(0.08)
        for _ in range(max_swipes):
            if self._is_visible_quick(target):
                return
            self._fast_vertical_swipe(cx, y_hi, y_lo)
            time.sleep(0.08)

    def _uiautomator_scroll_into_view_option(self, content_desc: str) -> None:
        """Single cheap call when it works — avoids many gesture iterations."""
        safe = content_desc.replace('"', '\\"')
        ui_selector = (
            f'new UiScrollable(new UiSelector().scrollable(true))'
            f'.scrollIntoView(new UiSelector().description("{safe}"))'
        )
        try:
            self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
        except Exception:
            pass

    def scroll_filter_options_to_desc(self, content_desc: str):
        """
        Scroll **only** options (right column / inner list / full dialog), never the category rail.
        Order: inner right scrollables (excluding left rail) → outer dialog → UiScrollable by description
        → right-edge swipes → last-resort full-screen touch.
        """
        target = (AppiumBy.ACCESSIBILITY_ID, content_desc)
        plat = (self.platform or "").lower()

        if self._is_visible_quick(target):
            return self.find_element(target)

        if plat == "ios":
            self._touch_scroll_right_options_column(target, max_swipes=10)
            if not self._is_visible_quick(target):
                self._fast_fullscreen_touch_scroll(target, max_swipes=10)
            return self.find_element(target)

        # 1) Often succeeds in one round-trip — run before heavier loops
        self._uiautomator_scroll_into_view_option(content_desc)
        if self._is_visible_quick(target):
            return self.find_element(target)

        # 2) Right-column inner scrollables (excluding left-rail containers)
        self._scroll_inner_options_lists(target)

        # 3) Whole dialog — bounded gestures only (base scroll_to_element can run very long)
        dialog_scroller = (AppiumBy.XPATH, FiltersLocator.ANDROID_FILTER_DIALOG_SCROLLER_XPATH)
        if not self._is_visible_quick(target):
            self._bounded_scroll_gesture(dialog_scroller, target, "down", max_gestures=5)
        if not self._is_visible_quick(target):
            self._bounded_scroll_gesture(dialog_scroller, target, "up", max_gestures=5)

        # 4) UiAutomator again after layout may have changed
        if not self._is_visible_quick(target):
            self._uiautomator_scroll_into_view_option(content_desc)

        # 5) Right-column touch
        if not self._is_visible_quick(target):
            self.logger.debug("Right-column touch scroll for option: %s", content_desc)
            self._touch_scroll_right_options_column(target)

        # 6) Last resort — avoid base_page.scroll_to_element_by_touch (2s waits per swipe)
        if not self._is_visible_quick(target):
            self.logger.debug("Full-screen touch fallback for option: %s", content_desc)
            self._fast_fullscreen_touch_scroll(target, max_swipes=10)

        return self.find_element(target)

    
    # --- Panel actions ---

    def open_filters(self):
        try:
            self.click_element(self.locators["header_filter_button"])
            self.logger.info("Filters panel opened successfully")
        except Exception as e:
            self.logger.error(f"Exception raised while opening the filters panel, exception:: {str(e)}")
            raise Exception(f"Unable to open the filters panel")

    def apply_filters(self):
        try:
            self.click_element(self.locators["filter_show_result_button"])
            self.logger.info("Filters applied successfully")
        except Exception as e:
            self.logger.error(f"Exception raised while applying the filters, exception:: {str(e)}")
            raise Exception(f"Unable to apply the filters")

    def reset_filters(self):
        try:
            self.click_element(self.locators["filter_reset_button"])
            self.logger.info("Filters reset successfully")
        except Exception as e:
            self.logger.error(f"Exception raised while resetting the filters, exception:: {str(e)}")
            raise Exception(f"Unable to reset the filters")

    def click_filter_category(self, category):
        try:
            locator = self.locators[category]
            raw = locator[1]
            if callable(raw):
                raise ValueError(f"Category {category} uses dynamic locator; not supported as filter section header")
            text = raw

            element = self.scroll_category_rail_to_desc(text)
            element.click()
            self.logger.info(f"Filter category {category} clicked successfully")
        except Exception as e:
            self.logger.error(f"Exception raised while clicking the filter category {category}, exception:: {str(e)}")
            raise Exception(f"Unable to click the filter category {category}")

    def select_filter_option(self, option_key, startDate=None, endDate=None):
        try:
            locator = self.locators[option_key]
            raw = locator[1]
            if callable(raw):
                raise ValueError(f"Option {option_key} uses dynamic locator; pass resolved value separately")
            text = raw

            element = self.scroll_filter_options_to_desc(text)
            element.click()
            self.logger.info(f"Filter option {option_key} clicked successfully")
            if(option_key == "filter_schedule_custom_checkBox"):
                self.click_element(self.locators["filter_schedule_date_range_picker"])
                startDate = self.build_locator(self.locators["range_start_date"], startDate)
                endDate = self.build_locator(self.locators["range_end_date"], endDate)
                self.click_element(startDate)
                self.click_element(endDate)
                self.click_element(self.locators["Save_button"])
                self.logger.info(f"Filter schedule custom date range {startDate} - {endDate} clicked successfully")
        except Exception as e:
            self.logger.error(f"Exception raised while selecting the filter option {option_key}, exception:: {str(e)}")
            raise Exception(f"Unable to select the filter option {option_key}")

    def apply_filter_combination(self, filters: dict, startDate=None, endDate=None):
        """
        Supports:
        - single selection
        - multiple selection (checkbox)
        - schedule (radio button)

        Example:
        {
            "filter_type": "filter_type_meetup_checkBox",
            "filter_mode": ["filter_mode_online_checkBox", "filter_mode_in_person_checkBox"],
            "filter_schedule": "filter_schedule_upcoming_checkBox"
        }
        """
        try:
            try:
                self.open_filters()
                self.logger.info("Filters opened successfully")
            except Exception as e:
                self.logger.error(f"Exception raised while opening the filters, exception:: {str(e)}")
                raise Exception(f"Unable to open the filters")

            for category, options in filters.items():
                self.click_filter_category(category)
                self.logger.info(f"Filter category {category} clicked successfully")

                if isinstance(options, list):
                    for option in options:
                        self.select_filter_option(option, startDate, endDate)
                        self.logger.info(f"Filter option {option} clicked successfully")
                else:
                    # Same path as list items: scroll options column only, then click
                    self.select_filter_option(options, startDate, endDate)
                    self.logger.info(f"Filter option {options} clicked successfully")

            try:
                self.apply_filters()
                self.logger.info("Filters applied successfully")
                time.sleep(20)
            except Exception as e:
                self.logger.error(f"Exception raised while applying the filters, exception:: {str(e)}")
                raise Exception(f"Unable to apply the filters")

        except Exception as e:
            self.logger.error(f"Exception raised while applying the filters combination, exception:: {str(e)}")
            raise Exception(f"Unable to apply the filters combination")

    def extract_page_contents(self):
        import re
        source = self.driver.page_source
        pattern = re.compile(r'(?:text|content-desc|label|name|value)="([^"]+)"')
        matches = pattern.findall(source)
        return sorted(set(m.strip() for m in matches if m.strip()))

    def verify_by_text(self, expected_keywords):
        content = self.extract_page_contents()
        return all(
            any(exp.lower() in text.lower() for text in content)
            for exp in expected_keywords
        )

    def verify_by_elements(self, keyword):
        elements = self.driver.find_elements("xpath", "//*")
        for el in elements:
            text = el.get_attribute("content-desc") or el.get_attribute("text") or ""
            if keyword.lower() in text.lower():
                return True
        return False
