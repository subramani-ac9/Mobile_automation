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

    def scroll_category_rail_to_desc(self, text, max_swipes=10):
        for i in range(max_swipes):
            try:
                element = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, text)
                return element
            except:
                prev_source = self.driver.page_source

                # LEFT PANEL swipe (X small)
                self.driver.swipe(178, 1900, 178, 1450, 800)

                new_source = self.driver.page_source

                if prev_source == new_source:
                    raise Exception(f"No element found in LEFT panel: {text}")

        raise Exception(f"No element found in LEFT panel after {max_swipes} swipes: {text}")

    def scroll_filter_options_to_desc(self, text, max_swipes=10):
        for i in range(max_swipes):
            try:
                element = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, text)
                return element
            except:
                prev_source = self.driver.page_source

                # RIGHT PANEL swipe (X large)
                self.driver.swipe(700, 1900, 700, 1450, 800)

                new_source = self.driver.page_source

                if prev_source == new_source:
                    raise Exception(f"No element found in RIGHT panel: {text}")

        raise Exception(f"No element found in RIGHT panel after {max_swipes} swipes: {text}")
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

    def _calendar_picker_scroll_rect(self):
        """Lower-screen bounds so scroll gestures target the date sheet, not the filter column."""
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        return {
            "left": int(w * 0.06),
            "top": int(h * 0.30),
            "width": int(w * 0.88),
            "height": int(h * 0.60),
        }

    def _calendar_scroll(self, direction: str, percent: float = 0.9):
        """
        Same semantics as BasePage.scroll_to_element_by_touch:
        - 'up' — reveal content above / scroll toward the top of the picker (finger swipe down).
        - 'down' — reveal content below (finger swipe up).
        """
        if self.platform == "android":
            rect = self._calendar_picker_scroll_rect()
            self.driver.execute_script("mobile: scrollGesture", {
                **rect,
                "direction": direction,
                "percent": percent,
            })
        else:
            rect = self._calendar_picker_scroll_rect()
            cx = rect["left"] + rect["width"] // 2
            mid_y = rect["top"] + rect["height"] // 2
            span = max(int(rect["height"] * 0.35), 120)
            if direction == "up":
                self.drag_and_drop(cx, mid_y - span // 2, cx, mid_y + span // 2)
            else:
                self.drag_and_drop(cx, mid_y + span // 2, cx, mid_y - span // 2)

    def _find_visible_calendar_cell(self, locator):
        """Return the element if it exists and is displayed; otherwise None."""
        try:
            el = self.driver.find_element(*locator)
            if el.is_displayed():
                return el
        except Exception:
            pass
        return None

    def locate_calendar_day_cell(self, locator, max_swipes_up=20, max_swipes_down=25):
        """
        Find a day cell in the range picker:
        1. If already visible, return it (caller clicks).
        2. Scroll up toward the top; after each swipe, if the cell becomes visible, return it immediately.
        3. When the calendar can no longer scroll up (at top) and the cell is still missing, scroll down
           until it appears.
        """
        found = self._find_visible_calendar_cell(locator)
        if found is not None:
            return found

        unchanged_streak = 0
        for _ in range(max_swipes_up):
            prev = self.driver.page_source
            self._calendar_scroll("up", 1.0)
            found = self._find_visible_calendar_cell(locator)
            if found is not None:
                return found
            if self.driver.page_source == prev:
                unchanged_streak += 1
                if unchanged_streak >= 2:
                    break
            else:
                unchanged_streak = 0

        for _ in range(max_swipes_down):
            found = self._find_visible_calendar_cell(locator)
            if found is not None:
                return found
            prev = self.driver.page_source
            self._calendar_scroll("down", 1.0)
            if self.driver.page_source == prev:
                break

        found = self._find_visible_calendar_cell(locator)
        if found is not None:
            return found
        raise Exception(f"Calendar day cell not found after up/down scrolls: {locator}")

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
                time.sleep(0.5)
                start_locator = self.build_locator(self.locators["range_start_date"], startDate)
                end_locator = self.build_locator(self.locators["range_end_date"], endDate)

                self.click_element(self.locate_calendar_day_cell(start_locator))
                self.click_element(self.locate_calendar_day_cell(end_locator))
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
            self.logger.info(
                "apply_filter_combination | categories=%s | startDate=%r | endDate=%r",
                list(filters.keys()) if filters else [],
                startDate,
                endDate,
            )
            try:
                self.open_filters()
                self.logger.info("Filters panel opened")
            except Exception as e:
                self.logger.error(f"Exception raised while opening the filters, exception:: {str(e)}")
                raise Exception(f"Unable to open the filters")

            for category, options in filters.items():
                self.logger.info("apply_filter_combination | selecting category %r", category)
                self.click_filter_category(category)
                self.logger.info("apply_filter_combination | category %r header clicked", category)

                if isinstance(options, list):
                    for j, option in enumerate(options):
                        self.logger.info(
                            "apply_filter_combination | category %r option %d/%d %r",
                            category,
                            j + 1,
                            len(options),
                            option,
                        )
                        self.select_filter_option(option, startDate, endDate)
                else:
                    self.logger.info(
                        "apply_filter_combination | category %r single option %r",
                        category,
                        options,
                    )
                    self.select_filter_option(options, startDate, endDate)

            try:
                self.logger.info("apply_filter_combination | tapping Show Filter Results")
                self.apply_filters()
                self.logger.info("apply_filter_combination | Show Filter Results confirmed; waiting for UI")
                time.sleep(3)
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
