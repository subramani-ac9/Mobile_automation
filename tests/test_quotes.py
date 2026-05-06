import time

import allure
import pytest

from config.config import TestConfig
from pages.login_page import LoginPage
from pages.logout_page import LogoutPage
from pages.my_events_page import MyEventsPage
from pages.onboard_page import OnBoardPage
from pages.quotes_page import QuotesPage
from utils.driver_manager import DriverManager
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig
from utils.navigator import Navigator


def _assert_with_allure(logger, title: str, condition: bool, fail_msg: str) -> None:
    LoggerConfig.log_assertion(logger, title, condition)
    body = f"Assertion: {title}\nStatus: {'PASSED' if condition else 'FAILED'}"
    if not condition:
        body += f"\nExpected: {fail_msg}"
    allure.attach(
        body,
        name=f"[ASSERT] {title[:72]}",
        attachment_type=allure.attachment_type.TEXT,
    )
    assert condition, fail_msg


def _pass_with_allure(logger, title: str, detail: str = "") -> None:
    LoggerConfig.log_assertion(logger, title, True)
    body = f"Assertion: {title}\nStatus: PASSED"
    if detail:
        body += f"\n{detail}"
    allure.attach(
        body,
        name=f"[ASSERT] {title[:72]}",
        attachment_type=allure.attachment_type.TEXT,
    )


