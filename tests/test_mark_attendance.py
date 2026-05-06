
import os
import time

import allure
import pytest

from config.config import TestConfig
from pages.login_page import LoginPage
from pages.logout_page import LogoutPage
from pages.mark_attendance_page import MarkAttendancePage
from pages.my_events_page import MyEventsPage
from pages.onboard_page import OnBoardPage
from pages.participant_transfer_page import ParticipantTransferPage
from utils.driver_manager import DriverManager
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig
from utils.navigator import Navigator

LOGIN_TENANT = "US"
LOGIN_EMAIL = os.getenv("MARK_ATTENDANCE_EMAIL", "geetha@abovecloud9.ai")
LOGIN_PASSWORD = os.getenv("MARK_ATTENDANCE_PASSWORD", "Admin@ac9")
EVENT_CODE = os.getenv("MARK_ATTENDANCE_EVENT_CODE", "E-065857")
PARTICIPANT_NAME_SINGLE = os.getenv(
    "MARK_ATTENDANCE_PARTICIPANT_NAME", "Manoj Kumar"
)
PARTICIPANT_SEARCH_PREFIX = os.getenv(
    "MARK_ATTENDANCE_PARTICIPANT_SEARCH_PREFIX", "Manoj"
)
PARTICIPANT_LIST_ROW_A11Y = os.getenv("MARK_ATTENDANCE_ROW_A11Y", "MK\nManoj Kumar")


