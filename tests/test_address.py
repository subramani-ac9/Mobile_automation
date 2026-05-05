import json
import os
import time, random, string, pytest, re, logging
import pandas as pd
from datetime import datetime, timedelta
from constants.locator.myevent_locator import MyEventLocator
from constants.message.address_message import AddressMessage
from pages import address_page
from pages.course_create_page import CourseCreatePage
from utils.driver_manager import DriverManager
from utils.googleSheet_helper import read_google_sheet
from utils.time_zone_util import TimezoneFormatter
from config.config import TestConfig
from utils.helpers import read_csv_as_dict
from pages.login_page import LoginPage
from pages.my_events_page import MyEventsPage
from pages.onboard_page import OnBoardPage
from pages.meetup_create_page import MeetupCreatePage
from utils.helpers import take_screenshot, read_csv_as_dict, read_input_data, write_output_data, write_csv_from_dicts
from utils.navigator import Navigator
from constants.message.meetup_create_message import MeetupCreateMsg
from utils.logger_config import LoggerConfig
from pages.address_page import AddressPage

import allure

def _load_address_rows():
    # rows = read_csv_as_dict("data/filter_run1.csv")
    rows = read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "Address")
    print(f"Address data: {rows}")
    return [r for r in rows if r.get("Testcase_ID", "").strip()]


ADDRESS_ROWS = _load_address_rows()


def _row_id(row):
    return row.get("Testcase_ID", "unknown")


def _rows_prefix(prefix: str):
    return [r for r in ADDRESS_ROWS if r.get("Testcase_ID", "").startswith(prefix)]



_DEFAULT_ADDRESS_UPDATE_ROW = {
    "existingAddressName": "Asdf",
    "addressName": "Hello",
    "address": "456 Oak",
    "city": "Little Rocks",
    "zipcode": "72002",
    "state": "Arizona (AZ)",
    "tenant": "us",
}
_DEFAULT_ADDRESS_CANCEL_ROW = {
    "originalAddressName": "Test01278",
    "draftAddressName": "DraftCancelDoNotSave999",
    "tenant": "us",
}


