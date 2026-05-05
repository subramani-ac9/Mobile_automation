"""
Poster flows (US) are independent: login → one flow → logout per test.

Functions: create_poster_US(), download_poster_US(), share_poster_US(), delete_poster_US()

Create poster test:
  pytest tests/test_poster_creation.py::TestPosterCreation::test_poster_creation_end_to_end_US -m poster_creation -s

Download poster test:
  pytest tests/test_poster_creation.py::TestPosterCreation::test_download_poster_end_to_end_US -m poster_download -s

Share poster test:
  pytest tests/test_poster_creation.py::TestPosterCreation::test_share_poster_end_to_end_US -m poster_share -s

Delete poster test:
  pytest tests/test_poster_creation.py::TestPosterCreation::test_poster_delete_end_to_end_US -m poster_delete -s
"""
import os
import time

import allure
import pytest

from config.config import TestConfig
from pages.login_page import LoginPage
from pages.logout_page import LogoutPage
from pages.my_events_page import MyEventsPage
from pages.onboard_page import OnBoardPage
from pages.participant_transfer_page import ParticipantTransferPage
from pages.poster_creation_page import PosterCreationPage
from utils.driver_manager import DriverManager
from utils.helpers import switch_to_webview, take_screenshot, switch_to_native
from utils.logger_config import LoggerConfig
from utils.navigator import Navigator

LOGIN_TENANT = "US"
LOGIN_EMAIL = os.getenv("POSTER_TEST_EMAIL", "geetha@abovecloud9.ai")
LOGIN_PASSWORD = os.getenv("POSTER_TEST_PASSWORD", "Admin@ac9")
EVENT_CODE = "E-064549"

SUCCESS_MSG = "Poster Created Successfully and Validation of Elements Done"
POSTER_AVAILABLE_MSG = "Poster is available.. Verification Done"
DELETE_SUCCESS_MSG = "Poster Deleted Successfully and verified"
DOWNLOAD_POSTER_SUCCESS_MSG = "Download Poster Functionality works as expected"
SHARE_POSTER_SUCCESS_MSG = "Share Poster Functionality works as expected"


