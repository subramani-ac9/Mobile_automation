import json
import os
import time, random, string, pytest, re, logging
import pandas as pd
from datetime import datetime, timedelta
from constants.locator.myevent_locator import MyEventLocator
from pages import address_page
from pages.course_create_page import CourseCreatePage
from utils.driver_manager import DriverManager
from utils.time_zone_util import TimezoneFormatter
from config.config import TestConfig
from utils.googleSheet_helper import read_google_sheet
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
    resource_data = read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "Resource")
    print(f"Resource data: {resource_data}")
    RESOURCE_PRODUCT_NAME = "Art of Living Part 1"
    AUDIO_RESOURCE_NAME = "Audio route test"
    DOCUMENT_RESOURCE_NAME = "[QA] Readme: Long Sudarshan Kriya"
    VIDEO_RESOURCE_NAME = "4K Cast Test File"

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

    @pytest.mark.resource
    @pytest.mark.regression 
    def test_validate_resource_page_authentication(self):
        with allure.step("navigate to resource page"):   
            self.nav.navigate_to_resource_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        with allure.step("Handle authentication popup"):
            self.resource_page.handle_authentication_if_present("986532")
        with allure.step("Validate resource page loaded"):
            assert self.resource_page.is_resources_page_displayed(), "Resources page not loaded"

    @pytest.mark.resource 
    @pytest.mark.regression 
    def test_validate_resource_page_authentication_failure(self):
        with allure.step("navigate to resource page"):   
            self.nav.navigate_to_resource_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        with allure.step("Handle authentication popup"):
            self.resource_page.handle_authentication_if_present("98653")
        with allure.step("Validate resource page loaded"):
            assert self.resource_page.is_authentication_screen_displayed(), "Authentication screen not displayed"

    
    @pytest.mark.resource 
    @pytest.mark.regression 
    def test_validate_resource_download_button_displayed(self):
        with allure.step("navigate to resource list page"):   
            is_resources_page_displayed = self.nav.navigate_to_resource_list_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
            assert is_resources_page_displayed, "Resources page not loaded"
            self.logger.info("Resource list page loaded")
        self.resource_page.click_resource_product_card(self.RESOURCE_PRODUCT_NAME)
        self.logger.info("click on one of the resourse from the list")
        assert self.resource_page.isDownloadButtonDisplayed("audio", self.AUDIO_RESOURCE_NAME), "Download button not displayed"
        self.logger.info("Download button displayed")

    @pytest.mark.resource 
    @pytest.mark.regression 
    def test_validate_resource_delete_button_displayed(self):
        with allure.step("navigate to resource list page"):   
            is_resources_page_displayed = self.nav.navigate_to_resource_list_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
            assert is_resources_page_displayed, "Resources page not loaded"
            self.logger.info("Resource list page loaded")
        self.resource_page.click_resource_product_card(self.RESOURCE_PRODUCT_NAME)
        self.logger.info("click on one of the resourse from the list")
        self.resource_page.click_resource_download_button("audio", self.AUDIO_RESOURCE_NAME)
        assert self.resource_page.isPauseDownloadButtonDisplayed("audio", self.AUDIO_RESOURCE_NAME), "Pause download button not displayed"
        assert self.resource_page.isDeleteButtonDisplayed("audio", self.AUDIO_RESOURCE_NAME), "Delete button not displayed"
        self.logger.info("Delete button displayed")
            
    @pytest.mark.resource 
    @pytest.mark.regression 
    def test_validate_resource_pause_download_button_displayed(self):
        with allure.step("navigate to resource list page"):   
            is_resources_page_displayed = self.nav.navigate_to_resource_list_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
            assert is_resources_page_displayed, "Resources page not loaded"
            self.logger.info("Resource list page loaded")
        self.resource_page.click_resource_product_card(self.RESOURCE_PRODUCT_NAME)
        self.logger.info("click on one of the resourse from the list")
        self.resource_page.click_resource_download_button("audio", self.AUDIO_RESOURCE_NAME)
        assert self.resource_page.isPauseDownloadButtonDisplayed("audio", self.AUDIO_RESOURCE_NAME), "Pause download button not displayed"
        self.logger.info("Pause download button displayed")
           
    @pytest.mark.resource 
    @pytest.mark.regression 
    def test_validate_resource_playing_All_elements_displayed(self):
        with allure.step("navigate to resource list page"):   
            is_resources_page_displayed = self.nav.navigate_to_resource_list_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
            assert is_resources_page_displayed, "Resources page not loaded"
            self.logger.info("Resource list page loaded")
        self.resource_page.click_resource_product_card(self.RESOURCE_PRODUCT_NAME)
        self.logger.info("click on one of the resourse from the list")
        self.resource_page.click_resource_download_button("audio", self.AUDIO_RESOURCE_NAME)
        assert self.resource_page.isPauseDownloadButtonDisplayed("audio", self.AUDIO_RESOURCE_NAME), "Pause download button not displayed"
        assert self.resource_page.isDeleteButtonDisplayed("audio", self.AUDIO_RESOURCE_NAME), "Delete button not displayed"
        self.resource_page.click_resourse_card("audio", self.AUDIO_RESOURCE_NAME)
        assert self.resource_page.isAllElementsDispalyed(self.AUDIO_RESOURCE_NAME), "All elements not displayed"
        self.logger.info("All elements displayed")
