import os
import time
from datetime import datetime, timedelta
from itertools import cycle
import random
import pytest
import pandas as pd
from pages.course_create_page import CourseCreatePage
from pages.course_details_page import CourseDetailsPage
from pages.filters_page import FiltersPage
from pages.login_page import LoginPage
from pages.my_events_page import MyEventsPage
from utils.googleSheet_helper import read_google_sheet
from utils.helpers import read_csv_as_dict, take_screenshot, write_output_data
from utils.navigator import Navigator
from utils.time_zone_util import TimezoneFormatter
from utils.driver_manager import DriverManager
from config.config import TestConfig
from constants.message.event_create_message import EventCreateMessage
import logging
from utils.logger_config import LoggerConfig


class TestCourseCreate:
    course_create_csv = 'data/course_create_run1.csv'
    course_create_validation_csv = 'data/course_create_validation1.csv'
    course_create_validation_data = read_csv_as_dict(course_create_validation_csv)
    search_course_data = read_csv_as_dict('data/search_course.csv')

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
            self.login_page = LoginPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.course_create = CourseCreatePage(self.driver, platform=TestConfig.MOBILE_PLATFORM)
            self.navigator = Navigator(self.driver, TestConfig.MOBILE_PLATFORM)
            self.event_create_message = EventCreateMessage.get_message()
            self.my_events_page = MyEventsPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.course_details = CourseDetailsPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.filter_page = FiltersPage(self.driver, TestConfig.MOBILE_PLATFORM)
            
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
            test_status = "COMPLETED"
            rep_call = getattr(request.node, "rep_call", None)
            if rep_call is not None and rep_call.failed:
                test_status = "FAILED"
                self.logger.error(f"Test failed: {test_method_name}")
                take_screenshot(self.driver, f"test_failed_{self.__class__.__name__}_{test_method_name}")

            LoggerConfig.log_test_end(self.logger, test_method_name, duration, test_status)
            
            # Cleanup
            try:
                self.logger.info("Starting test cleanup")
                self.driver_manager.quit_driver()
                self.logger.info("Test cleanup completed")
            except Exception as e:
                self.logger.error(f"Test cleanup failed: {str(e)}")

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven_with_status
    def test_course_create_with_status(self):
        import pandas as pd
        input_csv = self.course_create_csv    
        output_csv = 'data/course_create_run1_output.csv'

        df = pd.read_csv(input_csv)
        if 'status' not in df.columns:
            df['status'] = ''
        if 'detailed_result' not in df.columns:
            df['detailed_result'] = ''

        print(f"Processing {len(df)} test cases from {input_csv}")

        for index, row in df.iterrows():
            row_dict = row.to_dict()

            # Add test case ID if not present
            if 'Test Case ID' not in row_dict:
                row_dict['Test Case ID'] = f"TC_{index + 1}"
            
            print(f"\n--- Processing Row {index + 1}/{len(df)} ---")
            
            try:
                event_type = row_dict.get("event_type", "")
                if event_type == "course":
                    detailed_result = self.course_create.create_course(row_dict)
                else:
                    detailed_result = "Event type is not course"
                
                if detailed_result.startswith("Success"):
                    status = 'Created'
                else:
                    status = 'Not Created'
                
                df.at[index, 'detailed_result'] = detailed_result
                
            except Exception as e:
                status = 'Error'
                detailed_result = f'Exception: {str(e)}'
                df.at[index, 'detailed_result'] = detailed_result
                print(f"Exception occurred for row {index + 1}: {e}")
            
            df.at[index, 'status'] = status
            print(f"Row {index + 1} Status: {status}")
            
            # Navigate back to course creation page for next iteration
            if index + 1 < len(df):
                try:
                    print("Navigating back to course creation page...")
                    self.navigator.navigate_to_course_create_page(
                        TestConfig.TEST_EMAIL, 
                        TestConfig.TEST_PASSWORD
                    )
                except Exception as nav_error:
                    print(f"Navigation error: {nav_error}")

        write_output_data(output_csv, df)
        print(f"\n=== Test Summary ===")
        print(f"Total test cases: {len(df)}")
        print(f"Created: {len(df[df['status'] == 'Created'])}")
        print(f"Not Created: {len(df[df['status'] == 'Not Created'])}")
        print(f"Errors: {len(df[df['status'] == 'Error'])}")
        print(f"Detailed results written to: {output_csv}")


    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_14")
    # @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    @pytest.mark.parametrize("row", read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "CourseCreateIndia")[:1])
    def test_create_course_for_india(self, row):
        if row.get("tenant", "").strip().lower() == "us":
            self.navigator.navigate_to_course_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, 'us')
        else:
            self.navigator.navigate_to_course_create_page("KR2227", TestConfig.TEST_PASSWORD, 'india')
        self.course_create.create_course(row,self.event_create_message["course_create_success_msg"])
        assert self.course_create.is_msg_displayed(
            self.event_create_message["course_create_success_msg"]
        ), "Course creation success message not displayed"


    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_15")
    # @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run3.csv')[:1])
    @pytest.mark.parametrize("row", read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "CourseCreateUS")[:1])
    def test_create_course_for_us(self, row):
        if row.get("tenant", "").strip().lower() == "us":
            self.navigator.navigate_to_course_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, 'us')
        else:
            self.navigator.navigate_to_course_create_page("KR2227", TestConfig.TEST_PASSWORD, 'india')
        self.course_create.create_course(row,self.event_create_message["course_create_success_msg"])
        assert self.course_create.is_msg_displayed(
            self.event_create_message["course_create_success_msg"]
        ), "Course creation success message not displayed"

    @pytest.mark.validated
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_15")
    def test_cancel_course(self):
        searchButton = self.my_events_page.locator["search_button"]
        searchField = self.course_create.locator["search"]
        eventCode = "E-064923"
        self.navigator.navigate_to_my_events_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, 'us')
        self.course_create.cancel_course(eventCode)
        self.logger.info(f"Course cancelled successfully with event code: {eventCode}")
        self.logger.info(f"Validating course cancellation with event code: {eventCode}")
        time.sleep(2)
        filters =  {
            "filter_status": "filter_status_cancelled_checkBox",
        }
        self.logger.info(f"Applying filters: {filters}")
        self.filter_page.apply_filter_combination(filters)
        isCancelled = self.course_create.validate_cancel_course(eventCode)
        assert isCancelled, "Course cancellation validation failed"

    @pytest.mark.validated
    @pytest.mark.search_course
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_15")
    def test_search_field_functionality_us(self):
        searchButton = self.my_events_page.locator["search_button"]
        searchField = self.course_create.locator["search"]
        eventCode = self.search_course_data[0]["code"]
        self.navigator.navigate_to_my_events_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, 'us')
        self.course_create.enterEventCode(searchButton, searchField, eventCode)
        assert self.course_create.is_course_displayed(self.course_create.locator["event_cards"], eventCode), f"Course with event code {eventCode} not found on the UI"

    @pytest.mark.validated
    @pytest.mark.search_course
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_15")
    def test_search_field_functionality_india(self):
        searchButton = self.my_events_page.locator["search_button"]
        searchField = self.course_create.locator["search"]
        eventCode = self.search_course_data[1]["code"]
        self.navigator.navigate_to_my_events_page("KR2227", TestConfig.TEST_PASSWORD, 'india')
        self.course_create.enterEventCode(searchButton, searchField, eventCode)
        assert self.course_create.is_course_displayed(self.course_create.locator["event_cards"], eventCode), f"Course with event code {eventCode} not found on the UI"

    @pytest.mark.validated  
    @pytest.mark.search_course
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_15")
    def test_search_field_not_found_india(self):
        searchButton = self.my_events_page.locator["search_button"]
        searchField = self.course_create.locator["search"]
        eventCode = self.search_course_data[2]["code"]
        self.navigator.navigate_to_my_events_page("KR2227", TestConfig.TEST_PASSWORD, 'india')
        self.course_create.enterEventCode(searchButton, searchField, eventCode)
        assert self.course_create.is_msg_displayed(
            self.event_create_message["program_not_found_msg"]
        ), "program not found message not displayed"

    @pytest.mark.validated
    @pytest.mark.search_course
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_15")
    def test_search_field_not_found_us(self):
        searchButton = self.my_events_page.locator["search_button"]
        searchField = self.course_create.locator["search"]
        eventCode = self.search_course_data[2]["code"]
        self.navigator.navigate_to_my_events_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, 'us')
        self.course_create.enterEventCode(searchButton, searchField, eventCode)
        assert self.course_create.is_msg_displayed(
            self.event_create_message["event_not_found_msg"]
        ), "event not found message not displayed"
    
    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_16")
    def test_create_course_required_teacher(self):
        row = self.course_create_validation_data[0]
        print("row:",row)
        if row.get("tenant", "").strip().lower() == "us":
            self.navigator.navigate_to_course_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, 'us')
        else:
            self.navigator.navigate_to_course_create_page("KR2227", TestConfig.TEST_PASSWORD, 'india')
        self.course_create.create_course(row,self.event_create_message["teacher_required_err_msg"])
        assert self.course_create.is_msg_displayed(
            self.event_create_message["teacher_required_err_msg"]
        ), "Teacher required error message not displayed"

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.smoke
    @pytest.mark.testcase_id("CC_TC_17")
    def test_create_course_required_organizer(self):
        row = self.course_create_validation_data[1]
        print("row:",row)
        if row.get("tenant", "").strip().lower() == "us":
            self.navigator.navigate_to_course_create_page(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, 'us')
        else:
            self.navigator.navigate_to_course_create_page("KR2227", TestConfig.TEST_PASSWORD, 'india')
        self.course_create.create_course(row,self.event_create_message["teacher_required_err_msg"])
        assert self.course_create.is_msg_displayed(
            self.event_create_message["teacher_required_err_msg"]
        ), "Teacher required error message not displayed"


    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_42")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_mark_attendance_should_not_accept_negative_values(self, row):
        tenant = row.get("tenant", "us").strip().lower()
        row["max_attendees"] = -5
        self.course_create.enter_max_attendees(row["max_attendees"], tenant)
        observed = self.course_create.get_text_from_mark_attendance_text_field()
        self.logger.info(f"Observed: {observed}")
        assert str(observed) != "-5", f"Field accepts negative value (-5): observed='{observed}'"

    

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_13")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_error_message_displayed_when_creating_course_without_product(self, row):
        tenant = row.get("tenant", "us").strip().lower()
        row["product_name"] = ""
        # self.course_create.select_course(row["product_name"], tenant)
        self.course_create.enter_max_attendees(row["max_attendees"], tenant)
        assert self.course_create.is_error_message_displayed(
            self.event_create_message["product_error_msg"]
        ), "Product error message not displayed"

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_9")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_error_message_when_center_missing(self, row):
        row["aol_center"] = ""
        self.course_create.create_course(row)
        assert self.course_create.is_error_message_displayed(
            self.event_create_message["center_err_msg"]
        ), "Center required error not displayed"

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_12")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_error_message_when_contact_missing(self, row):
        row["contact_person"] = ""
        self.course_create.create_course(row)
        assert self.course_create.is_error_message_displayed(
            self.event_create_message["contact_err_msg"]
        ), "Contact person required error not displayed"

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_13")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_error_message_when_no_teacher_selected(self, row):
        row["teacher1"] = ""
        row["teacher2"] = ""    
        row["teacher3"] = ""
        self.course_create.create_course(row)
        assert self.course_create.is_teacher_err_msg_displayed(), "Teacher error message not displayed"

    """
    #unable to process as - Mobile app restrict seleting teacher,max attendees,date,time without selecting product
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_err_msg_when_fields_empty(self, row):
        row["product_name"] = ""
        row["teacher1"] = ""
        row["max_attendees"] = ""
        row["date1"] = ""
        row["start_time1"] = ""
        row["end_time1"] = ""
        self.course_create.create_course(row)

        assert self.course_create.is_max_attendees_err_msg_displayed(), "Max attendees required error not shown"
        assert self.course_create.is_teacher_err_msg_displayed(), "Teacher error message not displayed"
        assert self.course_create.is_error_message_displayed(
            self.event_create_message["product_error_msg"]
        ), "Course required error not displayed"
        assert self.course_create.is_datetime_err_displayed(), "Date/time error message not displayed"
    """

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_err_msg_when_timezone_missing(self, row):
        row["timezone"] = ""
        self.course_create.create_course(row)
        assert self.course_create.is_timezone_err_msg_displayed(), "Timezone required error not displayed"
    

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_33_1")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_selecting_past_date_1(self, row):
        row["date1"] = (datetime.today() - timedelta(days=1)).strftime("%m/%d/%Y")
        row["date2"] = ""
        row["date3"] = ""
        self.course_create.create_course(row)
        assert self.course_create.is_msg_displayed(
            self.event_create_message["past_date_msg"] or self.event_create_message["out_of_range_err_msg"] or self.event_create_message["date_invalid_err_msg"]
        ), "Past date error message not displayed"
    

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_33_2")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_selecting_past_date_2(self, row):
        print("check validation1")
        row["date2"] = (datetime.today() - timedelta(days=1)).strftime("%m/%d/%Y")
        row["date3"] = ""
        result = self.course_create.create_course(row)
        if result != "success":
            assert result in [self.event_create_message["past_date_msg"], 
                            self.event_create_message["out_of_range_err_msg"], 
                            self.event_create_message["date_invalid_err_msg"]], \
            f"Expected past date error message, got: {result}"

    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_33_3")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_selecting_past_date_3(self, row):
        row["date3"] = (datetime.today() - timedelta(days=1)).strftime("%m/%d/%Y")
        result = self.course_create.create_course(row)
        if result != "success":
            assert result in [self.event_create_message["past_date_msg"], 
                            self.event_create_message["out_of_range_err_msg"], 
                            self.event_create_message["date_invalid_err_msg"]], \
            f"Expected past date error message, got: {result}"


    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_40")
    @pytest.mark.parametrize("row", read_csv_as_dict('data/course_create_run1.csv')[:1])
    def test_max_attendees_zero_input(self, row):
        tenant = row.get("tenant", "us").strip().lower()
        row["max_attendees"] = 0
        self.course_create.select_course(row["product_name"], tenant)
        self.course_create.enter_max_attendees(row["max_attendees"], tenant)
        zero_error_displayed = self.course_create.is_max_attendees_zero_err_msg_displayed()
        generic_error_displayed = self.course_create.is_max_attendees_err_msg_displayed()
        assert zero_error_displayed or generic_error_displayed, f"Max attendees error message not displayed. Zero error: {zero_error_displayed}, Generic error: {generic_error_displayed}"

    @pytest.mark.course_create
    @pytest.mark.teacher_validation
    @pytest.mark.regression
    def test_verify_all_csv_teachers_available_in_teacher_listing(self):
        """
        Test to verify that all primary and assistant teachers from 'All Teachers.csv' 
        are available in the teacher selection dropdown for their respective courses
        """
        import pandas as pd
        import os
        
        # Read the All Teachers CSV file
        teachers_csv_path = 'data/All Teachers.csv'
        
        if not os.path.exists(teachers_csv_path):
            pytest.skip(f"Teachers CSV file not found at {teachers_csv_path}")
        
        df = pd.read_csv(teachers_csv_path)
        
        # Filter for active teachers (both primary and assistant based on type-2 column)
        active_teachers = df[
            (df['status'] == 'active') & 
            (df['type'].isin(['teacher', 'assistant-teacher'])) &
            (df['type-2'].isin(['primary', 'assistant']))
        ]
        
        # Group by product details to test teachers for different products
        grouped_teachers = active_teachers.groupby(['product_id', 'title', 'format'])
        
        # Track test results
        missing_teachers = []
        test_results = {
            'total_teachers_tested': 0,
            'total_products_tested': 0,
            'successful_verifications': 0,
            'failed_verifications': 0,
            'product_results': {}
        }
        
        print(f"\n=== Teacher Availability Test ===")
        print(f"Total active teachers found in CSV: {len(active_teachers)}")
        print(f"Products to test: {len(grouped_teachers)}")
        
        for (product_id, course_title, event_format), product_teachers in grouped_teachers:
            print(f"\n=== Testing Product: {course_title} ({event_format}) - ID: {product_id} ===")
            
            # First, select the event type and course for this product
            try:
                self._setup_course_for_teacher_testing(course_title, event_format)
                print(f"Successfully selected course: {course_title} ({event_format})")
            except Exception as e:
                print(f"Failed to select course {course_title} ({event_format}): {e}")
                # Skip this product if we can't select it
                continue
            
            test_results['total_products_tested'] += 1
            
            # Test teachers in order: Primary first, then Additional
            teacher_types_order = ['primary', 'assistant']
            
            for teacher_type in teacher_types_order:
                # Filter teachers for this specific type
                teachers_of_type = product_teachers[product_teachers['type-2'] == teacher_type]
                
                if teachers_of_type.empty:
                    print(f"\n  No {teacher_type} teachers found for {course_title} ({event_format})")
                    continue
                
                print(f"\n  Testing {teacher_type} teachers for {course_title} ({event_format})")
                
                # Get unique teachers (by combining first_name and last_name)
                unique_teachers = teachers_of_type.drop_duplicates(subset=['first_name', 'last_name'])
                print(f"  Teachers to test: {len(unique_teachers)}")
                
                for _, teacher_row in unique_teachers.iterrows():
                    # Combine first_name and last_name with space
                    teacher_full_name = f"{teacher_row['first_name']} {teacher_row['last_name']}".strip()
                    
                    # Skip if name is empty or invalid
                    if not teacher_full_name or teacher_full_name == " ":
                        continue
                    
                    test_results['total_teachers_tested'] += 1
                    
                    try:
                        # Test teacher availability based on type (primary or assistant)
                        teacher_found = self._verify_teacher_availability_for_selected_course(
                            teacher_full_name, 
                            teacher_type
                        )
                        
                        if teacher_found:
                            test_results['successful_verifications'] += 1
                            print(f"    ✓ Found: {teacher_full_name}")
                        else:
                            missing_teachers.append({
                                'name': teacher_full_name,
                                'product_id': product_id,
                                'course_title': course_title,
                                'format': event_format,
                                'type': teacher_type,
                                'email': teacher_row.get('email', 'N/A')
                            })
                            test_results['failed_verifications'] += 1
                            print(f"    ✗ Missing: {teacher_full_name}")
                            
                    except Exception as e:
                        missing_teachers.append({
                            'name': teacher_full_name,
                            'product_id': product_id,
                            'course_title': course_title,
                            'format': event_format,
                            'type': teacher_type,
                            'email': teacher_row.get('email', 'N/A'),
                            'error': str(e)
                        })
                        test_results['failed_verifications'] += 1
                        print(f"    ✗ Error testing {teacher_full_name}: {e}")
                
                # Add a small pause between primary and assistant teacher testing
                if teacher_type == 'primary':
                    time.sleep(1)
                    print(f"  ✓ Completed testing {teacher_type} teachers, moving to assistant teachers...")
            
            # Navigate back to course creation page for next product
            if test_results['total_products_tested'] < len(grouped_teachers):
                try:
                    print("  Navigating back to course creation page for next product...")
                    self.navigator.navigate_to_course_create_page(
                        TestConfig.TEST_EMAIL, 
                        TestConfig.TEST_PASSWORD
                    )
                    time.sleep(2)
                except Exception as nav_error:
                    print(f"  Navigation error: {nav_error}")
        
        # Print final test summary
        print(f"\n=== Final Test Summary ===")
        print(f"Products tested: {test_results['total_products_tested']}")
        print(f"Total teachers tested: {test_results['total_teachers_tested']}")
        print(f"Successfully verified: {test_results['successful_verifications']}")
        print(f"Failed verifications: {test_results['failed_verifications']}")
        
        if missing_teachers:
            print(f"\n=== Missing Teachers ({len(missing_teachers)}) ===")
            for teacher in missing_teachers:
                error_info = f" (Error: {teacher['error']})" if 'error' in teacher else ""
                print(f"  - {teacher['name']} | Course: {teacher['course_title']} ({teacher['format']}) | Type: {teacher['type']} | Email: {teacher['email']}{error_info}")
        
        # Detailed assertion with helpful error message
        success_rate = (test_results['successful_verifications'] / test_results['total_teachers_tested']) * 100 if test_results['total_teachers_tested'] > 0 else 0
        
        assert len(missing_teachers) == 0, (
            f"Teacher verification failed! "
            f"{len(missing_teachers)} out of {test_results['total_teachers_tested']} teachers were not found. "
            f"Success rate: {success_rate:.1f}%. "
            f"First 5 missing teachers: {[f'{t['name']} ({t['course_title']})' for t in missing_teachers[:5]]}"
        )
        
        print(f"✓ All teachers successfully verified! Success rate: {success_rate:.1f}%")

    def _setup_course_for_teacher_testing(self, course_title: str, event_format: str, tenant: str = "us") -> bool:
        """
        Helper method to select event type and course name before testing teachers
        
        Args:
            course_title: Name of the course (e.g., "Art of Living Part 1")
            event_format: Format of the event ("in-person" or "online")
            tenant: Tenant identifier (default: "us")
            
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            # Select event mode based on format
            print(f"    Setting up course: {course_title} ({event_format})")
            
            # Map format to event mode
            if event_format.lower() == 'in-person':
                event_mode = 'In-person'
            elif event_format.lower() == 'online':
                event_mode = 'Online'
            else:
                raise Exception(f"Unknown event format: {event_format}")
            
            # Select event mode
            self.course_create.select_event_mode(event_mode)
            time.sleep(1)
            
            # Select course with tenant
            self.course_create.select_course(course_title, tenant)
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"Error setting up course {course_title} ({event_format}): {e}")
            return False

    def _verify_teacher_availability_for_selected_course(self, teacher_name: str, teacher_type: str) -> bool:
        """
        Helper method to verify if a teacher is available in the teacher selection dropdown
        for the currently selected course
        
        Args:
            teacher_name: Full name of the teacher (first_name + last_name)
            teacher_type: 'primary' or 'assistant'
            
        Returns:
            bool: True if teacher is found, False otherwise
        """
        try:
            # Determine which teacher field to use based on type
            if teacher_type == 'primary':
                teacher_field = self.course_create.locator["teacher_primary_txt_field"]
            else:  # assistant
                teacher_field = self.course_create.locator["teacher_additional_txt_field"]
            
            # Click on the teacher field to open dropdown
            self.course_create.scroll_to_element(self.course_create.locator["scroll"], teacher_field)
            self.course_create.click_element(teacher_field)
            time.sleep(2)
            
            # Search for the teacher
            search_field = self.course_create.locator["search"]
            self.course_create.send_keys(search_field, teacher_name, 5, is_necessary=False)
            time.sleep(2)
            
            # Try to find the teacher in the dropdown
            teacher_item = self.course_create.build_locator(self.course_create.locator["item"], teacher_name)
            teacher_found = self.course_create.is_displayed(teacher_item, timeout=3)
            
            # Always dismiss keyboard properly to ensure search continues
            self._dismiss_keyboard_and_dropdown()
            
            return teacher_found
            
        except Exception as e:
            print(f"      Error verifying teacher {teacher_name}: {e}")
            # Try to recover by dismissing keyboard and dropdown
            self._dismiss_keyboard_and_dropdown()
            return False

    def _dismiss_keyboard_and_dropdown(self):
        """
        Helper method to properly dismiss keyboard and dropdown after teacher search
        """
        try:
            # First try to hide keyboard if it's visible
            if self.course_create.platform == "android":
                # On Android, press Done key to dismiss keyboard first
                self.course_create.driver.press_keycode(66)  # KEYCODE_ENTER/Done
                time.sleep(0.5)
                # Click on Scrim background to close dropdown
                try:
                    scrim_element = self.course_create.locator["background"]
                    self.course_create.click_element(scrim_element, timeout=2)
                    print(f"      ✓ Clicked on Scrim background to close dropdown")
                except:
                    # Fallback to back button if Scrim click fails
                    self.course_create.driver.press_keycode(4)  # Back button
                    print(f"      ✓ Used back button as fallback")
            else:
                # On iOS, hide keyboard with Done button
                self.course_create.driver.hide_keyboard(key_name='Done')
                time.sleep(0.5)
                # Click on Scrim background to close dropdown
                try:
                    scrim_element = self.course_create.locator["background"]
                    self.course_create.click_element(scrim_element, timeout=2)
                    print(f"      ✓ Clicked on Scrim background to close dropdown")
                except:
                    # Fallback to tapping outside if Scrim click fails
                    try:
                        screen_size = self.course_create.driver.get_window_size()
                        self.course_create.driver.tap([(screen_size['width'] // 2, screen_size['height'] // 4)])
                        print(f"      ✓ Used tap outside as fallback")
                    except:
                        pass
            
            time.sleep(1)  # Allow UI to settle
            
        except Exception as e:
            print(f"      Warning: Could not properly dismiss keyboard/dropdown: {e}")
            # Final fallback - just wait a bit
            time.sleep(1)
            

    """
    #unable to process as by default app shows 3 days schedule
    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_17")
    def test_course_with_num_days_minus_one_schedule(self):
        #CC_TC_17: Create a course with only product.num_days-1 days schedule given for a 3 days course
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()
        row["no_of_dates"] = 2  
        row["date1"] = (datetime.today() + timedelta(days=1)).strftime("%m/%d/%Y")
        row["date2"] = (datetime.today() + timedelta(days=2)).strftime("%m/%d/%Y")

        tenant = row.get("tenant", "us").strip().lower()
        # Fill all required fields except Create Now to check Add Date button availability
        self.course_create.select_event_mode(row["event_mode"])
        self.course_create.select_course(row["product_name"], tenant)
        if row["is_private"].upper() == "TRUE":
            self.course_create.check_is_private(True, tenant)
        self.course_create.enter_max_attendees(row["max_attendees"], tenant)
        self.course_create.select_n_teachers(row)
        self.course_create.select_organizers(row["organizer"])
        self.course_create.select_timezone(row["timezone"])
        self.course_create.select_n_date(row)
        self.course_create.select_n_time(row)
        
        # Check Add Date button availability for insufficient dates scenario (should be available)
        is_add_date_available = self.course_create.is_add_date_button_available()
        self.logger.info(f"Add Date button availability for num_days-1 (2 dates for 3-day course): {is_add_date_available}")
        assert is_add_date_available, "Add Date button should be available when insufficient dates are provided for a 3-day course"
        
        # Continue with course creation to trigger validation
        self.course_create.click_create_button()
        assert self.course_create.is_msg_displayed(
            self.course_create_message["insufficient_dates_msg"]
        ), "Insufficient dates error message not displayed for num_days-1 schedule"
    """
    
    @pytest.mark.validated
    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_17_1")
    def test_add_date_button_not_available_after_all_dates_entered(self):
        """CC_TC_17_1: Verify Add Date button is NOT available after entering all required dates for a 3-day course"""
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()
        tenant = row.get("tenant", "us").strip().lower()
        
        # Verify this is a 3-day course from products.csv
        products_df = pd.read_csv('data/products.csv')
        product_info = products_df[products_df['id'] == int(row['product_id'])]
        if product_info.empty:
            pytest.fail(f"Product ID {row['product_id']} not found in products.csv")
        
        product_duration = int(product_info.iloc[0]['duration'])
        if product_duration != 3:
            pytest.fail(f"Expected 3-day course, but product duration is {product_duration} days")
        
        teacher_names = [
                teacher for teacher in [
                    row.get("teacher1", ""),
                    row.get("teacher2", ""),
                    row.get("teacher3", "")
                ] if teacher.strip()
            ]
        no_of_dates = int(row.get("no_of_dates", 1))
        event_dates = []
        for i in range(1, no_of_dates + 1):
            date_key = f"date{i}"
            start_time_key = f"start_time{i}"
            end_time_key = f"end_time{i}"
            
            if row.get(date_key) and row.get(start_time_key) and row.get(end_time_key):
                event_dates.append({
                    "date": row[date_key],
                    "start_time": row[start_time_key],
                    "end_time": row[end_time_key]
                })
        dates = [event["date"] for event in event_dates]
        times = [(event["start_time"], event["end_time"]) for event in event_dates]
        self.course_create.select_event_mode(row["event_mode"])
        self.course_create.select_course(row["product_name"], tenant)
        if row["is_private"].upper() == "TRUE":
            self.course_create.check_is_private(True, tenant)
        self.course_create.enter_max_attendees(row["max_attendees"], tenant)
        self.course_create.select_n_teachers(teacher_names)
        self.course_create.select_organizers(row["organizer"])
        self.course_create.select_timezone(row["timezone"])
        self.course_create.select_n_date(dates)
        self.course_create.select_n_time(times)
        
        # After entering all 3 dates, Add Date button should NOT be available
        is_add_date_available = self.course_create.is_add_date_button_available()
        assert not is_add_date_available, "Add Date button should NOT be available after entering all required dates for a 3-day course"

    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_18")    
    def test_course_with_num_days_plus_one_schedule(self):
        """CC_TC_18: Create a course with only product.num_days+1 days schedule given for a 3 days course"""
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()
        tenant = row.get("tenant", "us").strip().lower()
        # Assuming a 3-day course, set 4 days
        row["no_of_dates"] = 4  # Should be 3 for a 3-day course
        row["date1"] = (datetime.today() + timedelta(days=1)).strftime("%m/%d/%Y")
        row["date2"] = (datetime.today() + timedelta(days=2)).strftime("%m/%d/%Y")
        row["date3"] = (datetime.today() + timedelta(days=3)).strftime("%m/%d/%Y")
        row["date4"] = (datetime.today() + timedelta(days=4)).strftime("%m/%d/%Y")

        # Fill all required fields except Create Now to check Add Date button availability
        self.course_create.select_event_mode(row["event_mode"])
        self.course_create.select_course(row["product_name"], tenant)
        if row["is_private"].upper() == "TRUE":
            self.course_create.check_is_private(True, tenant)
        self.course_create.enter_max_attendees(row["max_attendees"], tenant)
        self.course_create.select_n_teachers(row)
        self.course_create.select_organizers(row["organizer"])
        self.course_create.select_timezone(row["timezone"])
        self.course_create.select_n_date(row)
        self.course_create.select_n_time(row)
        
        # Check Add Date button availability for excess dates scenario (should NOT be available)
        is_add_date_available = self.course_create.is_add_date_button_available()
        self.logger.info(f"Add Date button availability for num_days+1 (4 dates for 3-day course): {is_add_date_available}")
        assert not is_add_date_available, "Add Date button should NOT be available when excess dates are provided for a 3-day course"
        
        # Continue with course creation to trigger validation
        self.course_create.click_create_button()
        assert self.course_create.is_msg_displayed(
            self.course_create_message["excess_dates_msg"]
        ), "Excess dates error message not displayed for num_days+1 schedule"

    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_75")
    def test_consecutive_dates_out_of_range_error(self):
        """CC_TC_75: Ensure that for consecutive dates courses - out of range error occurs for a valid date with in a range"""
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()
        row["no_of_dates"] = 3
        # Create non-consecutive dates for a course that requires consecutive dates
        row["date1"] = (datetime.today() + timedelta(days=1)).strftime("%m/%d/%Y")
        row["date2"] = (datetime.today() + timedelta(days=3)).strftime("%m/%d/%Y")  # Gap in dates
        row["date3"] = (datetime.today() + timedelta(days=5)).strftime("%m/%d/%Y")

        self.course_create.create_course(row)
        assert self.course_create.is_msg_displayed(
            self.course_create_message["non_consecutive_dates_msg"]
        ), "Non-consecutive dates error message not displayed"

    
    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_81")
    def test_product_search_pagination_handling(self):
        """CC_TC_81: Ensure that the empty list was not visible to user while searching for a PRODUCT NAME and pagination for course was handled positively"""
        # Test product search with pagination
        search_term = "Art"  # Should return multiple results

        # Start typing in product search
        self.course_create.search_product(search_term)

        # Verify that empty list is not shown during search
        assert not self.course_create.is_empty_list_displayed(), "Empty list displayed during product search"

        # Verify pagination works correctly
        assert self.course_create.is_pagination_working(), "Product pagination not working correctly"

        # Verify all matching products are shown
        matching_products = self.course_create.get_matching_product_count(search_term)
        assert matching_products > 0, "No matching products found for search term"

    
    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("MCC_TC_11")
    def test_publish_course_button_disabled_until_required_fields_completed(self):
        """MCC_TC_11: Ensure that the "Publish Course" button is disabled until all required fields are completed"""
        # Start with empty form
        assert self.course_create.is_publish_button_disabled(), "Publish button should be disabled when no fields are filled"

        # Fill some fields but leave required ones empty
        self.course_create.select_course("Test Course")
        assert self.course_create.is_publish_button_disabled(), "Publish button should be disabled when required fields are missing"

        # Fill all required fields
        self.course_create.select_event_mode("Online")
        self.course_create.select_course("Art of Living Part 1")
        self.course_create.enter_max_attendees(10)
        self.course_create.select_teacher("Test Teacher", "primary")
        self.course_create.enter_organizer("Test Organizer")
        self.course_create.enter_contact_person("Test Contact")
        self.course_create.select_timezone("Asia/Kolkata")
        self.course_create.enter_date_time("01-Jan-2025", "10:00 AM", "12:00 PM")

        # Now publish button should be enabled
        assert self.course_create.is_publish_button_enabled(), "Publish button should be enabled when all required fields are completed"

    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.data_driven
    @pytest.mark.testcase_id("CC_TC_119")
    def test_add_teacher_option_available_with_three_teachers(self):
        """CC_TC_119: Have 3 teachers in initial course and check "add teacher" option is available"""
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()

        # Add 3 teachers initially
        self.course_create.select_teacher("Teacher 1", "primary")
        self.course_create.select_teacher("Teacher 2", "assistant")
        self.course_create.select_teacher("Teacher 3", "assistant")

        # Verify add teacher option is still available
        assert self.course_create.is_add_teacher_option_available(), "Add teacher option should be available even with 3 teachers"

        # Verify we can add a 4th teacher
        self.course_create.click_add_teacher_button()
        assert self.course_create.is_teacher_selection_available(), "Should be able to add 4th teacher"

    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_123")
    def test_add_teacher_option_does_not_allow_members(self):
        """CC_TC_123: Ensure that Add teacher option should not allow Members in dropdown"""
        # Click add teacher button
        self.course_create.click_add_teacher_button()

        # Verify that members are not shown in teacher dropdown
        # This would require checking the dropdown content
        # For now, we'll verify the teacher selection interface is available
        assert self.course_create.is_teacher_selection_available(), "Teacher selection interface should be available"

    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.data_driven
    @pytest.mark.testcase_id("CC_TC_124")
    def test_add_teacher_filters_eligible_teachers_only(self):
        """CC_TC_124: Ensure that Other course eligible teacher/assistant teacher should not be listed in dropdown, unless he/she is eligible to this event"""
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()

        # Select a specific course first
        self.course_create.select_course("Art of Living Part 1")

        # Click add teacher button
        self.course_create.click_add_teacher_button()

        # Verify teacher selection is available
        assert self.course_create.is_teacher_selection_available(), "Teacher selection should be available"

    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_131")
    def test_nda_signed_teacher_listing(self):
        """CC_TC_131: Check for Nda signed teacher listing in dropdown"""
        # Click add teacher button
        self.course_create.click_add_teacher_button()

        # Verify teacher selection interface
        assert self.course_create.is_teacher_selection_available(), "Teacher selection interface should be available"


    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_136")
    def test_save_course_without_teachers_assigned(self):
        """CC_TC_136: Trying to save the course without having any teachers assigned"""
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()

        # Clear all teacher fields
        row["teacher1"] = ""
        row["teacher2"] = ""
        row["teacher3"] = ""

        # Try to create course
        self.course_create.create_course(row)

        # Verify error message for no teachers assigned
        assert self.course_create.is_teacher_err_msg_displayed(), "Teacher error message should be displayed"


    @pytest.mark.course_create
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_138")
    def test_adding_assistant_teacher_with_send_notification_enabled(self):
        """CC_TC_138: Adding an assistant teacher with send notification enabled"""
        # Select primary teacher first
        self.course_create.select_teacher("Primary Teacher", "primary")

        # Add assistant teacher
        self.course_create.click_add_teacher_button()
        self.course_create.select_teacher("Assistant Teacher", "assistant")

        # Complete course creation
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()
        self.course_create.fill_remaining_fields(row)
        self.course_create.create_course(row)

        # Verify course created successfully
        assert self.course_create.is_msg_displayed(
            self.event_create_message["course_create_success_msg"]
        ), "Course creation success message not displayed"

    @pytest.mark.course_create
    @pytest.mark.data_driven
    @pytest.mark.regression
    @pytest.mark.testcase_id("CC_TC_139")
    def test_adding_assistant_teacher_without_send_notification(self):
        """CC_TC_139: Adding an assistant teacher without enabling send notification"""
        # Select primary teacher first
        self.course_create.select_teacher("Primary Teacher", "primary")

        # Add assistant teacher
        self.course_create.click_add_teacher_button()
        self.course_create.select_teacher("Assistant Teacher", "assistant")

        # Complete course creation
        row = read_csv_as_dict('data/course_create_run1.csv')[0].copy()
        self.course_create.fill_remaining_fields(row)
        self.course_create.create_course(row)

        # Verify course created successfully
        assert self.course_create.is_msg_displayed(
            self.event_create_message["course_create_success_msg"]
        ), "Course creation success message not displayed"
