import logging
import re
import pytest
import random, string
import time
from datetime import datetime, timedelta
import pandas as pd
from utils.driver_manager import DriverManager
from config.config import TestConfig
from utils.time_zone_util import TimezoneFormatter
from pages.my_events_page import MyEventsPage
from pages.onboard_page import OnBoardPage
from pages.meetup_details_page import MeetupDetailsPage
from utils.helpers import take_screenshot, read_csv_as_dict, read_input_data, write_output_data
from utils.navigator import Navigator
from utils.logger_config import LoggerConfig

class TestMeetDetails:
    meetup_create_csv = 'data/event_validate1.csv'
    product_csv = 'data/products.csv'

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
            self.my_events_page = MyEventsPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.meetup_details = MeetupDetailsPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.nav = Navigator(self.driver, TestConfig.MOBILE_PLATFORM)
            self.nav.navigate_to_my_events_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)

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
    @pytest.mark.parametrize("index, row", enumerate(read_csv_as_dict(meetup_create_csv)))
    def test_verify_created_meetups(self, index, row):
        # if row['event_type'].lower() == 'course': pytest.skip(f"Record skipped!")
        self.logger.info(f" ~ Row({index + 1}) - Data Set ~")
        # self.logger.info(row)
        # date = datetime.strptime(row['date1'], "%m/%d/%Y")
        
        # row['end_time1'] = TimezoneFormatter.add_duration_to_time(row['start_time1'], int(product['duration'].iloc[0]), str(product['duration_unit'].iloc[0]))
        # prev_day = (date - timedelta(days=1)).strftime("%-m/%-d/%Y")
        # next_day = (date + timedelta(days=1)).strftime("%-m/%-d/%Y")

        # self.nav.navigate_to_my_events_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        # res, exp = self.my_events_page.choose_advance_filter(types=['Meetup'], statuses=['Active'], date_range=[prev_day, next_day])
        # assert res, f"Filter Selection failed, {exp}"

        status = self.my_events_page.pick_event_card(row)
        print(status)