class TestMarkAttendance:
    @pytest.fixture(autouse=True)
    def setup(self, request):
        test_method_name = request.node.name
        self.logger = LoggerConfig.setup_test_logger(
            self.__class__.__name__, test_method_name
        )
        start_time = time.time()
        LoggerConfig.log_test_start(self.logger, test_method_name, None)

        try:
            self.logger.info("Initializing test setup")
            self.driver_manager = DriverManager()
            self.driver = self.driver_manager.start_driver()
            platform = TestConfig.MOBILE_PLATFORM
            self.login_page = LoginPage(self.driver, platform)
            self.onboard_page = OnBoardPage(self.driver, platform)
            self.my_events_page = MyEventsPage(self.driver, platform)
            self.transfer_page = ParticipantTransferPage(self.driver, platform)
            self.mark_attendance_page = MarkAttendancePage(self.driver, platform)
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

    def login_to_events_app(
        self,
        email: str = LOGIN_EMAIL,
        password: str = LOGIN_PASSWORD,
        tenant: str = LOGIN_TENANT,
    ) -> None:
        self.navigator.navigate_to_login()
        login_page_displayed = self.login_page.is_login_page_displayed()
        LoggerConfig.log_assertion(
            self.logger, "Login page should be displayed", login_page_displayed
        )
        assert login_page_displayed, "Login page should be displayed"
        self.login_page.login(email, password, tenant)
        validations = self.my_events_page.validate_successful_login(tenant)
        for validation in validations:
            validation_result = "not" not in validation.lower()
            LoggerConfig.log_assertion(
                self.logger, f"Validation: {validation}", validation_result
            )
            assert validation_result, f"Validation failed: {validation}"

    def _assert_ui(self, condition: bool, description: str) -> None:
        """Log ASSERTION pass/fail like login and MyEvents validation, then assert."""
        LoggerConfig.log_assertion(self.logger, description, condition)
        assert condition, description

    @pytest.mark.attendance
    @pytest.mark.mark_attendance
    @pytest.mark.smoke
    @allure.title("Mark Attendance page validation (US)")
    def test_mark_attendance_page_US(self):
        """App launch and driver teardown are handled by the test fixture."""
        ma = self.mark_attendance_page

        with allure.step("Login with US tenant (geetha@abovecloud9.ai / Admin@ac9)"):
            self.login_to_events_app(
                "geetha@abovecloud9.ai", "Admin@ac9", LOGIN_TENANT
            )

        with allure.step("Open Events, search for course, open Participants"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.35)
            self.transfer_page.enterEventCode(EVENT_CODE)
            self.transfer_page.click_event_row_containing(EVENT_CODE)
            self.transfer_page.open_participants_section()

        with allure.step("Search Participants icon is present"):
            self._assert_ui(
                ma.is_search_icon_visible(),
                "Search Participants Button is present",
            )

        with allure.step("Participants Filter icon is present"):
            self._assert_ui(
                ma.is_participant_filter_visible(),
                "Participants Filter Button is present",
            )

        with allure.step("Participants More Options Button is present"):
            self._assert_ui(
                ma.is_participants_more_options_button_visible(),
                "Participants More Options Button is present",
            )

        with allure.step("Open More Options and verify menu options"):
            ma.tap_participants_more_options_button()
            self._assert_ui(
                ma.is_more_options_menu_select_visible(),
                "More options: Select is present",
            )
            self._assert_ui(
                ma.is_more_options_menu_scan_qr_visible(),
                "More options: Scan QR is present",
            )
            self._assert_ui(
                ma.is_more_options_mark_all_attended_visible(),
                "More options: Mark all attended is present",
            )
            self._assert_ui(
                ma.is_more_options_mark_all_no_show_visible(),
                "More options: Mark all no-show is present",
            )
            self._assert_ui(
                ma.is_more_options_mark_all_dropout_visible(),
                "More options: Mark all drop-out is present",
            )

        with allure.step('Tap "Participants" to close the More Options menu'):
            ma.tap_participants_title_to_close_more_options()

        with allure.step("Participant name and Attendance status column headers are present"):
            self._assert_ui(
                ma.is_participant_name_header_visible(),
                "Participant name column header is present",
            )
            self._assert_ui(
                ma.is_attendance_column_header_visible(),
                "Attendance status column header is present",
            )

        with allure.step("Attendance Status dropdown is present"):
            self._assert_ui(
                ma.is_attendance_status_dropdown_visible(),
                "Attendance Status dropdown is present",
            )

        with allure.step("Open Attendance Status dropdown and verify options"):
            ma.tap_attendance_status_dropdown()
            self._assert_ui(
                ma.is_dropdown_attended_visible(),
                "Dropdown: Attended is present",
            )
            self._assert_ui(
                ma.is_dropdown_dropout_visible(),
                "Dropdown: Drop-out is present",
            )
            self._assert_ui(
                ma.is_dropdown_no_show_visible(),
                "Dropdown: No-Show is present",
            )

        with allure.step("Tap screen to dismiss the dropdown"):
            ma.tap_screen_center_to_dismiss()

        with allure.step("See Past Participants control is present at the bottom"):
            self._assert_ui(
                ma.scroll_until_see_past_participants_visible(),
                "See Past Participants Button is present",
            )

        with allure.step("Back to course (Back Button)"):
            ma.tap_toolbar_back_button()

        with allure.step("Back to Events search (Back Button)"):
            ma.tap_toolbar_back_button()

        with allure.step("Close Events search"):
            ma.tap_events_search_close()

        with allure.step("Open Account and Logout"):
            self.logout_page.click_account_icon()
            self._assert_ui(
                self.logout_page.is_logout_page_displayed(),
                "Logout screen is present",
            )
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()

    def _assert_participants_filter_sheet_controls(self, ma: MarkAttendancePage) -> None:
        self._assert_ui(
            ma.is_pa_filter_title_filters_visible(),
            "Mark Attendance Filter: Filters is available on the left",
        )
        self._assert_ui(
            ma.is_pa_filter_reset_visible(),
            "Mark Attendance Filter: Reset filters is available on the right",
        )
        self._assert_ui(
            ma.is_pa_filter_attendance_status_section_visible(),
            "Mark Attendance Filter: Attendance status section is available on the left",
        )
        self._assert_ui(
            ma.is_pa_filter_radio_all_visible(),
            "Mark Attendance Filter: All radio is available",
        )
        self._assert_ui(
            ma.is_pa_filter_radio_attended_visible(),
            "Mark Attendance Filter: Attended radio is available",
        )
        self._assert_ui(
            ma.is_pa_filter_radio_no_show_visible(),
            "Mark Attendance Filter: No-Show radio is available",
        )
        self._assert_ui(
            ma.is_pa_filter_radio_dropout_visible(),
            "Mark Attendance Filter: Drop-out radio is available",
        )
        self._assert_ui(
            ma.is_pa_filter_radio_not_set_visible(),
            "Mark Attendance Filter: Not set radio is available",
        )
        self._assert_ui(
            ma.is_pa_filter_show_results_visible(),
            "Mark Attendance Filter: Show Results is available at the bottom",
        )

    @pytest.mark.attendance
    @pytest.mark.mark_attendance_filter
    @allure.title(f"Mark Attendance filter validation (US, {EVENT_CODE})")
    def test_mark_attendance_filter_validation_US(self):
        ma = self.mark_attendance_page
        tr = self.transfer_page

        with allure.step("Login"):
            self.login_to_events_app()

        with allure.step("Events: search course and open Participants"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.35)
            tr.enterEventCode(EVENT_CODE)
            tr.click_event_row_containing(EVENT_CODE)
            tr.open_participants_section()

        with allure.step("Open participants filter"):
            ma.tap_open_participants_filter_sheet()

        with allure.step("Filter sheet: titles, reset, attendance radios, Show Results"):
            self._assert_participants_filter_sheet_controls(ma)

        with allure.step("All filter: select All and Show Results"):
            ma.tap_pa_filter_radio_all()
            ma.tap_pa_filter_show_results()
            self._assert_ui(
                ma.verify_all_filter_shows_attended_dropout_no_show(),
                "Mark Attendance Filter: All — Show Results applied (Participants of all status Displayed)",
            )

        with allure.step("Attended filter: Show Results"):
            ma.tap_open_participants_filter_sheet()
            ma.tap_pa_filter_radio_attended()
            ma.tap_pa_filter_show_results()
            self._assert_ui(
                ma.verify_list_shows_only_status("attended"),
                "Mark Attendance Filter: Attended — Show Results applied (Participants with Attended status displayed)",
            )

        with allure.step("No-Show filter: Show Results"):
            ma.tap_open_participants_filter_sheet()
            ma.tap_pa_filter_radio_no_show()
            ma.tap_pa_filter_show_results()
            self._assert_ui(
                ma.verify_list_shows_only_status("no_show"),
                "Mark Attendance Filter: No-Show — Show Results applied (Participants with No-Show status displayed)",
            )

        with allure.step("Drop-out filter: Show Results"):
            ma.tap_open_participants_filter_sheet()
            ma.tap_pa_filter_radio_dropout()
            ma.tap_pa_filter_show_results()
            self._assert_ui(
                ma.verify_list_shows_only_status("dropout"),
                "Mark Attendance Filter: Drop-out — Show Results applied (Participants with Drop-out status displayed)",
            )

        with allure.step("Not set filter: Show Results"):
            ma.tap_open_participants_filter_sheet()
            ma.tap_pa_filter_radio_not_set()
            ma.tap_pa_filter_show_results()
            self._assert_ui(
                ma.verify_list_shows_only_status("not_set"),
                "Mark Attendance Filter: Not set — Show Results applied (Participants whose Attendance are not marked are displayed)",
            )

        with allure.step("Navigate back"):
            ma.tap_toolbar_back_button()

        with allure.step("Back"):
            ma.tap_toolbar_back_button()

        with allure.step("Close Events search"):
            ma.tap_events_search_close()

        with allure.step("Logout"):
            self.logout_page.logout()

    @pytest.mark.attendance
    @pytest.mark.mark_attendance_single
    @allure.title(
        f"Mark Attendance single participant (US, {PARTICIPANT_NAME_SINGLE} / {EVENT_CODE})"
    )
    def test_mark_attendance_single_participant_US(self):
        ma = self.mark_attendance_page
        tr = self.transfer_page
        search_term = PARTICIPANT_SEARCH_PREFIX
        participant = PARTICIPANT_NAME_SINGLE
        row_a11y = PARTICIPANT_LIST_ROW_A11Y
        with allure.step("Login (geetha@abovecloud9.ai / Admin@ac9, US)"):
            self.login_to_events_app(
                "geetha@abovecloud9.ai", "Admin@ac9", LOGIN_TENANT
            )

        with allure.step("Open Events, search, open course, Participants"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.35)
            tr.enterEventCode(EVENT_CODE)
            tr.click_event_row_containing(EVENT_CODE)
            tr.open_participants_section()

        with allure.step("Search Participants icon is visible"):
            self._assert_ui(
                ma.is_search_icon_visible(),
                "Search Participants Button is present",
            )

        with allure.step('Tap Search Participants and type "Manoj"'):
            ma.tap_participants_search_icon()
            ma.type_participants_search_term(search_term)
            print("participant search term typed")

        with allure.step(f'Participant row "{row_a11y}" is displayed'):
            self._assert_ui(
                ma.is_row_access_id_in_dom(row_a11y, timeout=10),
                f'Participant row "{row_a11y}" is present',
            )
            print("participant row displayed")

        with allure.step(
            "Attendance Status Dropdown Expandable Dropdown for participant row"
        ):
            ma.tap_attendance_status_expandable_dropdown_for_row_cell_a11y(row_a11y)

        with allure.step("Brief wait before selecting Attended"):
            ma.wait_after_attendance_dropdown_open(1.0)

        with allure.step("Tap Attended (Accessibility ID: Attended)"):
            ma.tap_dropdown_attended_option()

        with allure.step("Cancel"):
            ma.tap_cancel()
        print("cancel tapped")

        with allure.step("Back (top-left)"):
            ma.tap_toolbar_back_button()
        print("back tapped")

        with allure.step("Back (top-left)"):
            ma.tap_toolbar_back_button()
        print("back tapped")

        with allure.step("Close Events search (top right, Events Search Close Button)"):
            ma.tap_events_search_close()

        with allure.step("Open Account and Logout"):
            self.logout_page.click_account_icon()

        with allure.step("Logout and close app in teardown"):
            self._assert_ui(
                self.logout_page.is_logout_page_displayed(),
                "Logout page should be displayed",
            )
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()

    @pytest.mark.attendance
    @pytest.mark.mark_attendance_single
    @pytest.mark.mark_attendance_single_revert
    @allure.title(
        f"Mark Attendance revert single participant — Drop-out "
        f"(US, {PARTICIPANT_NAME_SINGLE} / {EVENT_CODE})"
    )
    def test_mark_attendance_revert_single_participant_US(self):
        """
        Login → Events → search course → Participants → search participant → row cell
        → Attendance Status Dropdown Expandable Dropdown → Drop-out → Cancel → back ×2
        → Events search cancel → Account → Logout 
        """
        ma = self.mark_attendance_page
        tr = self.transfer_page
        search_term = PARTICIPANT_SEARCH_PREFIX
        row_a11y = PARTICIPANT_LIST_ROW_A11Y

        with allure.step("Login (geetha@abovecloud9.ai / Admin@ac9, US)"):
            self.login_to_events_app(
                "geetha@abovecloud9.ai", "Admin@ac9", LOGIN_TENANT
            )

        with allure.step("Open Events, search, open course, Participants"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.2)
            tr.enterEventCode(EVENT_CODE)
            tr.click_event_row_containing(EVENT_CODE)
            tr.open_participants_section()

        with allure.step("Search Participants Button is visible"):
            self._assert_ui(
                ma.is_search_icon_visible(),
                "Search Participants Button is present",
            )

        with allure.step('Tap Search Participants and type participant search term'):
            ma.tap_participants_search_icon()
            ma.type_participants_search_term(search_term)

        with allure.step(f'Participant row "{row_a11y}" is displayed'):
            self._assert_ui(
                ma.is_row_access_id_in_dom(row_a11y, timeout=10),
                f'Participant row "{row_a11y}" is present',
            )

        with allure.step(
            "Attendance Status Dropdown Expandable Dropdown "
        ):
            ma.tap_attendance_status_expandable_dropdown_for_row_cell_a11y(row_a11y)

        with allure.step("Tap Drop-out"):
            ma.tap_dropdown_dropout_option()

        with allure.step("Cancel"):
            ma.tap_cancel()

        with allure.step("Back (top-left)"):
            ma.tap_toolbar_back_button()

        with allure.step("Back (top-left)"):
            ma.tap_toolbar_back_button()

        with allure.step("Cancel on top right (Events search close)"):
            ma.tap_events_search_close()

        with allure.step("Accounts icon and Logout"):
            self.logout_page.click_account_icon()

        with allure.step("Logout; app closed in teardown"):
            self._assert_ui(
                self.logout_page.is_logout_page_displayed(),
                "Logout page should be displayed",
            )
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()

    @pytest.mark.attendance
    @pytest.mark.mark_attendance_bulk
    @allure.title(
        f"Mark Attendance bulk: More Options → Mark all attended (US, {EVENT_CODE})"
    )
    def test_mark_attendance_bulk_attendance_marking_US(self):
        """ 
        Login → Events → search course → Participants → More Options → Mark all attended
        → back (chevron) → back (Back Button) → close Events search → Account → Logout.
        App launch and driver quit are handled by the test fixture.
        """
        ma = self.mark_attendance_page
        tr = self.transfer_page

        with allure.step("Login (geetha@abovecloud9.ai / Admin@ac9, US)"):
            self.login_to_events_app(
                email="geetha@abovecloud9.ai",
                password="Admin@ac9",
                tenant="US",
            )

        with allure.step("Open Events, search, open course, Participants"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.35)
            tr.enterEventCode(EVENT_CODE)
            tr.click_event_row_containing(EVENT_CODE)
            tr.open_participants_section()

        with allure.step(
            "Participants More Options, then Mark all attended"
        ):
            self._assert_ui(
                ma.is_participants_more_options_button_visible(),
                "Participants More Options Button is visible",
            )
            ma.tap_participants_more_options_button()
            self._assert_ui(
                ma.is_more_options_mark_all_attended_visible(),
                "Mark all attended is present in the menu",
            )
            ma.tap_more_options_mark_all_attended()

        with allure.step("Back (top-left, first navigation)"):
            ma.tap_toolbar_back_button()

        with allure.step("Back (top-left, Accessibility ID: Back Button)"):
            ma.tap_toolbar_back_button()

        with allure.step("Close Events search (Accessibility ID: Events Search Close Button)"):
            ma.tap_events_search_close()

        with allure.step("Open Account and Logout"):
            self.logout_page.click_account_icon()

        with allure.step("Confirm logout; app closed in test teardown"):
            assert self.logout_page.is_logout_page_displayed(), (
                "Logout page should be displayed"
            )
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()
            self.logout_page.validate_logout()

    @pytest.mark.attendance
    @pytest.mark.mark_attendance_bulk_revert
    @allure.title(
        f"Mark Attendance bulk: More Options → Mark all drop-out (US, {EVENT_CODE})"
    )
    def test_revert_bulk_mark_attendance_US(self):
        """
        Same navigation as test_mark_attendance_bulk_attendance_marking_US, but
        Participants More Options → "Mark all drop-out" (Accessibility ID) instead
        of Mark all attended. Then: back (chevron) → back (Back Button) → close
        Events search → Account → Logout.
        """
        ma = self.mark_attendance_page
        tr = self.transfer_page

        with allure.step("Login (geetha@abovecloud9.ai / Admin@ac9, US)"):
            self.login_to_events_app(
                email="geetha@abovecloud9.ai",
                password="Admin@ac9",
                tenant="US",
            )

        with allure.step("Open Events, search, open course, Participants"):
            self.my_events_page.navigate_to_events()
            time.sleep(0.35)
            tr.enterEventCode(EVENT_CODE)
            tr.click_event_row_containing(EVENT_CODE)
            tr.open_participants_section()

        with allure.step("Participants More Options, then Mark all drop-out"):
            self._assert_ui(
                ma.is_participants_more_options_button_visible(),
                "Participants More Options Button is visible",
            )
            ma.tap_participants_more_options_button()
            self._assert_ui(
                ma.is_more_options_mark_all_dropout_visible(),
                "Mark all drop-out is present in the menu",
            )
            ma.tap_more_options_mark_all_dropout()

        with allure.step("Back (top-left, first navigation)"):
            ma.tap_toolbar_back_button()

        with allure.step("Back (top-left, Accessibility ID: Back Button)"):
            ma.tap_toolbar_back_button()

        with allure.step("Close Events search (Accessibility ID: Events Search Close Button)"):
            ma.tap_events_search_close()

        with allure.step("Open Account and Logout"):
            self.logout_page.click_account_icon()

        with allure.step("Confirm logout; app closed in test teardown"):
            assert self.logout_page.is_logout_page_displayed(), (
                "Logout page should be displayed"
            )
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()
            self.logout_page.validate_logout()
