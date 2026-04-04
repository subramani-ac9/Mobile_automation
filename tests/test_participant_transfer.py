"""
End-to-end participant transfer on My Events

- Launch app (fixture), login (geetha@abovecloud9.ai / Admin@ac9 or env vars).
- Events → search E-064549 → open course → Participants → Hari Krishnan.
- Transfer & Notes → Transfer → Confirm → reason → top Transfer.
- Eligible list → filter Teachers → Any One Event Teacher → Show Results.
- Long-press until E-064550 → open → top Transfer → Transfer Initiated (output) → OK.
- Back twice → Events search close → Events main.
- Search E-064550 → open → Participants → verify Hari Krishnan → output success message.
- Back twice → Events search close again → Account → Logout; teardown closes the app.

Run: pytest tests/test_participant_transfer.py -m participant_transfer -s
"""
import os
import time
import pytest
import allure

from pages.login_page import LoginPage
from pages.onboard_page import OnBoardPage
from pages.my_events_page import MyEventsPage
from pages.logout_page import LogoutPage
from pages.participant_transfer_page import ParticipantTransferPage
from utils.navigator import Navigator
from utils.driver_manager import DriverManager
from config.config import TestConfig
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig

LOGIN_TENANT = "US"

LOGIN_EMAIL = os.getenv("TRANSFER_TEST_EMAIL", "geetha@abovecloud9.ai")
LOGIN_PASSWORD = os.getenv("TRANSFER_TEST_PASSWORD", "Admin@ac9")

SOURCE_EVENT_CODE = "E-064550"
TARGET_EVENT_CODE = "E-064549" 
PARTICIPANT_NAME = "Hari Krishnan"
TRANSFER_MESSAGE = "Due to fewer participants"


class TestParticipantTransfer:
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

    @pytest.mark.participant_transfer
    @pytest.mark.smoke
    @allure.title("Participant transfer: E-064549 → E-064550")
    def test_participant_transfer_end_to_end(self):
        with allure.step("Login"):
            self.login_to_events_app()

        with allure.step("Events, search source course E-064549, open"):
            self.my_events_page.navigate_to_events()
            time.sleep(1)
            # self.transfer_page.open_events_search_and_type(SOURCE_EVENT_CODE)
            self.transfer_page.enterEventCode(self.transfer_page.locator["search_button"], self.transfer_page.locator["events_search_field"], SOURCE_EVENT_CODE)
            self.transfer_page.click_event_row_containing(SOURCE_EVENT_CODE)

        with allure.step(
            "Participants, participant, Transfer & Notes, Transfer, Confirm, reason, top Transfer"
        ):
            # self.transfer_page.open_participants_section()
            self.transfer_page.scroll_to_element(self.transfer_page.locator["course_detail_scroll"], self.transfer_page.locator["participants_section"])
            self.transfer_page.click_element(self.transfer_page.locator["participants_section"])
            self.transfer_page.open_participant_by_name(PARTICIPANT_NAME)
            assert self.transfer_page.transfer_and_notes_visible(
                timeout=15
            ), "Transfer and Notes should be visible"
            self.transfer_page.tap_transfer_on_participant_detail()
            self.transfer_page.tap_confirm()
            self.transfer_page.enter_transfer_reason(TRANSFER_MESSAGE)
            self.transfer_page.tap_transfer_top_right()

        with allure.step("Eligible list: Teachers filter, Any One Event, Show Results"):
            self.transfer_page.apply_eligible_programs_teacher_filter()

        with allure.step(
            "Long-press to E-064550, open, Transfer, Transfer Initiated, OK"
        ):
            self.transfer_page.long_press_until_target_program(TARGET_EVENT_CODE)
            time.sleep(1)
            self.transfer_page.tap_transfer_top_right_after_eligible_selection()
            self.transfer_page.assert_transfer_initiated_and_ok()

        with allure.step("Back twice, close Events search, Events main"):
            self.transfer_page.back_twice_then_close_events_search()

        with allure.step("Search E-064550, course, Participants, verify transfer"):
            self.transfer_page.enterEventCode(self.transfer_page.locator["search_button"], self.transfer_page.locator["events_search_field"], TARGET_EVENT_CODE)
            # self.transfer_page.open_events_search_and_type(TARGET_EVENT_CODE)
            self.transfer_page.click_event_row_containing(TARGET_EVENT_CODE)
            self.transfer_page.open_participants_section()
            self.transfer_page.scroll_to_element(self.transfer_page.locator["course_detail_scroll"], self.transfer_page.locator["participants_section"])
            self.transfer_page.click_element(self.transfer_page.locator["participants_section"])
            assert self.transfer_page.is_participant_visible(
                PARTICIPANT_NAME
            ), f"Participant {PARTICIPANT_NAME} should appear under {TARGET_EVENT_CODE}"
            print("\n========== OUTPUT: Participant Transfer Successful ==========\n")
            self.logger.info("OUTPUT: Participant Transfer Successful")

        with allure.step("Back twice, close Events search, Account, Logout"):
            self.transfer_page.back_twice_then_close_events_search()
            self.logout_page.logout()