class TestAddress:
    # address_data = read_csv_as_dict('data/address.csv')
    address_data = read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "Address")
    print(f"Address data: {address_data}")

    _raw_address_update = read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "AddressUpdate")
    address_update_data = _raw_address_update if _raw_address_update else [_DEFAULT_ADDRESS_UPDATE_ROW.copy()]
    _raw_address_cancel = read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "AddressCancel")
    address_cancel_data = _raw_address_cancel if _raw_address_cancel else [_DEFAULT_ADDRESS_CANCEL_ROW.copy()]

    @pytest.fixture(autouse=True)
    def setup(self, request):
        """Setup and teardown for each test"""
        # Setup test-specific logger
        test_method_name = request.node.name
        self.logger = LoggerConfig.setup_test_logger(self.__class__.__name__, test_method_name)
        
        # Get test ID from markers
        test_id = None
        for marker in request.node.iter_markers('id'):
            if marker.args:
                test_id = marker.args[0]
                break
        
        # Log test start
        start_time = time.time()
        LoggerConfig.log_test_start(self.logger, test_method_name, test_id)
        
        try:
            self.driver_manager = DriverManager()
            self.driver = self.driver_manager.start_driver()
            self.login_page = LoginPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.onboard_page = OnBoardPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.my_events_page = MyEventsPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.course_create = CourseCreatePage(self.driver, platform=TestConfig.MOBILE_PLATFORM)
            self.address_page = AddressPage(self.driver, platform=TestConfig.MOBILE_PLATFORM)
            self.nav = Navigator(self.driver, TestConfig.MOBILE_PLATFORM)
            self.address_message = AddressMessage.get_message()
            
            request.node.driver = self.driver  # for Allure screenshot-on-failure hook
            self.logger.info("Test setup completed successfully")
            yield
            
        except Exception as e:
            self.logger.error(f"Test setup failed: {str(e)}")
            raise
        finally:
            # Log test completion
            end_time = time.time()
            duration = end_time - start_time
            status = "COMPLETED"
            
            rep_call = getattr(request.node, "rep_call", None)
            if rep_call is not None and rep_call.failed:
                take_screenshot(self.driver, f"test_failed_{self.__class__.__name__}")
                status = "FAILED"
            
            LoggerConfig.log_test_end(self.logger, test_method_name, duration, status)
            
            # Cleanup
            if hasattr(self, 'driver_manager'):
                self.driver_manager.quit_driver()
                self.logger.info("Driver cleanup completed")

    @pytest.mark.data_driven
    @pytest.mark.address
    @pytest.mark.parametrize("row", _rows_prefix("AD_CREATE"), ids=_row_id)
    def test_create_address_with_given_data(self, row):
        with allure.step("navigate to address page"):   
            self.nav.navigate_to_address_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, row.get("tenant"))
            self.address_page.click_create_address_button()
        with allure.step("fill address form and validate result"):
            success, outcome_msg = self.address_page.handle_address(row)
            assert success, outcome_msg
        address_name = row.get("addressName")
        if address_name:
            with allure.step("verify created address is visible in the list"):
                assert self.address_page.is_address_visible(address_name), (
                    f"Address '{address_name}' should be visible after create"
                )


    @pytest.mark.data_driven
    @pytest.mark.address
    @pytest.mark.parametrize("row", _rows_prefix("AD_UPDATE"), ids=_row_id)
    def test_update_address_with_given_data(self, row):
        existing = row.get("existingAddressName")
        assert existing, "AddressUpdate row must include existingAddressName (or use sheet defaults)"
        with allure.step("navigate to address page"):
            self.nav.navigate_to_address_page(
                TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, row.get("tenant")
            )
        with allure.step("edit address: snapshot, partial update from sheet, save, re-open and verify fields"):
            success, outcome_msg, meta = self.address_page.update_address(existing, row)
            self.logger.info(f"Update address message: {outcome_msg ,success,meta}")
            assert success, outcome_msg
            assert meta is not None, "Expected verification meta (before/after snapshots)"
            allure.attach(
                json.dumps(meta.get("before", {}), indent=2),
                name="address_form_before",
                attachment_type=allure.attachment_type.JSON,
            )
            allure.attach(
                json.dumps(meta.get("after", {}), indent=2),
                name="address_form_after",
                attachment_type=allure.attachment_type.JSON,
            )
            allure.attach(
                json.dumps(meta.get("modified_keys", []), indent=2),
                name="modified_field_keys",
                attachment_type=allure.attachment_type.JSON,
            )
        new_name = (
            self.address_page._cell_to_str(row["addressName"])
            if self.address_page._sheet_has_value(row.get("addressName"))
            else existing
        )
        self.address_page.click_cancel_location_form()
        with allure.step("verify updated address is visible in the list (by row name)"):
            assert self.address_page.is_address_visible(new_name), (
                f"Address '{new_name}' should be visible after update"
            )
        if new_name != existing:
            with allure.step("verify previous address label is not shown after rename"):
                assert not self.address_page.is_address_visible(existing), (
                    f"Old address label '{existing}' should not remain after rename to '{new_name}'"
                )

    # @pytest.mark.data_driven
    # @pytest.mark.address
    # @pytest.mark.parametrize("row", address_cancel_data)
    # def test_cancel_address_edit_discards_changes(self, row):
    #     original = row.get("originalAddressName")
    #     draft = row.get("draftAddressName")
    #     assert original and draft, (
    #         "AddressCancel row must include originalAddressName and draftAddressName"
    #     )
    #     with allure.step("navigate to address page"):
    #         self.nav.navigate_to_address_page(
    #             TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, row.get("tenant")
    #         )
    #     with allure.step("open edit, change name, cancel"):
    #         success, outcome_msg = self.address_page.cancel_address_edit(original, draft)
    #         assert success, outcome_msg
    #     with allure.step("verify draft name was not saved (not visible in the list)"):
    #         assert not self.address_page.is_address_visible(draft), (
    #             f"Draft name '{draft}' must not appear after cancel"
    #         )
    #     with allure.step("verify original address is still visible in the list"):
    #         assert self.address_page.is_address_visible(original), (
    #             f"Original address '{original}' should still be visible after cancel"
    #         )


    @pytest.mark.data_driven
    @pytest.mark.address
    @pytest.mark.parametrize("row", _rows_prefix("AD_DELETE"), ids=_row_id)
    def test_delete_address_with_given_data(self, row):
        address_name = row.get("existingAddressName")
        with allure.step("navigate to address page"):
            self.nav.navigate_to_address_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, "us")
            with allure.step("delete address"):
                success, outcome_msg = self.address_page.delete_address(address_name)
                assert success, outcome_msg
            with allure.step("verify deleted address is not visible in the list"):
                assert self.address_page.wait_until_address_not_visible(address_name), (
                    f"Address '{address_name}' should no longer be visible after delete"
                )
