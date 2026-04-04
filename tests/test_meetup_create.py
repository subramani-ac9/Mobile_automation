import os
import time, random, string, pytest, re, logging
import pandas as pd
from datetime import datetime, timedelta
from utils.driver_manager import DriverManager
from utils.googleSheet_helper import read_google_sheet
from utils.time_zone_util import TimezoneFormatter
from config.config import TestConfig
from pages.login_page import LoginPage
from pages.my_events_page import MyEventsPage
from pages.onboard_page import OnBoardPage
from pages.meetup_create_page import MeetupCreatePage
from utils.helpers import take_screenshot, read_csv_as_dict, read_input_data, write_output_data, write_csv_from_dicts
from utils.navigator import Navigator
from constants.message.meetup_create_message import MeetupCreateMsg
from utils.logger_config import LoggerConfig

class TestMeetupCreate:
    meetup_create_csv = 'data/meetup_create_run1.csv'
    meetup_data =read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "Meetup")
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
            self.login_page = LoginPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.onboard_page = OnBoardPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.my_events_page = MyEventsPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.meetup_create = MeetupCreatePage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.nav = Navigator(self.driver, TestConfig.MOBILE_PLATFORM)
            self.message = MeetupCreateMsg.get_meetup_create_message()
            
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
    @pytest.mark.meetup_create
    # @pytest.mark.parametrize("row", read_csv_as_dict(meetup_create_csv))
    @pytest.mark.parametrize("row", meetup_data)
    def test_create_meetup_with_given_data(self, row):
        if row['event_type'].lower() == 'course': pytest.skip(f"Record skipped!")
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        result, e = self.meetup_create.create_meetup(row, self.message["meetup_create_success_msg"])
        assert result, (
            f"FAIL: Meetup Creation failed"
            f"Reason: {str(e)}"
        )
    
    @pytest.mark.data_driven_with_status
    @pytest.mark.meetup_create
    def test_create_meetup_with_status(self):
        import pandas as pd
        input_csv = self.meetup_create_csv    
        output_csv = 'data/meetup_create_run1_output.csv'

        df = pd.read_csv(input_csv)
        if 'status' not in df.columns:
            df['status'] = ''
        if 'detailed_result' not in df.columns:
            df['detailed_result'] = ''

        print(f"Processing {len(df)} test cases from {input_csv}")

        for index, row in df.iterrows():
            row_dict = row.to_dict()
            
            if 'test_case_id' not in row_dict:
                row_dict['test_case_id'] = f"M_{index + 1}"
            
            print(f"\n--- Processing Row {index + 1}/{len(df)} ---")
            
            try:
                print(f"Navigating to meetup creation page for test case {index + 1}...")
                self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
                result, error_message = self.meetup_create.create_meetup(row_dict, self.message["meetup_create_success_msg"])
                if result:
                    status = 'Created'
                    detailed_result = f"Success: {error_message}"
                else:
                    status = 'Not Created'
                    detailed_result = f"Failed: {error_message}"
                
                df.at[index, 'detailed_result'] = detailed_result
                
            except Exception as e:
                status = 'Error'
                detailed_result = f'Exception: {str(e)}'
                df.at[index, 'detailed_result'] = detailed_result
                print(f"Exception occurred for row {index + 1}: {e}")
            
            df.at[index, 'status'] = status
            print(f"Row {index + 1} Status: {status}")

        write_output_data(output_csv, df)
        print(f"\n=== Test Summary ===")
        print(f"Total test cases: {len(df)}")
        print(f"Created: {len(df[df['status'] == 'Created'])}")
        print(f"Not Created: {len(df[df['status'] == 'Not Created'])}")
        print(f"Errors: {len(df[df['status'] == 'Error'])}")
        print(f"Detailed results written to: {output_csv}")
        
        print("Successfully executed the meetup creation script")
    
    # @pytest.mark.data_driven_with_status
    # @pytest.mark.meetup_create
    # @pytest.mark.parametrize("index, row", list(enumerate(read_csv_as_dict(meetup_create_csv))))
    # def test_create_meetup_with_status(self, index, row):
    #     df = read_input_data(self.meetup_create_csv)
    #     try:
    #         self.logger.info(f" ~ Row({index + 1}) - Data Set ~")
    #         self.logger.info(row)
    #         self.nav.navigate_to_my_events_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
    #         self.my_events_page.start_to_create_meetup()
    #         result, e = self.meetup_create.create_meetup(row, self.message["meetup_create_success_msg"])
    #         if result:
    #             df.loc[int(index), 'status'] = "Passed"
    #         else:
    #             df.loc[int(index), 'status'] = f"Failed: {e}"
    #     except Exception as e:
    #         df.loc[int(index), 'status'] = f"Failed: {str(e)}"
    #     write_output_data(self.meetup_create_csv, df)


    
    @pytest.mark.testcase_id("CM_TC_194")
    @pytest.mark.meetup_create 
    def test_event_mode_display(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        result, e = self.meetup_create.is_meetup_mode_displayed("In-person")
        assert result, (
            f"FAIL: MEETUP_MODE::{"In-person"} selection field is not found"
            f"Reason: {e}"
        )
        result, e = self.meetup_create.is_meetup_mode_displayed("Online")
        assert result, (
            f"FAIL: MEETUP_MODE::{"Online"} selection field is not found"
            f"Reason: {e}"
        )

    @pytest.mark.testcase_id("CM_TC_21")
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("mode, product", [
        ("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT),
        ("In-person", "Long SKY Meditation Meetup"),
        ("In-person", "Sahaj Samadhi Meditation Meetup"),
    ])
    def test_select_in_person_product(self, mode, product):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        result, e = self.meetup_create.is_select_meetup_txt_field_displayed()
        assert result, (
            f"FAIL: MEETUP_PRODUCT selection field is not found"
            f"Reason: {e}"
        )
        self.meetup_create.select_meetup_mode_and_product(mode, product)
        result, e = self.meetup_create.is_txt_displayed(product)
        assert result, (
            f"FAIL: MEETUP_PRODUCT::{product} is not found"
            f"Reason: {e}"
        )
    @pytest.mark.testcase_id("CM_TC_21")
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("mode, product", [
        ("Online", TestConfig.TEST_MEETUP_ONLINE_PRODUCT),
    ])
    def test_select_online_product(self, mode, product):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        result, e = self.meetup_create.is_select_meetup_txt_field_displayed()
        assert result, (
            f"FAIL: MEETUP_PRODUCT selection field is not found"
            f"Reason: {e}"
        )
        self.meetup_create.select_meetup_mode_and_product(mode, product)
        result, e = self.meetup_create.is_txt_displayed(product)
        assert result, (
            f"FAIL: MEETUP_PRODUCT::{product} is not found"
            f"Reason: {e}"
        )

    #need to update the below method to ensure the private checkbox is checked or not!
    # @pytest.mark.data_driven
    # @pytest.mark.meetup_create
    # @pytest.mark.parametrize("row", read_csv_as_dict(meetup_create_csv)[-1:])
    # def test_user_can_check_is_private_check_box(self, row):
    #     self.nav.navigate_to_meetup_create_page(row["email"], row["password"])        #TODO could not differentiate - checked and unchecked
    #     self.meetup_create.select_meetup_mode(row["event_mode"])
    #     self.meetup_create.select_meetup(row["product_name"])
    #     if bool(row["is_private_event"]):
    #         self.meetup_create.check_private_meetup_checkbox(row["is_private_event"])
    #     assert self.meetup_create.is_private_checked(), "User is not able to check the is_private checkbox"
    
    @pytest.mark.testcase_id('CM_TC_195')
    @pytest.mark.meetup_create
    def test_set_max_attendees(self):
        max_attendees = random.randint(10, 99)
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("Online", TestConfig.TEST_MEETUP_ONLINE_PRODUCT)
        is_field_displayed, error_message = self.meetup_create.is_max_attendees_txt_field_displayed()
        assert is_field_displayed, (
            f"FAIL: MAX_ATTENDEES text field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.enter_max_attendees(max_attendees)
        actual_value, error = self.meetup_create.get_max_attendees_value()
        assert int(actual_value) == max_attendees, (
            f"FAIL: Expected MAX_ATTENDEES value '{max_attendees}' "
            f"but got '{actual_value}'. Reason: {error}"
        )
    
    @pytest.mark.testcase_id("CM_TC_196")
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("organizer", [
        "Gohul AC9",
        "Adarsh K",
        "Nivedha S",
        "Thangaraj C"
    ])
    def test_select_organizer(self, organizer):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_organizer_txt_field_displayed()
        assert result, (
            f"FAIL: ORGANIZER field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.select_organizer(organizer)
        result, error_message = self.meetup_create.is_txt_displayed(organizer)
        assert result, (
            f"FAIL: ORGANIZER field is not found"
            f"Reason: {error_message}"
        )
        
    @pytest.mark.testcase_id('CM_TC_77')
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("timezone", [
        "Eastern Time - EST",
        "Central Time - CST",
        "Mountain Time - MST",
        "Pacific Time - PST",
        "Hawaii Time - HST"
    ])
    def test_select_timezone(self, timezone):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        is_field_displayed, error_message = self.meetup_create.is_timezone_txt_field_displayed()
        assert is_field_displayed, (
            f"FAIL: TIMEZONE text field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.select_timezone(timezone)
        result, e = self.meetup_create.is_txt_displayed(timezone)
        assert result, (
            f"FAIL: TIMEZONE::{timezone} is not found"
            f"Reason: {e}"
        )
    
    @pytest.mark.testcase_id("CM_TC_29")
    @pytest.mark.meetup_create
    def test_select_start_date(self):
        start_date = f"{random.randint(1,12)}/{random.randint(1,30)}/{random.randint(2027,2030)}"
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_date_selection_txt_field_displayed()
        assert result, (
            f"FAIL: START_DATE field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.select_timezone("Eastern Time - EST")
        self.meetup_create.select_start_date(start_date)
        result, e = self.meetup_create.is_txt_displayed(start_date)
        assert result, (
            f"FAIL: STARDT_DATE::{start_date} is not found"
            f"Reason: {e}"
        )

    @pytest.mark.testcase_id("CM_TC_29")
    @pytest.mark.meetup_create
    def test_select_start_time(self):
        start_time = f"{random.randint(1, 12):02d}:{random.randint(0, 59):02d} {random.choice(['AM', 'PM'])}"
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_time_selection_txt_field_displayed()
        assert result, (
            f"FAIL: START_TIME field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.select_timezone("Eastern Time - EST")
        self.meetup_create.select_start_time(start_time)
        result, e = self.meetup_create.is_txt_displayed(re.sub(r"^0", "", start_time))
        assert result, (
            f"FAIL: START_TIME::{start_time} is not found"
            f"Reason: {e}"
        )

    @pytest.mark.testcase_id('CM_TC_197')
    @pytest.mark.meetup_create
    def test_enter_meetup_link(self):
        meetup_link = f"https://www.google.com"
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("Online", TestConfig.TEST_MEETUP_ONLINE_PRODUCT)
        result, error_message = self.meetup_create.is_link_field_displayed()
        assert result, (
            f"FAIL: MEETING _RL field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.enter_meeting_url(meetup_link)
        result, error = self.meetup_create.get_entered_link()
        assert meetup_link == result, (
            f"FAIL: Expected MEETING_URL value '{meetup_link}' "
            f"but got '{result}'. Reason: {error}"
        )
    
    @pytest.mark.testcase_id('CM_TC_70')
    @pytest.mark.meetup_create
    def test_enter_address(self):
        address = f"Partway street"
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_address_txt_field_displayed()
        assert result, (
            f"FAIL: ADDRESS field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.enter_address(address)
        result, error = self.meetup_create.is_given_location_field_displayed(address)
        assert result, (
            f"FAIL: ADDRESS::{address} is not found"
            f"Reason: {error}"
        )
    
    @pytest.mark.testcase_id('CM_TC_70')
    @pytest.mark.meetup_create
    def test_enter_city(self):
        city = f"California"
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_city_txt_field_displayed()
        assert result, (
            f"FAIL: CITY field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.enter_city(city)
        result, error = self.meetup_create.is_given_location_field_displayed(city)
        assert result, (
            f"FAIL: CITY::{city} is not found"
            f"Reason: {error}"
        )
    
    @pytest.mark.testcase_id('CM_TC_70')
    @pytest.mark.meetup_create
    def test_enter_zipcode(self):
        zipcode = f"{random.randint(11111,99999)}"
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_zipcode_txt_field_displayed()
        assert result, (
            f"FAIL: ZIPCODE field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.enter_zipcode(zipcode)
        result, error = self.meetup_create.is_given_location_field_displayed(zipcode)
        assert result, (
            f"FAIL: ZIPCODE::{zipcode} is not found"
            f"Reason: {error}"
        )
    
    @pytest.mark.testcase_id('CM_TC_70')
    @pytest.mark.testcase_id('CM_TC_62')
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("state", [
        "Alabama (AL)",
        "Alaska (AK)",
        "New York (NY)",
        "Texas (TX)"
    ])
    def test_select_state(self, state):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_state_txt_field_displayed()
        assert result, (
            f"FAIL: STATE field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.select_state(state.split(" (")[0])
        expected = state.split("(")[-1].replace(")", "")
        result, error = self.meetup_create.is_given_state_appr_displayed(expected)
        assert result, (
            f"FAIL: STATE::{expected} is not found"
            f"Reason: {error}"
        )
    
    @pytest.mark.testcase_id('CM_TC_25')
    @pytest.mark.testcase_id("CM_TC_67")
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("center", [
        "Dallas (TX)",
        "Bryan (TX)",
        "Auburn (AL)",
        "Vienna (VA)"
    ])
    def test_select_aol_center(self, center):
        choice = random.choice([
            ('Online', TestConfig.TEST_MEETUP_ONLINE_PRODUCT),
            ('In-person', TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        ])
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product(choice[0], choice[1])
        result, error_message = self.meetup_create.is_aol_center_txt_field_displayed()
        assert result, (
            f"FAIL: AOL_CENTER field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.select_aol_center(center)
        result, error_message = self.meetup_create.is_txt_displayed(center.split()[0])
        assert result, (
            f"FAIL: AOL_CENTER field is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_198')
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("contact", [
        "Gohul AC9",
        "Adarsh K",
        "Nivedha S",
        "Thangaraj C"
    ])
    def test_select_contact(self, contact):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_add_contact_displayed()
        assert result, (
            f"FAIL: CONTACT_PERSON field is not found"
            f"Reason: {error_message}"
        )
        self.meetup_create.select_contact_person(contact)
        result, error_message = self.meetup_create.is_txt_displayed(contact)
        assert result, (
            f"FAIL: CONTACT_PERSON field is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_199')
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("mode, product", [
        ("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT),
        ("Online", TestConfig.TEST_MEETUP_ONLINE_PRODUCT),
    ])
    def test_meetup_headers(self, mode, product):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        res1, err1 = self.meetup_create.is_new_meetup_header_displayed()
        self.meetup_create.select_meetup_mode_and_product(mode, product)
        res2, err2 = self.meetup_create.is_select_teacher_header_displayed()
        res3, err3 = self.meetup_create.is_select_organizer_header_displayed()
        res4, err4 = self.meetup_create.is_event_date_header_displayed()
        res5, err5 = False, "No Exception"
        if mode == 'In-person':
            res5, err5 = self.meetup_create.is_location_header_displayed()
        elif mode == 'Online':
            res5, err5 = self.meetup_create.is_meeting_url_header_displayed()
        res6, err6 = self.meetup_create.is_revenue_header_displayed()
        assert all([res1, res2, res3, res4, res5, res6]), (
            f"FAIL: HEADERS check failed: "
            f"new_meetup={err1}, " \
            f"select_teacher={err2}, " \
            f"select_organizer={err3}, " \
            f"event_date={err4}, " \
            f"location_or_url={err5}, " \
            f"revenue={err6}"
        )

    @pytest.mark.testcase_id("CM_TC_200")
    @pytest.mark.meetup_create
    def test_no_product_error(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["product_error_msg"])           
        assert result, (
            f"FAIL: NO_PRODUCT_ERROR MESSAGE is not found "
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_201")
    @pytest.mark.meetup_create
    def test_empty_max_attendees(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_max_attendees_err_displayed(self.message["common_err"])
        assert result, (
            f"FAIL: NO_MAXATTENDESS_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_20')
    @pytest.mark.testcase_id("CM_TC_27")
    @pytest.mark.meetup_create
    def test_no_teachers(self):
        count = random.randint(1,3)
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        for _ in range(count - 1): self.meetup_create.click_add_teacher()
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_no_teachers_err_displayed(count)          
        assert result, (
            f"FAIL: NO_TEACHERS ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_28")
    @pytest.mark.meetup_create
    def test_no_timezone_error(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["timezone_err_msg"])            
        assert result, (
            f"FAIL: NO_TIMEZONE_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )

    @pytest.mark.testcase_id('CM_TC_62')
    @pytest.mark.testcase_id("CM_TC_60")
    @pytest.mark.meetup_create
    def test_no_address_err(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_no_address_err_displayed(self.message["common_err"])    
        assert result, (
            f"FAIL: NO_ADDRESS_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_62')
    @pytest.mark.testcase_id("CM_TC_60")
    @pytest.mark.meetup_create
    def test_no_city_err(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_no_city_err_displayed(self.message["common_err"])    
        assert result, (
            f"FAIL: NO_CITY_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_62')
    @pytest.mark.testcase_id("CM_TC_60")
    @pytest.mark.meetup_create
    def test_no_zipcode_err(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["common_err"])            
        assert result, (
            f"FAIL: NO_ZIPCODE_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_62')
    @pytest.mark.testcase_id("CM_TC_60")
    @pytest.mark.meetup_create
    def test_no_state_err(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["state_err_msg"])            
        assert result, (
            f"FAIL: NO_STATE_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    @pytest.mark.testcase_id("CM_TC_70")
    @pytest.mark.meetup_create
    def test_address_visibility_online(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("Online", TestConfig.TEST_MEETUP_ONLINE_PRODUCT)
        res, err = self.meetup_create.is_location_header_displayed()
        assert not res, (
            f"FAIL: ADDRESS fields should not be displayed but was found. "
            f"Reason: {err}"
        )

    @pytest.mark.testcase_id('CM_TC_202')
    @pytest.mark.meetup_create
    def test_no_aol_center_err(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["center_err_msg"])            
        assert result, (
            f"FAIL: NO_AOLCENTER_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_203')
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("row", read_csv_as_dict(product_csv))
    def test_exceed_max_attendees_error(self,row):
        if row['format'].lower() == 'course': pytest.skip(f"Record skipped!")
        max_attendees = int(row['max_attendees']) + random.randint(1,10)
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product(row['format'], row['title'])
        self.meetup_create.enter_max_attendees(max_attendees)
        result, error_message = self.meetup_create.is_txt_displayed(self.message["max_attendees_exceed_err_msg"](row['max_attendees']))
        assert result, (
            f"FAIL: MAX_ATTENDEES_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_204')
    @pytest.mark.meetup_create          
    def test_negative_max_attendees(self):
        max_attendees = -1 * random.randint(1, 10)
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("Online", TestConfig.TEST_MEETUP_ONLINE_PRODUCT)
        self.meetup_create.enter_max_attendees(max_attendees)
        actual_value, error = self.meetup_create.get_max_attendees_value()
        assert int(actual_value) == abs(max_attendees), (
            f"FAIL: Expected MAX_ATTENDEES value '{max_attendees}' "
            f"but got '{actual_value}'. Reason: {error}"
        )
    
    @pytest.mark.testcase_id('CM_TC_63')
    @pytest.mark.meetup_create          # it covers the empty part as well
    def test_enter_invalid_link(self):
        meetup_link = random.choice(["www.google .com", "htp://google.com", "https://google", "https://goo<>gle.com", ""])
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("Online", TestConfig.TEST_MEETUP_ONLINE_PRODUCT)
        self.meetup_create.enter_meeting_url(meetup_link)
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["url_err_msg"])
        assert result, (
            f"FAIL: INVALID_MEETING_URL_ERROR MESSAGE is not found"
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_64")
    @pytest.mark.meetup_create         
    def test_reject_url_in_person(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_link_field_displayed()
        assert not result, (
            f"FAIL: MEETING_URL field should not be displayed but was found. "
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_64")
    @pytest.mark.meetup_create
    def test_short_address(self):
        min_length = 5
        invalid_address = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1,min_length)))
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.enter_address(invalid_address)
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["min_char_err_msg"](min_length))
        assert result, (
            f"FAIL: ADDRESS:: '{invalid_address}' - Expected a 'maximum {min_length} characters' error, but it was not found."
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_72")
    @pytest.mark.meetup_create
    def test_long_address(self):
        max_length = 100
        count = random.randint(max_length+1 , max_length + 10)
        address = ''.join(random.choices(string.ascii_letters + string.digits, k=count))
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.enter_address(address)
        result, error_message = self.meetup_create.get_entered_address()
        assert len(result) == max_length, (
            f"FAIL: ADDRESS:: should allow 'maximum of {max_length} characters, but it allowed more than {max_length}."
            f"Reason: {error_message}"
        )

    @pytest.mark.testcase_id('CM_TC_204')
    @pytest.mark.meetup_create
    def test_short_city(self):
        min_char = 3
        invalid_city = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1,min_char)))
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.enter_city(invalid_city)
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["min_char_err_msg"](min_char))
        assert result, (
            f"FAIL: CITY:: '{invalid_city}' - Expected a 'minimum of {min_char} characters' error, but it was not found."
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id('CM_TC_59')
    @pytest.mark.meetup_create
    def test_short_zipcode(self):
        max_char = 5
        invalid_zipcode = random.randint(1,9999)
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.enter_zipcode(str(invalid_zipcode))
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["min_char_zipcode_err"](max_char))
        assert result, (
            f"FAIL: ZIPCODE:: '{invalid_zipcode}' - Expected a 'maximum of {max_char} characters' error, but it was not found."
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_57")
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("timezone", [
        'Eastern Time - EST',
        'Central Time - CST',
        'Mountain Time - MST',
        'Pacific Time - PST',
        'Hawaii Time - HST' 
    ])
    def test_past_time(self, timezone):
        min_back_from_now = random.randint(1,10)
        hr_back_from_now = random.randint(0,1)
        today = TimezoneFormatter.get_the_current_date_for_given_timezone(timezone)
        past_time = TimezoneFormatter.get_the_past_time_for_given_timezone(timezone, hours=hr_back_from_now, minutes=min_back_from_now)
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.select_timezone(timezone)
        self.meetup_create.select_start_date(today)
        self.meetup_create.select_start_time(past_time)
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["date_err_msg2"])
        assert result, (
            f"FAIL: START_DATE::{today} START_TIME::{past_time} - Expected the past time error , but it was not found."
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_57")
    @pytest.mark.meetup_create
    @pytest.mark.parametrize("row", read_csv_as_dict(product_csv))
    def test_select_midnight_time(self, row):
        if row['format'].lower() == 'course': pytest.skip(f"Record skipped!")
        
        # Extract values from row
        product = row.get('title', 'Unknown Product')
        mode = row.get('format', 'Unknown Mode')
        duration = int(row.get('duration', 60))  # Default to 60 minutes if not specified
        
        timezone = random.choice(['Eastern Time - EST', 'Central Time - CST', 'Mountain Time - MST', 'Pacific Time - PST', 'Hawaii Time - HST'])
        today = TimezoneFormatter.get_the_current_date_for_given_timezone(timezone) 
        mid_night_time = datetime.strptime("12:00 AM", "%I:%M %p")
        future_date = (datetime.strptime(today, "%m/%d/%Y") + timedelta(days=1)).strftime("%m/%d/%Y")
        test_time = (mid_night_time - timedelta(minutes=duration)) + timedelta(minutes= random.randint(1, duration - 1))
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product(row['format'], row['title'])
        self.meetup_create.select_timezone(timezone)
        self.meetup_create.select_start_date(future_date)
        self.meetup_create.select_start_time(test_time.strftime("%I:%M %p"))
        self.meetup_create.click_create_now_button()
        result, error_message = self.meetup_create.is_error_message_displayed(self.message["time_err_msg"])
        assert result, (
            f"FAIL: PRODUCT::{product} MODE::{mode} DURATION::{duration} START_DATE::{future_date } TIMEZONE::{timezone} START_TIME::{test_time.strftime("%I:%M %p")} - Expected the end time error , but it was not found."
            f"Reason: {error_message}"
        )
    
    @pytest.mark.testcase_id("CM_TC_30")
    @pytest.mark.meetup_create
    def test_is_end_time_displayed(self):
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        result, error_message = self.meetup_create.is_end_time_displayed()
        assert not result, (
            f"FAIL: END_TIME should not be displayed, but it was found."
            f"Reason: {error_message}"
        )

    @pytest.mark.testcase_id('CM_TC_56')
    @pytest.mark.meetup_create
    @pytest.mark.test_past_date
    @pytest.mark.parametrize("timezone", [
        'Eastern Time - EST'
    ])
    def test_past_date(self, timezone):
        days, months, years = random.randint(1,30),random.randint(1,12),random.randint(0,2)
        past_date = TimezoneFormatter.get_past_date_for_given_timezone(timezone, days, months, years)
        self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
        self.meetup_create.select_meetup_mode_and_product("In-person", TestConfig.TEST_MEETUP_INPERSON_PRODUCT)
        self.meetup_create.select_timezone(timezone)
        self.meetup_create.select_start_date(past_date)
        result, error_message = self.meetup_create.is_out_range_err_displayed()
        assert result, (
            f"FAIL: START_DATE::{past_date} - Expected the past date error , but it was not found."
            f"Reason: {error_message}"
        )
    
    # TODO yet to add test method for - whether the private_checkbox checked or not
    # TODO yet to add test method for - send notification - need the expected result
    # TODO yet to add test method for - data driven with status
    # TODO Ensure the "Add Teacher" option lists all available teachers except the ones already selected

    # def test_extract_content(self):
    #     self.nav.navigate_to_meetup_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD)
    #     content = self.meetup_create.extract_page_contents()
    #     print(content)
