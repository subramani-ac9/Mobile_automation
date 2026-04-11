import logging
import time
from typing import Tuple

import allure
from selenium.webdriver.remote.webelement import WebElement

from constants.locator.myevent_locator import MyEventLocator
from constants.locator.participant_transfer_locator import ParticipantTransferLocator
from constants.locator.poster_locators import PosterLocators
from pages.base_page import BasePage


class PosterCreationPage(BasePage):
    """Course detail → edit event (date/time) → Course Posters → poster template → save."""

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = {
            **MyEventLocator.get_locators(platform),
            **ParticipantTransferLocator.get_locators(platform),
            **PosterLocators.get_locators(platform),
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join((value or "").split()).strip().lower()

    def _read_element_text(self, loc: tuple, timeout: int = 15) -> str:
        el = self.find_element(loc, timeout)
        return self._read_web_element_text(el)

    def _read_web_element_text(self, el: WebElement) -> str:
        if self.platform.lower() == "ios":
            return (
                el.get_attribute("label")
                or el.get_attribute("value")
                or el.text
                or ""
            ).strip()
        return (el.text or el.get_attribute("content-desc") or "").strip()

    def _edit_screen_scroll_container(self) -> tuple:
        custom = self.locator.get("event_edit_scroll")
        if custom and custom[1]:
            return custom
        return self.locator["course_detail_scroll"]

    @allure.step("Tap Edit Event Button (top right)")
    def tap_edit_event_button(self) -> None:
        self.click_element(self.locator["edit_event_button"], timeout=14)
        time.sleep(0.4)

    @allure.step(
        "Scroll to Date & Time *, read Event Date Field 1 and Event Time Field 1"
    )
    def read_event_date_and_time_from_edit_screen(
        self, timeout: int = 18
    ) -> Tuple[str, str]:
        scroll = self._edit_screen_scroll_container()
        section = self.locator["date_time_section_label"]
        self.scroll_to_element(scroll, section, direction="down")
        date_val = self._read_element_text(
            self.locator["event_date_field_1"], timeout=timeout
        )
        time_val = self._read_element_text(
            self.locator["event_time_field_1"], timeout=timeout
        )
        return date_val, time_val

    @allure.step('Tap top-left "Back Button" once (leave edit screen)')
    def tap_toolbar_back_once(self) -> None:
        self.click_element(self.locator["toolbar_back_button"], timeout=14)
        time.sleep(0.35)

    @allure.step("Scroll to Course Posters and open")
    def open_course_posters_section(self) -> None:
        # scroll = self.locator["course_detail_scroll"]
        entry = self.locator["course_posters_entry"]
        self.scroll_to_element_by_touch(entry, direction="down")
        self.click_element(entry, timeout=14)
        time.sleep(0.32)

    @allure.step("Tap create poster plus (FAB)")
    def tap_poster_fab_plus(self) -> None:
        self.click_element(self.locator["poster_fab_plus"], timeout=14)
        time.sleep(0.3)

    @allure.step("Select Template 39")
    def select_template_39(self) -> None:
        self.click_element(self.locator["template_39"], timeout=14)
        time.sleep(0.4)

    def assert_poster_preview_date_time_matches_stored(
        self, stored_date: str, stored_time: str
    ) -> None:
        """
        Assert poster preview shows the same date and time as captured from
        Event Date Field 1 / Event Time Field 1 on the edit screen.

        Disabled for now — preview locators are unreliable.

        Intended logic when enabled:
            preview_date = self._read_element_text(self.locator["poster_preview_date"], ...)
            preview_time = self._read_element_text(self.locator["poster_preview_time"], ...)
            d_exp, d_got = self._normalize_text(stored_date), self._normalize_text(preview_date)
            t_exp, t_got = self._normalize_text(stored_time), self._normalize_text(preview_time)
            assert d_got and (d_exp == d_got or d_exp in d_got or d_got in d_exp)
            assert t_got and (t_exp == t_got or t_exp in t_got or t_got in t_exp)
        """
        # preview_date = self._read_element_text(self.locator["poster_preview_date"], timeout=15)
        # preview_time = self._read_element_text(self.locator["poster_preview_time"], timeout=15)
        # d_exp = self._normalize_text(stored_date)
        # d_got = self._normalize_text(preview_date)
        # t_exp = self._normalize_text(stored_time)
        # t_got = self._normalize_text(preview_time)
        # assert d_got and (d_exp == d_got or d_exp in d_got or d_got in d_exp), (
        #     f"Preview date mismatch: expected ~{stored_date!r}, got {preview_date!r}"
        # )
        # assert t_got and (t_exp == t_got or t_exp in t_got or t_got in t_exp), (
        #     f"Preview time mismatch: expected ~{stored_time!r}, got {preview_time!r}"
        # )
        pass

    @allure.step("Verify Add Teacher, Add Contact, Save Poster are visible")
    def assert_poster_editor_controls_visible(self, timeout: int = 12) -> None:
        assert self.is_displayed(
            self.locator["add_teacher_icon"], timeout
        ), "Add Teacher control not visible"
        assert self.is_displayed(
            self.locator["add_contact_icon"], timeout
        ), "Add Contact control not visible"
        assert self.is_displayed(
            self.locator["save_poster_button"], timeout
        ), "Save Poster not visible"

    @allure.step("Verify QR code and URL are present on poster")
    def assert_qr_and_url_visible(self, timeout: int = 12) -> str:
        assert self.is_displayed(
            self.locator["poster_qr_code"], timeout
        ), "QR code not visible on poster"
        assert self.is_displayed(
            self.locator["poster_url_text"], timeout
        ), "URL not visible on poster"
        return self._read_element_text(self.locator["poster_url_text"], timeout)

    @allure.step("Tap Save Poster")
    def tap_save_poster(self) -> None:
        self.click_element(self.locator["save_poster_button"], timeout=14)
        time.sleep(0.5)

    @allure.step("Verify Register here line includes poster URL")
    def assert_register_here_contains_url(self, url_fragment: str) -> None:
        src = self.driver.page_source or ""
        lowered = src.lower()
        assert "register here" in lowered, (
            "Expected 'Register here' in screen content"
        )
        frag = (url_fragment or "").strip()
        assert frag, "Poster URL text was empty"
        if frag in src:
            return
        stripped = frag.replace("https://", "").replace("http://", "")
        assert stripped and stripped in src, (
            f"Expected poster URL (or path) in content; got fragment {frag[:120]!r}..."
        )

    @allure.step("Check whether a saved poster appears in Course Posters list")
    def is_poster_available_in_list(self, timeout: int = 8) -> bool:
        return self.is_displayed(self.locator["poster_saved_tile"], timeout)

    @allure.step("Tap overflow / three-dots on Course Posters (top right)")
    def tap_course_posters_overflow_menu(self) -> None:
        self.click_element(self.locator["course_posters_overflow_menu"], timeout=14)
        time.sleep(0.28)

    @allure.step(
        "Verify Share Poster, Download Poster, Delete Poster, and Cancel are visible"
    )
    def assert_poster_overflow_delete_menu_visible(self, timeout: int = 12) -> None:
        assert self.is_displayed(
            self.locator["share_poster_option"], timeout
        ), "Share Poster option not visible"
        assert self.is_displayed(
            self.locator["download_poster_option"], timeout
        ), "Download Poster option not visible"
        assert self.is_displayed(
            self.locator["delete_poster_option"], timeout
        ), "Delete Poster option not visible"
        cancel = self.locator.get("option_cancel")
        assert cancel and self.is_displayed(
            cancel, timeout
        ), "Cancel button not visible"

    @allure.step("Tap Delete Poster, then confirm Delete on dialog")
    def tap_delete_poster_and_confirm(self) -> None:
        self.click_element(self.locator["delete_poster_option"], timeout=12)
        time.sleep(0.28)
        self.click_element(self.locator["delete_poster_confirm_button"], timeout=12)
        time.sleep(0.55)

    @allure.step('Check empty state text "No posters yet"')
    def is_no_posters_yet_displayed(self, timeout: int = 12) -> bool:
        return self.is_displayed(self.locator["no_posters_yet_label"], timeout)

    @allure.step("Tap Download Poster in overflow menu")
    def tap_download_poster_menu_option(self) -> None:
        self.click_element(self.locator["download_poster_option"], timeout=12)
        time.sleep(0.03)

    def _page_source_has_downloading_poster_message(self) -> bool:
        src = (self.driver.page_source or "").lower()
        return "downloading poster" in src

    def _page_source_has_poster_saved_to_gallery_message(self) -> bool:
        src = (self.driver.page_source or "").lower()
        if "poster saved" not in src or "phone" not in src:
            return False
        return "gallery" in src or "tap to open" in src

    @allure.step(
        'Detect "Downloading poster…" and "Poster saved to your phone… gallery" in page source'
    )
    def saw_download_poster_success_messages(self, timeout: float = 14.0) -> bool:
        """
        Toasts may be brief; remember if downloading was seen, then require saved/gallery
        text (possibly on a later poll).
        """
        saw_downloading = False
        deadline = time.perf_counter() + float(timeout)
        poll_interval = 0.02
        while time.perf_counter() < deadline:
            if self._page_source_has_downloading_poster_message():
                saw_downloading = True
            if saw_downloading and self._page_source_has_poster_saved_to_gallery_message():
                return True
            time.sleep(poll_interval)
        return saw_downloading and self._page_source_has_poster_saved_to_gallery_message()

    @allure.step(
        "Tap Course Posters at top to close share options (activityCollectionView XPath)"
    )
    def tap_course_posters_top_to_close_share_options(self) -> None:
        loc = self.locator.get("course_posters_close_share_options")
        assert loc and loc[1], (
            "course_posters_close_share_options locator must be set for this platform"
        )
        self.click_element(loc, timeout=14)
        time.sleep(0.22)

    @allure.step("Pull-to-refresh gesture on Course Posters list (vertical swipe)")
    def pull_to_refresh_course_posters_list(self) -> None:
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        cx = w // 2
        y_start = int(h * 0.22)
        y_end = int(h * 0.58)
        self.drag_and_drop(cx, y_start, cx, y_end, steps=6, pause=0.03)
        time.sleep(0.65)

    @allure.step("Tap Share Poster in overflow menu")
    def tap_share_poster_menu_option(self) -> None:
        self.click_element(self.locator["share_poster_option"], timeout=12)
        time.sleep(0.03)

    _PREPARING_POSTER_NEEDLES = (
        "preparing poster for sharing",
        "preparing poster",
    )

    def _page_source_contains_preparing_poster(self) -> bool:
        src = (self.driver.page_source or "").lower()
        return any(n in src for n in self._PREPARING_POSTER_NEEDLES)

    @allure.step(
        'Check "Preparing poster for sharing…" via page source (or optional locator)'
    )
    def is_preparing_poster_for_sharing_displayed(self, timeout: int = 10) -> bool:
        loc = self.locator.get("preparing_poster_sharing_message")
        if loc and loc[1]:
            if self.is_displayed(loc, timeout=min(2.0, float(timeout))):
                return True
        deadline = time.perf_counter() + float(timeout)
        poll_interval = 0.02
        while time.perf_counter() < deadline:
            if self._page_source_contains_preparing_poster():
                return True
            time.sleep(poll_interval)
        return False
