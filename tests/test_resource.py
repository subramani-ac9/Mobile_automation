import json
import time, random, string, pytest, re, logging
import pandas as pd
from datetime import datetime, timedelta
from constants.locator.myevent_locator import MyEventLocator
from pages import address_page
from pages.course_create_page import CourseCreatePage
from utils.driver_manager import DriverManager
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
from pages.resource_page import ResourcePage

import allure
class TestResource:
    resource_data = read_csv_as_dict('data/resource.csv')
    print(f"Resource data: {resource_data}")

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
            self.resource_page = ResourcePage(self.driver, platform=TestConfig.MOBILE_PLATFORM)
            self.nav = Navigator(self.driver, TestConfig.MOBILE_PLATFORM)
            
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
    @pytest.mark.resource
    def test_validate_resource_page(self):
        with allure.step("navigate to resource page"):   
            self.nav.navigate_to_resource_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
            time.sleep(10)



       
    