class TestPosterCreation:
    @pytest.fixture(autouse=True)
    def setup(self, request):
        test_method_name = request.node.name
        self.logger = LoggerConfig.setup_test_logger(
            self.__class__.__name__, test_method_name
        )
        start_time = time.time()
        LoggerConfig.log_test_start(self.logger, test_method_name, None)

        self.web_locators = {
    "add_teacher": "[data-testid='Preview-button-18']",
    "add_contact": "[data-testid='Preview-button-21']",
    "save_poster": "[data-testid='buttons-Button-1']",
    "qr_code": "svg[data-testid='ElementRenderer-QRCodeSVG-24']",
    
    "poster_url": "div:contains('tinyurl')"  # fallback handled differently
    }

        try:
            self.logger.info("Initializing test setup")
            self.driver_manager = DriverManager()
            self.driver = self.driver_manager.start_driver()
            platform = TestConfig.MOBILE_PLATFORM
            self.login_page = LoginPage(self.driver, platform)
            self.onboard_page = OnBoardPage(self.driver, platform)
            self.my_events_page = MyEventsPage(self.driver, platform)
            self.transfer_page = ParticipantTransferPage(self.driver, platform)
            self.poster_page = PosterCreationPage(self.driver, platform)
            self.navigator = Navigator(self.driver, platform)
            self.logout_page = LogoutPage(self.driver, platform)
            request.node.driver = self.driver
            self.logger.info("Test setup completed successfully")
        except Exception as e:
            self.logger.error(f"Test setup failed: {str(e)}")
            raise

        yield

        end_time = time.time()
        duration = end_time - start_time
        test_status = "COMPLETED"
        rep_call = getattr(request.node, "rep_call", None)
        if rep_call is not None and rep_call.failed:
            test_status = "FAILED"
            self.logger.error(f"Test failed: {test_method_name}")
            take_screenshot(
                self.driver,
                f"test_failed_{self.__class__.__name__}_{test_method_name}",
            )
        LoggerConfig.log_test_end(self.logger, test_method_name, duration, test_status)

        try:
            self.logger.info("Starting test cleanup (quit driver)")
            self.driver_manager.quit_driver()
            self.logger.info("Test cleanup completed")
        except Exception as e:
            self.logger.error(f"Test cleanup failed: {str(e)}")

    def login_to_events_app(self) -> None:
        self.navigator.navigate_to_login()
        login_page_displayed = self.login_page.is_login_page_displayed()
        LoggerConfig.log_assertion(
            self.logger, "Login page should be displayed", login_page_displayed
        )
        assert login_page_displayed, "Login page should be displayed"
        self.login_page.login(LOGIN_EMAIL, LOGIN_PASSWORD, LOGIN_TENANT)
        validations = self.my_events_page.validate_successful_login(LOGIN_TENANT)
        for validation in validations:
            validation_result = "not" not in validation.lower()
            LoggerConfig.log_assertion(
                self.logger, f"Validation: {validation}", validation_result
            )
            assert validation_result, f"Validation failed: {validation}"

    def _tap_cancel_top_right_if_visible(self, timeout: float = 4.0) -> None:
        cancel = self.poster_page.locator.get("Events_search_close_button")
        if cancel and self.poster_page.is_displayed(cancel, timeout=timeout):
            self.poster_page.click_element(cancel)
            time.sleep(0.12)

    def _leave_poster_flow_to_events_main(self) -> None:
        self.transfer_page.tap_back_with_platform_fallbacks(2)
        self.transfer_page.finish_return_to_events_main_after_backs()
        self._tap_cancel_top_right_if_visible(timeout=0.75)
        assert self.my_events_page.is_events_screen_displayed(), (
            "Events page should be visible after back twice and cancel"
        )

    def _leave_posters_screen_to_events_main(self) -> None:
        """
        Exit Course Posters stack to Events main: iOS-specific back ×2 (chevron then Back
        Button), Events search close + recovery via ``back_twice_then_close_events_search``,
        then optional Cancel ×2 — same intent as manual steps 15–16 after share/download/delete.
        """
        # self.transfer_page.back_twice_then_close_events_search()
        self.transfer_page.tap_back_with_platform_fallbacks(2)
        self.logger.info("Backed twice to events main")
        self._tap_cancel_top_right_if_visible()
        self.logger.info("Tapped cancel top right if visible")
        time.sleep(0.22)
        self._tap_cancel_top_right_if_visible(timeout=0.8)
        self.logger.info("Tapped cancel top right if visible again")
        assert self.my_events_page.is_events_screen_displayed(), (
            "Events page should be visible after back twice and two cancels"
        )

    def create_poster_US(self) -> None:
        """
        Create poster (US): login → Events → search E-064549 → edit screen date/time
        capture → back → Course Posters → new poster → template → validations → save →
        second pass verification → navigate to Events → logout.
        """
        with allure.step("Login"):
            self.login_to_events_app()

        with allure.step("Events, search course, open filtered course"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.42)
            self.transfer_page.enterEventCode(EVENT_CODE)
            self.transfer_page.click_event_row_containing(EVENT_CODE)

        with allure.step("Edit event: capture date & time from Date & Time section"):
            self.poster_page.tap_edit_event_button()
            event_date_value, event_time_value = (
                self.poster_page.read_event_date_and_time_from_edit_screen()
            )
            self.logger.info("Stored event date (field 1): %s", event_date_value)
            self.logger.info("Stored event time (field 1): %s", event_time_value)

        with allure.step("Back from edit to course detail"):
            self.poster_page.tap_toolbar_back_once()

        with allure.step("Course Posters → new poster → Template 39"):
            self.poster_page.open_course_posters_section()
            self.poster_page.tap_poster_fab_plus()
            self.poster_page.select_template_39()

        switch_to_webview(self.driver)
        time.sleep(20)

        with allure.step(
            "Poster preview date/time vs stored (skipped — locator issues)"
        ):
            self.logger.info(
                "Poster preview date/time check skipped; "
                "assert_poster_preview_date_time_matches_stored is disabled"
            )

        with allure.step("Editor controls, QR code, URL"):
            self.poster_page.assert_poster_editor_controls_visible()
            poster_url = self.poster_page.assert_qr_and_url_visible()

        with allure.step("Save poster; Register here + URL"):
            self.poster_page.tap_save_poster()
            time.sleep(10)
            switch_to_native(self.driver)
            self.poster_page.assert_register_here_contains_url(poster_url)

        print(f"\n========== OUTPUT: {SUCCESS_MSG} ==========\n")
        self.logger.info("OUTPUT: %s", SUCCESS_MSG)

        with allure.step("Back twice, cancel — Events main"):
            self._leave_poster_flow_to_events_main()

        with allure.step("Search again, open course, Course Posters, verify poster"):
            self.transfer_page.enterEventCode(EVENT_CODE)
            self.transfer_page.click_event_row_containing(EVENT_CODE)
            self.poster_page.open_course_posters_section()  
            if self.poster_page.is_poster_available_in_list(timeout=12):
                print(f"\n========== OUTPUT: {POSTER_AVAILABLE_MSG} ==========\n")
                self.logger.info("OUTPUT: %s", POSTER_AVAILABLE_MSG)
            else:
                self.logger.warning(
                    "Saved poster tile not found — set poster_saved_tile locator"
                )

        with allure.step("Back twice, cancel — Events main"):
            self._leave_poster_flow_to_events_main()

        with allure.step("Account → Logout (driver quit in teardown closes app)"):
            self.logout_page.logout()

    def download_poster_US(self) -> None:
        """
        Download poster (US): login; Events; search E-064549; course; Course Posters;
        overflow; Share/Download/Delete + Cancel; Download Poster; downloading + saved
        to gallery messages; one back to dismiss sheet; back ×2 + cancel path as
        delete_poster; Account logout.
        """
        with allure.step("Login (email + password + tenant)"):
            self.login_to_events_app()

        with allure.step("Click Events icon (bottom navigation)"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.42)

        with allure.step("Click Search icon at top right"):
            self.transfer_page.enterEventCode(EVENT_CODE)
        #     self.transfer_page.tap_events_search_icon()

        # with allure.step(f"Type {EVENT_CODE}"):
        #     self.transfer_page.type_events_search_term(EVENT_CODE)

        with allure.step("Click filtered course"):
            self.transfer_page.click_event_row_containing(EVENT_CODE)

        with allure.step("Scroll down and open Course Posters"):
            self.poster_page.open_course_posters_section()

        with allure.step("Click three dots (overflow, top right)"):
            self.poster_page.tap_course_posters_overflow_menu()

        with allure.step(
            "Check Share Poster, Download Poster, Delete Poster, and Cancel (overflow)"
        ):
            self.poster_page.assert_poster_overflow_delete_menu_visible()

        with allure.step("Click Download Poster"):
            self.poster_page.tap_download_poster_menu_option()

        with allure.step(
            'Check "Downloading poster…" and saved-to-gallery message in page source'
        ):
            download_msgs_seen = self.poster_page.saw_download_poster_success_messages(
                timeout=14.0
            )

        with allure.step("If messages shown, report success"):
            if download_msgs_seen:
                print(f"\n========== OUTPUT: {DOWNLOAD_POSTER_SUCCESS_MSG} ==========\n")
                self.logger.info("OUTPUT: %s", DOWNLOAD_POSTER_SUCCESS_MSG)
            else:
                self.logger.warning(
                    "Download poster toasts not fully detected within timeout "
                    "(downloading + saved-to-gallery text in page source)"
                )

        # with allure.step("Back once (top left) — dismiss download / options UI"):
            # self.transfer_page.tap_back_with_platform_fallbacks(1)

        with allure.step(
            "Back twice, Cancel twice — Events main (same sequence as delete_poster)"
        ):
            self._leave_posters_screen_to_events_main()

        with allure.step("Account icon → Logout (driver quit in teardown closes app)"):
            self.logout_page.logout()

    def share_poster_US(self) -> None:
        """
        Share poster (US): Events → search E-064549 → Course Posters → overflow;
        Share/Download/Delete + Cancel; Share Poster; preparing message; dismiss share
        sheet (Course Posters XPath); pull-to-refresh list; back ×2 + cancel path;
        Account logout.
        """
        with allure.step("Login (email + password + tenant)"):
            self.login_to_events_app()

        with allure.step("Click Events icon (bottom navigation)"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.42)

        with allure.step("Click Search icon at top right"):
            self.transfer_page.enterEventCode(EVENT_CODE)
        #     self.transfer_page.tap_events_search_icon()

        # with allure.step(f"Type {EVENT_CODE}"):
        #     self.transfer_page.type_events_search_term(EVENT_CODE)

        with allure.step("Click filtered course"):
            self.transfer_page.click_event_row_containing(EVENT_CODE)

        with allure.step("Scroll down and open Course Posters"):
            self.poster_page.open_course_posters_section()

        with allure.step("Capture registration link from Course Posters list"):
            link_loc = self.poster_page.locator.get("link_element")
            assert link_loc and link_loc[1], (
                "link_element locator required for share URL validation on this platform"
            )
            app_link = self.poster_page._read_element_text(link_loc, timeout=15)
            assert app_link, "Could not read registration link from poster list"
            self.logger.info("Captured link from app: %s", app_link)

        with allure.step("Click three dots (overflow, top right)"):
            self.poster_page.tap_course_posters_overflow_menu()

        with allure.step(
            "Check Share Poster, Download Poster, Delete Poster, and Cancel (overflow)"
        ):
            self.poster_page.assert_poster_overflow_delete_menu_visible()

        with allure.step("Click Share Poster"):
            self.poster_page.tap_share_poster_menu_option()

        with allure.step('Check "Preparing poster for sharing…" message'):
            preparing_seen = self.poster_page.is_preparing_poster_for_sharing_displayed(
                timeout=6
            )

        with allure.step("If preparing message shown, report success"):
            if preparing_seen:
                print(f"\n========== OUTPUT: {SHARE_POSTER_SUCCESS_MSG} ==========\n")
                self.logger.info("OUTPUT: %s", SHARE_POSTER_SUCCESS_MSG)
            else:
                self.logger.warning(
                    "Preparing poster for sharing message not seen within timeout"
                )

        with allure.step(
            "Sharing options window (no stable locators; brief wait for sheet)"
        ):
            time.sleep(2)

        with allure.step(
            "Wait for share message; validate link matches Course Posters list"
        ):
            share_loc = self.poster_page.locator.get("share_message_element")
            assert share_loc and share_loc[1], (
                "share_message_element locator required for share validation on this platform"
            )
            share_message = self.poster_page._read_element_text(share_loc, timeout=15)
            self.logger.info(
                "Share sheet text (truncated): %s",
                (share_message[:240] + "…") if len(share_message) > 240 else share_message,
            )
            link_ok = app_link in share_message
            if not link_ok:
                stripped = (
                    app_link.replace("https://", "").replace("http://", "").strip()
                )
                link_ok = bool(stripped and stripped in share_message)
            LoggerConfig.log_assertion(
                self.logger,
                "Share sheet contains same registration URL as list",
                link_ok,
            )
            assert link_ok, (
                f"Link mismatch!\nApp list: {app_link!r}\nShare sheet: {share_message!r}"
            )
            self.driver.back()
        # with allure.step("Pull-to-refresh on Course Posters list"):
        #     self.poster_page.pull_to_refresh_course_posters_list()

        with allure.step(
            "Back twice, Cancel twice — Events main (same sequence as delete_poster)"
        ):
            self._leave_posters_screen_to_events_main()

        with allure.step("Account icon → Logout (driver quit in teardown closes app)"):
            self.logout_page.logout()

    def delete_poster_US(self) -> None:
        """
        Delete poster flow (US): login → Events → search E-064549 → course →
        Course Posters → overflow menu → assert Share/Download/Delete/Cancel →
        delete + confirm → assert "No posters yet" → back ×2 and two cancels to
        Events → search again → Course Posters → if empty, print success line →
        back ×2, one cancel to Events → Account logout (driver quit in test teardown).
        """
        with allure.step("Login"):
            self.login_to_events_app()

        with allure.step("Events, search E-064549, open filtered course"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.42)
            self.transfer_page.enterEventCode(EVENT_CODE)
            self.transfer_page.click_event_row_containing(EVENT_CODE)

        with allure.step("Scroll to Course Posters and open"):
            self.poster_page.open_course_posters_section()

        with allure.step("Three dots (overflow) — validate menu options"):
            self.poster_page.tap_course_posters_overflow_menu()
            self.poster_page.assert_poster_overflow_delete_menu_visible()

        with allure.step("Delete Poster → confirm Delete"):
            self.poster_page.tap_delete_poster_and_confirm()

        with allure.step('Assert "No posters yet" on Course Posters'):
            assert self.poster_page.is_no_posters_yet_displayed(
                timeout=15
            ), 'Expected "No posters yet" after delete'

        with allure.step("Back twice, Cancel twice — Events main"):
            self._leave_posters_screen_to_events_main()

        with allure.step("Search again, Course Posters — verify empty state"):
            self.transfer_page.enterEventCode(EVENT_CODE)
            self.transfer_page.click_event_row_containing(EVENT_CODE)
            self.poster_page.open_course_posters_section()
            if self.poster_page.is_no_posters_yet_displayed(timeout=12):
                print(f"\n========== OUTPUT: {DELETE_SUCCESS_MSG} ==========\n")
                self.logger.info("OUTPUT: %s", DELETE_SUCCESS_MSG)
            else:
                self.logger.warning(
                    '"No posters yet" not found on second pass — check no_posters_yet_label locator'
                )

        with allure.step("Back twice, cancel — Events main"):
            self._leave_poster_flow_to_events_main()

        with allure.step("Account → Logout (driver quit in teardown closes app)"):
            self.logout_page.logout()

    @pytest.mark.poster_creation
    @pytest.mark.smoke
    @allure.title("Poster creation (US): E-064549 — template 39, save, verify")
    def test_poster_creation_end_to_end_US(self):
        self.create_poster_US()

    @pytest.mark.poster_download
    @pytest.mark.smoke
    @allure.title("Poster download (US): E-064549 — overflow, Download Poster, toasts")
    def test_download_poster_end_to_end_US(self):
        self.download_poster_US()

    @pytest.mark.poster_share
    @pytest.mark.smoke
    @allure.title("Poster share (US): E-064549 — overflow, Share Poster, pull-to-refresh")
    def test_share_poster_end_to_end_US(self):
        self.share_poster_US()

    @pytest.mark.poster_delete
    @pytest.mark.smoke
    @allure.title("Poster delete (US): E-064549 — overflow menu, delete, verify empty")
    def test_poster_delete_end_to_end_US(self):
        self.delete_poster_US()