class TestQuotesPage:
    @pytest.fixture(autouse=True)
    def setup(self, request):
        test_method_name = request.node.name
        self.logger = LoggerConfig.setup_test_logger(
            self.__class__.__name__, test_method_name
        )

        test_id = None
        for marker in request.node.iter_markers("id"):
            if marker.args:
                test_id = marker.args[0]
                break

        start_time = time.time()
        LoggerConfig.log_test_start(self.logger, test_method_name, test_id)

        try:
            self.driver_manager = DriverManager()
            self.driver = self.driver_manager.start_driver()
            self.login_page = LoginPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.onboard_page = OnBoardPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.my_events_page = MyEventsPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.navigator = Navigator(self.driver, TestConfig.MOBILE_PLATFORM)
            self.logout_page = LogoutPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.quotes_page = QuotesPage(self.driver, TestConfig.MOBILE_PLATFORM)

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
            self.logger.info("Starting test cleanup")
            self.driver_manager.quit_driver()
            self.logger.info("Test cleanup completed")
        except Exception as e:
            self.logger.error(f"Test cleanup failed: {str(e)}")

    @pytest.mark.testcase_id("QT_TC_US_1")
    @pytest.mark.quotes
    @pytest.mark.regression
    @allure.feature("Home — Daily quote")
    @allure.story("US — Quote title, overflow menu, actions, logout")
    def test_quotes_page_validation_US(self):
        """
        Launch app (fixture), log in, validate quote on Home and overflow actions,
        dismiss menu, open Account, log out. 
        """
        email = TestConfig.TEST_EMAIL
        password = TestConfig.TEST_PASSWORD

        with allure.step("App launched — session active"):
            _assert_with_allure(
                self.logger,
                "Appium driver session is active",
                self.driver is not None,
                "Driver should exist after fixture setup",
            )

        with allure.step("Navigate to login"):
            self.navigator.navigate_to_login()

        with allure.step("Assertion: Login screen is displayed"):
            _assert_with_allure(
                self.logger,
                "Login page is displayed",
                self.login_page.is_login_page_displayed(),
                "Login page should be shown before credentials",
            )

        with allure.step("Submit login (US tenant)"):
            status = self.login_page.login(email, password, "US")

        with allure.step("Assertion: Login succeeded"):
            ok_login = "Successful" in status
            _assert_with_allure(
                self.logger,
                "Login completed successfully",
                ok_login,
                f"Login failed; status was: {status}",
            )

        with allure.step("Wait for dashboard"):
            dashboard_ok = self.my_events_page.wait_for_dashboard_to_load(
                timeout=45, tenant="us"
            )

        with allure.step("Assertion: Dashboard / bottom navigation ready"):
            _assert_with_allure(
                self.logger,
                "Dashboard loaded after login (events area + bottom navigation)",
                dashboard_ok,
                "My Events dashboard should be visible after login",
            )

        with allure.step("Open Home tab"):
            self.quotes_page.navigate_to_home()

        with allure.step("Assertion: Quote strip loads within time budget"):
            ready = self.quotes_page.is_quote_section_ready_within(max_seconds=8.0)
            _assert_with_allure(
                self.logger,
                'Quote section ready quickly (title + "Quote More Options")',
                ready,
                "Quote UI should appear within 8s on Home",
            )

        with allure.step("Assertion: Jai Gurudev! title visible"):
            _assert_with_allure(
                self.logger,
                'Accessibility: title "Jai Gurudev!" is visible',
                self.quotes_page.is_jai_gurudev_title_displayed(timeout=10),
                'Title "Jai Gurudev!" should be visible on Home',
            )

        with allure.step("Assertion: Quote More Options (three dots) visible"):
            _assert_with_allure(
                self.logger,
                'Accessibility: "Quote More Options Button" is visible',
                self.quotes_page.is_quote_more_options_displayed(timeout=10),
                "Quote More Options Button should be visible",
            )

        with allure.step("Open quote overflow menu"):
            self.quotes_page.click_quote_more_options()

        with allure.step("Assertion: Edit menu row visible"):
            flags = self.quotes_page.are_quote_menu_actions_displayed()
            _assert_with_allure(
                self.logger,
                "Edit quote menu item is visible",
                flags["edit"],
                "Expected Edit Quote Menu Item",
            )

        with allure.step("Assertion: Share menu row visible"):
            _assert_with_allure(
                self.logger,
                "Share quote menu item is visible",
                flags["share"],
                "Expected Share Quote Menu Item",
            )

        with allure.step("Assertion: Download menu row visible"):
            _assert_with_allure(
                self.logger,
                "Download quote menu item is visible",
                flags["download"],
                "Expected Download Quote Menu Item",
            )

        with allure.step("Tap outside to close quote menu"):
            self.quotes_page.dismiss_quote_menu_by_tapping_outside()

        with allure.step("Assertion: Quote controls still on Home"):
            _assert_with_allure(
                self.logger,
                "Quote More Options still available after closing menu",
                self.quotes_page.is_quote_more_options_displayed(timeout=10),
                "Home quote strip should remain usable",
            )

        with allure.step("Open Account"):
            self.logout_page.click_account_icon()

        with allure.step("Assertion: Logout screen / account actions visible"):
            _assert_with_allure(
                self.logger,
                "Logout tile / account screen is displayed",
                self.logout_page.is_logout_page_displayed(),
                "Logout page should open after Account icon",
            )

        with allure.step("Logout and confirm"):
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()

        with allure.step("Logout completed — user signed out; app closes when driver quits"):
            _pass_with_allure(
                self.logger,
                "Logout (and confirm when shown) finished; teardown ends the session and closes the app",
                "No check on post-logout screen — only that logout flow was executed.",
            )

    @pytest.mark.testcase_id("QT_TC_US_2")
    @pytest.mark.quotes
    @pytest.mark.regression
    @allure.feature("Home — Daily quote")
    @allure.story("US — Repeat quote share without errors")
    def test_share_quotes_US(self):
        """
        Launch, log in (US), open Home, repeat share flow several times,
        then Account → Logout.
        """
        email = TestConfig.TEST_EMAIL
        password = TestConfig.TEST_PASSWORD

        with allure.step("Assertion: Driver session active"):
            _assert_with_allure(
                self.logger,
                "Appium driver session is active",
                self.driver is not None,
                "Driver should exist after fixture setup",
            )

        with allure.step("Navigate to login"):
            self.navigator.navigate_to_login()

        with allure.step("Assertion: Login screen"):
            _assert_with_allure(
                self.logger,
                "Login page is displayed",
                self.login_page.is_login_page_displayed(),
                "Login page should be shown",
            )

        with allure.step("Login (US)"):
            status = self.login_page.login(email, password, "US")

        with allure.step("Assertion: Login success"):
            _assert_with_allure(
                self.logger,
                "Login completed successfully",
                "Successful" in status,
                f"Login failed; status: {status}",
            )

        with allure.step("Wait for dashboard"):
            dash = self.my_events_page.wait_for_dashboard_to_load(
                timeout=45, tenant="us"
            )

        with allure.step("Assertion: Dashboard ready"):
            _assert_with_allure(
                self.logger,
                "Dashboard loaded after login",
                dash,
                "Dashboard should be ready before Home",
            )

        with allure.step("Go to Home"):
            self.quotes_page.navigate_to_home()

        with allure.step("Assertion: Quote strip ready"):
            _assert_with_allure(
                self.logger,
                "Quote section visible within budget on Home",
                self.quotes_page.is_quote_section_ready_within(max_seconds=10.0),
                "Quote title + More Options should appear within 10s",
            )

        iterations = 5
        for i in range(1, iterations + 1):
            tag = f"Share attempt {i} of {iterations}"

            with allure.step(f"{tag}: Assertion — More options present"):
                _assert_with_allure(
                    self.logger,
                    f"{tag}: Quote More Options available before share",
                    self.quotes_page.is_quote_more_options_displayed(timeout=12),
                    "Quote More Options Button should be visible",
                )

            with allure.step(f"{tag}: Tap Quote More Options"):
                self.quotes_page.click_quote_more_options()

            with allure.step(f"{tag}: Assertion — Share row visible"):
                flags = self.quotes_page.are_quote_menu_actions_displayed()
                _assert_with_allure(
                    self.logger,
                    f"{tag}: Share Quote Menu Item is visible",
                    flags["share"],
                    "Share row should appear in overflow menu",
                )

            with allure.step(f"{tag}: Tap Share"):
                self.quotes_page.click_share_quote_menu_item()

            with allure.step(f"{tag}: Optional preparing toast (may skip on repeat share)"):
                saw_preparing = (
                    self.quotes_page.wait_for_preparing_quote_message_optional(
                        timeout=8.0
                    )
                )

            with allure.step(f"{tag}: Assertion — Preparing toast"):
                if saw_preparing:
                    _pass_with_allure(
                        self.logger,
                        f'{tag}: "Preparing quote for sharing..." was shown',
                    )
                else:
                    _pass_with_allure(
                        self.logger,
                        f"{tag}: Preparing toast not shown — continuing "
                        "(cached asset / repeat share)",
                        "Proceed to share sheet dismissal.",
                    )

            with allure.step(f"{tag}: Wait for preparing overlay to finish (if shown)"):
                self.quotes_page.wait_for_preparing_quote_message_gone(timeout=22.0)

            with allure.step(f"{tag}: Assertion — No preparing overlay before closing share"):
                _assert_with_allure(
                    self.logger,
                    f"{tag}: Preparing message no longer shown (share phase)",
                    not self.quotes_page.is_preparing_quote_message_displayed(timeout=1),
                    "Preparing overlay should not block closing the share window",
                )

            with allure.step(f"{tag}: Pause for OS share presentation"):
                # Without toast, the system sheet may need slightly longer to appear.
                self.quotes_page.wait_for_share_sheet_animation(
                    1.2 if not saw_preparing else 0.7
                )

            with allure.step(
                f"{tag}: Close share window — tap anywhere on screen, then fallbacks"
            ):
                self.quotes_page.dismiss_system_share_sheet()

            with allure.step(f"{tag}: Close any leftover quote overflow menu"):
                self.quotes_page.dismiss_quote_menu_by_tapping_outside()

            with allure.step(f"{tag}: Assertion — Home quote ready for next share"):
                _assert_with_allure(
                    self.logger,
                    f"{tag}: Quote More Options still available (no error state)",
                    self.quotes_page.is_quote_more_options_displayed(timeout=12),
                    "Repeated share should leave Home quote usable",
                )

        with allure.step("Open Account"):
            self.logout_page.click_account_icon()

        with allure.step("Assertion: Logout / account screen"):
            _assert_with_allure(
                self.logger,
                "Account screen shows logout",
                self.logout_page.is_logout_page_displayed(),
                "Logout page should display",
            )

        with allure.step("Logout"):
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()

        with allure.step("Logout completed — session ends when driver quits in teardown"):
            _pass_with_allure(
                self.logger,
                "Logout (and confirm when shown) finished; app/session cleanup runs in fixture",
                "No assertion on post-logout screen — requirement is logout then close app.",
            )

    @pytest.mark.testcase_id("QT_TC_US_3")
    @pytest.mark.quotes
    @pytest.mark.regression
    @allure.feature("Home — Daily quote")
    @allure.story("US — Repeat quote download toasts")
    def test_download_quotes_US(self):
        """
        Launch, log in (US), open Home, repeat quote download flow (more options →
        Download → downloading toast → wait 2s → saved-to-gallery message → wait 2s)
        five times, then Account → Logout.
        """
        email = TestConfig.TEST_EMAIL
        password = TestConfig.TEST_PASSWORD

        with allure.step("Assertion: Driver session active"):
            _assert_with_allure(
                self.logger,
                "Appium driver session is active",
                self.driver is not None,
                "Driver should exist after fixture setup",
            )

        with allure.step("Navigate to login"):
            self.navigator.navigate_to_login()

        with allure.step("Assertion: Login screen"):
            _assert_with_allure(
                self.logger,
                "Login page is displayed",
                self.login_page.is_login_page_displayed(),
                "Login page should be shown",
            )

        with allure.step("Login (US)"):
            status = self.login_page.login(email, password, "US")

        with allure.step("Assertion: Login success"):
            _assert_with_allure(
                self.logger,
                "Login completed successfully",
                "Successful" in status,
                f"Login failed; status: {status}",
            )

        with allure.step("Wait for dashboard"):
            dash = self.my_events_page.wait_for_dashboard_to_load(
                timeout=45, tenant="us"
            )

        with allure.step("Assertion: Dashboard ready"):
            _assert_with_allure(
                self.logger,
                "Dashboard loaded after login",
                dash,
                "Dashboard should be ready before Home",
            )

        with allure.step("Go to Home"):
            self.quotes_page.navigate_to_home()

        with allure.step("Assertion: Quote strip ready"):
            _assert_with_allure(
                self.logger,
                "Quote section visible within budget on Home",
                self.quotes_page.is_quote_section_ready_within(max_seconds=10.0),
                "Quote title + More Options should appear within 10s",
            )

        iterations = 5
        for i in range(1, iterations + 1):
            tag = f"Download attempt {i} of {iterations}"

            with allure.step(f"{tag}: Assertion — Quote More Options present"):
                _assert_with_allure(
                    self.logger,
                    f"{tag}: Quote More Options available",
                    self.quotes_page.is_quote_more_options_displayed(timeout=12),
                    "Quote More Options Button should be visible",
                )

            with allure.step(f"{tag}: Tap Quote More Options"):
                self.quotes_page.click_quote_more_options()

            with allure.step(f"{tag}: Assertion — Download row visible"):
                flags = self.quotes_page.are_quote_menu_actions_displayed()
                _assert_with_allure(
                    self.logger,
                    f"{tag}: Download Quote Menu Item is visible",
                    flags["download"],
                    "Download row should appear in overflow menu",
                )

            with allure.step(f"{tag}: Tap Download"):
                self.quotes_page.click_download_quote_menu_item()

            with allure.step(f"{tag}: Optional — Downloading quote… toast"):
                saw_dl = self.quotes_page.wait_for_downloading_quote_message_optional(
                    timeout=8.0
                )
                if saw_dl:
                    _pass_with_allure(
                        self.logger,
                        f'{tag}: "Downloading quote..." was shown',
                        "Accessibility or page source matched.",
                    )
                else:
                    _pass_with_allure(
                        self.logger,
                        f"{tag}: Downloading toast not detected — continuing (repeat / fast path)",
                        "Proceed with fixed waits per spec.",
                    )

            with allure.step(f"{tag}: Wait 2 seconds after download starts"):
                self.quotes_page.wait_seconds(2.0)

            with allure.step(
                f'{tag}: Wait for "Quote saved to your phone. Tap to open gallery."'
            ):
                self.quotes_page.wait_for_quote_saved_to_gallery_message(timeout=28.0)

            with allure.step(f"{tag}: Wait 2 seconds after saved message"):
                self.quotes_page.wait_seconds(2.0)

            with allure.step(f"{tag}: Dismiss quote overflow if still open"):
                self.quotes_page.dismiss_quote_menu_by_tapping_outside()

            with allure.step(f"{tag}: Assertion — Home quote ready for next download"):
                _assert_with_allure(
                    self.logger,
                    f"{tag}: Quote More Options still available",
                    self.quotes_page.is_quote_more_options_displayed(timeout=12),
                    "Repeated download should leave Home quote usable",
                )

        with allure.step("Open Account"):
            self.logout_page.click_account_icon()

        with allure.step("Assertion: Logout / account screen"):
            _assert_with_allure(
                self.logger,
                "Account screen shows logout",
                self.logout_page.is_logout_page_displayed(),
                "Logout page should display",
            )

        with allure.step("Logout"):
            self.logout_page.click_logout_button()
            if self.logout_page.is_confirm_logout_button_displayed():
                self.logout_page.click_confirm_logout_button()

        with allure.step("Logout completed — session ends when driver quits in teardown"):
            _pass_with_allure(
                self.logger,
                "Logout finished; driver quit in fixture closes the app",
                "",
            )
