import pytest
import allure
import pandas as pd
import time
from pages.login_page import LoginPage
from pages.my_events_page import MyEventsPage
from pages.onboard_page import OnBoardPage
from pages.logout_page import LogoutPage
import logging
from utils.navigator import Navigator
from utils.driver_manager import DriverManager
from config.config import TestConfig
from utils.helpers import take_screenshot, read_csv_as_dict, read_input_data, write_output_data
from constants.message.login_message import LoginMessage
from utils.logger_config import LoggerConfig


class TestLogin:
    valid_credentials_csv = 'data/valid_credentials.csv'
    invalid_credentials_csv = 'data/invalid_credentials.csv'

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
            self.logger.info("Initializing test setup")
            self.driver_manager = DriverManager()
            self.driver = self.driver_manager.start_driver()
            
            self.logger.info("Initializing page objects")
            self.login_page = LoginPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.onboard_page = OnBoardPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.my_events_page = MyEventsPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.navigator = Navigator(self.driver,TestConfig.MOBILE_PLATFORM)
            self.logout_page = LogoutPage(self.driver,TestConfig.MOBILE_PLATFORM)
            self.login_message = LoginMessage.get_message()
            
            request.node.driver = self.driver  # for Allure screenshot-on-failure hook
            self.logger.info("Test setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Test setup failed: {str(e)}")
            raise

        yield
        
        # Calculate test duration
        end_time = time.time()
        duration = end_time - start_time
        
        # Check if test failed
        test_status = "COMPLETED"
        if hasattr(self, '_outcome') and self._outcome.result.failed:
            test_status = "FAILED"
            self.logger.error(f"Test failed: {test_method_name}")
            take_screenshot(self.driver, f"test_failed_{self.__class__.__name__}_{test_method_name}")
        
        # Log test end
        LoggerConfig.log_test_end(self.logger, test_method_name, duration, test_status)
        
        # Cleanup
        try:
            self.logger.info("Starting test cleanup")
            self.driver_manager.quit_driver()
            self.logger.info("Test cleanup completed")
        except Exception as e:
            self.logger.error(f"Test cleanup failed: {str(e)}")


    # LG_TC_1: Ensure a user can log in with valid credentials

    @pytest.mark.testcase_id("LG_TC_1")
    @pytest.mark.login
    @pytest.mark.test_successful_login
    def test_successful_login(self):
        self.logger.info("Starting successful login test")
        with allure.step("Navigate to Login screen"):
            self.navigator.navigate_to_login()
        with allure.step("Verify Login page is displayed"):
            login_page_displayed = self.login_page.is_login_page_displayed()
            LoggerConfig.log_assertion(self.logger, "Login page should be displayed", login_page_displayed)
            assert login_page_displayed, "Login page should be displayed"
        with allure.step("Perform login with valid credentials"):
            self.login_page.login(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, "US")
        with allure.step("Verify dashboard and post-login state"):
            validations = self.my_events_page.validate_successful_login("US")
            for validation in validations:
                validation_result = "not" not in validation.lower()
                LoggerConfig.log_assertion(self.logger, f"Validation: {validation}", validation_result)
                assert validation_result, f"Validation failed: {validation}"
        with allure.step("Logout"):
            self.logout_page.logout()
        self.logger.info("Successful login test completed successfully")

    
    @pytest.mark.testcase_id("LG_TC_1")
    @pytest.mark.data_driven
    @pytest.mark.login
    @pytest.mark.parametrize("row", read_csv_as_dict('data/valid_credentials.csv'))
    def test_valid_credentials_data_driven(self, row):
        print(f"testing scenario: {row['test_scenario']} for tenant: {row['tenant']}")
        with allure.step("Navigate to Login screen"):
            self.navigator.navigate_to_login()
        with allure.step("Verify Login page and perform login"):
            assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
            self.login_page.login(row['email'], row['password'], row['tenant'])
        with allure.step("Verify dashboard and logout"):
            validations = self.my_events_page.validate_successful_login(row['tenant'])
            for validation in validations:
                assert "not" not in validation.lower(), f"Validation failed: {validation}"
            self.logout_page.logout()

    # LG_TC_2: Ensure a user cannot log in with invalid email for US tenant
    @pytest.mark.testcase_id("LG_TC_2")
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_with_invalid_email(self):
        print("test_login_with_invalid_email")
        self.navigator.navigate_to_login()

        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        self.login_page.login("invalid-email","password123",stop_after_email=True)
        error_message = self.login_page.is_error_msg_displayed(self.login_message['invalid_username'])
        self.logger.info(f"checking for error message: {error_message}")
        assert error_message, "Validation error should be displayed for invalid email format"
        assert self.login_page.is_login_page_displayed(), "Should remain on login page after failed login"

    # LG_TC_3: Ensure a user cannot log in with invalid password for US tenant

    @pytest.mark.testcase_id("LG_TC_3")
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_with_invalid_password(self):
        print("test_login_with_invalid_password")
        self.navigator.navigate_to_login()

        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        self.login_page.login("nivash@abovecloud9.ai", "wrongpassword",stop_after_password=True)
        error_message = (
                self.login_page.is_error_msg_displayed(self.login_message['incorrect_username_or_password'])
                )
        assert error_message, "Error message should be displayed for invalid password"
        assert self.login_page.is_login_page_displayed(), "Should remain on login page after failed login"

 
    # LG_TC_4: Ensure a user cannot log in with empty email fields

    @pytest.mark.testcase_id("LG_TC_4")
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_with_empty_email(self):
        print("test_login_with_empty_email")
        self.navigator.navigate_to_login()

        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        self.login_page.login("","password",stop_after_email=True)
        error_message = self.login_page.is_error_msg_displayed(self.login_message['empty_email_msg'])
        assert error_message, "Validation error should be displayed for empty email"
        assert self.login_page.is_login_page_displayed(), "Should remain on login page after failed login"

    # LG_TC_4: Ensure a user cannot log in with empty password fields

    @pytest.mark.testcase_id("LG_TC_4")
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_with_empty_password(self):
        print("test_login_with_empty_password")
        self.navigator.navigate_to_login()

        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        self.login_page.login("nivash@abovecloud9.ai","",stop_after_password=True)
        error_message = self.login_page.is_error_msg_displayed(self.login_message['empty_pass_msg'])
        assert error_message, "Validation error should be displayed for empty password"
        assert self.login_page.is_login_page_displayed(), "Should remain on login page after failed login"

    # LG_TC_25: Verify that all essential login form elements are properly displayed on the welcome page

    @pytest.mark.testcase_id("LG_TC_25")
    @pytest.mark.login
    def test_welcome_page_elements_visibility(self):
        print("test_welcome_page_elements_visibility")
        self.navigator.navigate_to_login()
        assert self.login_page.is_email_field_displayed(), "Email field not displayed"
        assert self.login_page.is_continue_btn_displayed(), "Continue button not displayed"

    # LG_TC_26: Verify that all essential login form elements are properly displayed on the login page

    @pytest.mark.testcase_id("LG_TC_26")
    @pytest.mark.login
    def test_login_page_elements_visibility(self):
        print("test_login_page_elements_visibility")
        self.navigator.navigate_to_login()
        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        self.login_page.login("nivash@abovecloud9.ai","",stop_after_email=True)
        validations = self.login_page.validate_login_page_elements()
        for validation in validations:
            assert "not visible" not in validation.lower(), f"Element validation failed: {validation}"



    # LG_TC_28: Validate the system's ability to handle multiple consecutive login attempts with invalid username

    @pytest.mark.testcase_id("LG_TC_28")
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_retry_functionality_invalid_username(self):
        print("test_login_retry_functionality")
        self.navigator.navigate_to_login()

        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        for i in range(5):
            self.login_page.login(f"invalid{i}@example.com", "",stop_after_email=True)
            error_message = self.login_page.is_error_msg_displayed(self.login_message['invalid_username'])
            assert error_message, "Login error should be displayed"
            assert self.login_page.is_login_page_displayed(), "Should be back on login page after retry"

    
    # LG_TC_28: Validate the system's ability to handle multiple consecutive login attempts with invalid password

    @pytest.mark.testcase_id("LG_TC_28")
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_retry_functionality_invalid_password(self):
        print("test_login_retry_functionality")
        self.navigator.navigate_to_login()

        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        self.login_page.enter_email("nivash@abovecloud9.ai")
        self.login_page.click_element(self.login_page.locator["continue"])
        for i in range(3):
            self.login_page.enter_password(f"invalidpassword{i}")
            self.login_page.click_signin_button()
            error_message = self.login_page.is_error_msg_displayed(self.login_message['incorrect_username_or_password'])
            assert error_message, "Error message should be displayed for invalid password"
            assert self.login_page.is_login_page_displayed(), "Should be back on login page after retry"

    # LG_TC_29: Verify protection against SQL injection attacks by testing various malicious SQL payloads in login fields

    @pytest.mark.testcase_id("LG_TC_29")
    @pytest.mark.security
    @pytest.mark.login
    def test_sql_injection_attempt(self):
        print("test_sql_injection_attempt")
        """Test SQL injection protection"""
        self.navigator.navigate_to_login()
        
        sql_injection_inputs = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'/*",
            "' OR 1=1 --"
        ]
        
        for malicious_input in sql_injection_inputs:
            self.login_page.enter_email(malicious_input)
            self.login_page.click_element(self.login_page.locator["continue"])
            error_displayed = self.login_page.is_error_msg_displayed(self.login_message['invalid_username'])
            assert error_displayed, f"SQL injection attempt should be blocked: {malicious_input}"
            assert self.login_page.is_login_page_displayed(), "Should remain on login page"

    # LG_TC_30: Validate cross-site scripting (XSS) attack prevention by testing XSS payloads in email input field

    @pytest.mark.testcase_id("LG_TC_30")
    @pytest.mark.security
    @pytest.mark.login 
    def test_xss_protection(self):
        print("test_xss_protection")
        """Test XSS attack protection"""
        self.navigator.navigate_to_login()
        
        xss_payloads = [
            "<script>alert('xss')</script>@test.com",
            "javascript:alert('xss')@test.com",
            "<img src=x onerror=alert('xss')>@test.com"
        ]
        
        for payload in xss_payloads:
            self.login_page.enter_email(payload)
            self.login_page.click_element(self.login_page.locator["continue"])
            error_displayed = (
                self.login_page.is_error_msg_displayed(self.login_message['invalid_username'])
            )
            assert error_displayed, f"XSS payload should be blocked: {payload}"
            assert self.login_page.is_login_page_displayed(), "Should remain on login page"


    # LG_TC_38: Validate that form field values persist appropriately after login errors and failed authentication attempts

    @pytest.mark.testcase_id("LG_TC_38")
    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.field_persistence
    def test_username_field_persistence(self):
        """Test if field values persist after login error"""
        print("test_field_persistence")
        self.navigator.navigate_to_login()
        
        test_email = f"invalid{TestConfig.TEST_EMAIL}"
        
        # Enter credentials and submit (this will cause an error)
        self.login_page.login(test_email,"",stop_after_email=True)
        
        # Verify error is displayed
        error_displayed = (self.login_page.is_error_msg_displayed(self.login_message['invalid_username']))
        assert error_displayed, "Error should be displayed"
        assert self.login_page.is_login_page_displayed(), "Should remain on login page"

        persisted_email = self.login_page.get_email_value()
        
        assert persisted_email == test_email, f"Email should persist after error. Expected: '{test_email}', Got: '{persisted_email}'"
        print(f"Email field persisted: '{persisted_email}'")

    # LG_TC_39: Validate that password field values persist appropriately after login errors and failed authentication attempts

    @pytest.mark.testcase_id("LG_TC_39")
    @pytest.mark.regression
    @pytest.mark.login
    def test_password_field_persistence(self):
        """Test if password field values persist after login error"""
        print("test_password_field_persistence")
        self.navigator.navigate_to_login()
        test_password = f"invalid{TestConfig.TEST_PASSWORD}"
        self.login_page.login(TestConfig.TEST_EMAIL,test_password,stop_after_password=True)
        error_displayed = (self.login_page.is_error_msg_displayed(self.login_message['incorrect_username_or_password']))
        assert error_displayed, "Error should be displayed"
        assert self.login_page.is_login_page_displayed(), "Should remain on login page"

        persisted_password = self.login_page.get_password_value()
        
        assert persisted_password == test_password, f"Email should persist after error. Expected: '{test_password}', Got: '{persisted_password}'"
        print(f"Email field persisted: '{persisted_password}'")


    @pytest.mark.validation
    @pytest.mark.regression
    @pytest.mark.testcase_id("LG_TC_43")
    def test_event_page_elements_displayed(self):
        self.navigator.navigate_to_login()
        self.login_page.login(TestConfig.TEST_EMAIL, TestConfig.TEST_PASSWORD, "US")
        assert self.my_events_page.check_event_page_elements("US"), "Event page elements are not displayed"


    # # LG_TC_40: Test forgot password functionality
    
    # @pytest.mark.testcase_id("LG_TC_40")
    # @pytest.mark.business_logic
    # @pytest.mark.login  
    # def test_forgot_password_link(self):
    #     """Test forgot password functionality"""
    #     print("test_forgot_password_link")
    #     self.navigator.navigate_to_login()
    #     forgot_password_displayed = self.login_page.is_displayed(self.login_page.locator['forgot_password_button'])        
    #     if forgot_password_displayed:
    #         self.login_page.click_element(self.login_page.locator['forgot_password_button'])


    # LG_TC_34: Validate email field handling with different length boundaries including empty, short, long local parts, and maximum length emails

    # @pytest.mark.testcase_id("LG_TC_34")
    # @pytest.mark.boundary
    # @pytest.mark.login
    # @pytest.mark.email_length_boundaries
    # def test_email_length_boundaries(self):
    #     """Test email length edge cases"""
    #     print("test_email_length_boundaries")
    #     self.navigator.navigate_to_login()
        
    #     long_local = "a" * 64 + "@example.com"      # Max local part
    #     long_domain = "test@" + "a" * 60 + ".com"   # Long domain
    #     max_email = "a" * 50 + "@" + "b" * 50 + ".com"  # Very long email
        
    #     boundary_emails = [
    #         "",                    # Empty
    #         "a@b.co",              # Short valid
    #         long_local,            # Long local part
    #         long_domain,           # Long domain
    #         max_email              # Maximum length
    #     ]
        
    #     for email in boundary_emails:
    #         self.login_page.clear_login_fields()
    #         self.login_page.login(email, TestConfig.TEST_PASSWORD)
            
    #         if len(email) == 0:
    #             error_displayed = self.login_page.is_error_msg_displayed(self.login_message['empty_email_msg'])
    #             assert error_displayed, "Empty email should show validation error"
            
    #         assert self.login_page.is_login_page_displayed(), "Should remain on login page"


     # LG_TC_33: Test password field validation with various length boundaries including empty, minimum, maximum, and extremely long passwords

    # @pytest.mark.testcase_id("LG_TC_33")
    # @pytest.mark.boundary
    # @pytest.mark.login
    # def test_password_length_boundaries(self):
    #     print("test_password_length_boundaries")
    #     """Test password length edge cases"""
    #     self.navigator.navigate_to_login()
    #     test_email = TestConfig.TEST_EMAIL
        
    #     boundary_passwords = [
    #         "",                    # Empty
    #         "1",                   # Too short (1 char)
    #         "12345",               # Boundary (5 chars)
    #         "123456",              # Minimum valid (6 chars)
    #         "a" * 100,             # Very long
    #         "a" * 1000             # Extremely long
    #     ]
        
    #     for password in boundary_passwords:
    #         self.login_page.clear_login_fields()
    #         self.login_page.login(test_email, password)
            
    #         if len(password) == 0:
    #             error_displayed = self.login_page.is_error_msg_displayed(self.login_message['empty_pass_msg'])
    #             assert error_displayed, "Empty password should show validation error"
    #         elif len(password) < 6:
    #             error_displayed = self.login_page.is_error_msg_displayed(self.login_message['valid_pass_msg'])
    #             assert error_displayed, f"Short password ({len(password)} chars) should show validation error"
            
    #         assert self.login_page.is_login_page_displayed(), "Should remain on login page"

  
    # LG_TC_3: Ensure a user cannot log in with invalid credentials for US tenant

    # @pytest.mark.testcase_id("LG_TC_3")
    # @pytest.mark.data_driven_with_status
    # @pytest.mark.login
    # def test_invalid_credentials_with_status(self):
        # print("test_invalid_credentials_with_status")
        # from time import sleep
        # import pandas as pd
        
        # input_login_csv = self.invalid_credentials_csv
        # output_login_csv = 'data/invalid_credentials_output.csv'        
        # data_login = read_input_data(input_login_csv)
        # self.navigator.navigate_to_login()
        
        # if 'status' not in data_login.columns:
        #     data_login['status'] = ''
        
        # for index, row in data_login.iterrows():
        #     try:
        #         print(f"Starting Login for: {row['email']}")
        #         assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        #         self.login_page.login(row['email'], row['password'])
        #         sleep(3) 
                
        #         if (self.login_page.is_error_msg_displayed(self.login_message['incorrect_username_or_password']) or
        #             self.login_page.is_error_msg_displayed(self.login_message['invalid_email_or_password']) or
        #             self.login_page.is_error_msg_displayed(self.login_message['invalid_credentials']) or
        #             self.login_page.is_error_msg_displayed(self.login_message['error_occurred'])):
        #             status = "Login Failed - Expected error displayed"
        #             print(f"Expected login failure for: {row['email']}")
        #         elif self.my_events_page.validate_successful_login():
        #             status = "Login Successful - Unexpected success"
        #             print(f"Unexpected login success for: {row['email']}")
                    
        #             print("Logout of session")
        #             self.logout_page.logout()
        #             sleep(2)
        #         else:
        #             status = "Login Failed - No clear status"
        #             print(f"Unclear login status for: {row['email']}")
                    
        #     except Exception as e:
        #         print(f"Error during login for {row['email']}: {e}")
        #         status = f"Login Error: {str(e)}"
                
        #     data_login.at[index, 'status'] = status
        
        # write_output_data(output_login_csv, data_login)
        # print(f"Invalid credentials test completed. Results saved to {output_login_csv}")