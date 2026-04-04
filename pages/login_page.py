import time
import allure
from constants.locator.login_locator import LoginLocator
from constants.locator.myevent_locator import MyEventLocator
from pages.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from utils.logger_config import LoggerConfig


class LoginPage(BasePage):

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = LoginLocator.get_locators(platform)
        # Initialize message attribute
        from constants.message.login_message import LoginMessage
        self.login_message = LoginMessage.get_message()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    @allure.step("Select tenant/country: {tenant_name}")
    def select_country_tenant(self, tenant_name):
        """
        Select a specific tenant/country from the dropdown
        
        Args:
            tenant_name: Name of the tenant (e.g., "[DND] The Art of Living Foundation (US)")
        """
        try:
            self.logger.info(f"Selecting tenant: {tenant_name}")
            
            # Click on country/tenant dropdown field
            if self.is_displayed(self.locator["country_field"]):
                self.click_element(self.locator["country_field"])
                self.logger.debug("Clicked on country dropdown field")
            else:
                self.logger.warning("Country dropdown field not found, trying alternative locator")
                self.click_element(self.locator["country_dropdown"])
            
            time.sleep(2)  # Wait for dropdown to open
            
            # Try to search for tenant if search field is available
            if self.is_displayed(self.locator.get("search_tenant"), timeout=3):
                self.logger.debug("Search field found, using search to find tenant")
                search_field = self.locator["search_tenant"]
                self.send_keys(search_field, tenant_name.split(']')[0] + ']' if ']' in tenant_name else tenant_name)
                time.sleep(1)
            
            # Select the tenant from dropdown
            tenant_locator = self.build_locator(self.locator["tenant_option"], tenant_name)
            
            # Try exact match first
            if self.is_displayed(tenant_locator, timeout=5):
                self.click_element(tenant_locator)
                self.logger.info(f"Successfully selected tenant: {tenant_name}")
            else:
                # If exact match not found, try partial match
                self.logger.debug(f"Exact match not found, trying partial match for: {tenant_name}")
                
                # Extract key parts for partial matching
                if "Foundation" in tenant_name:
                    partial_name = tenant_name.split("Foundation")[0] + "Foundation"
                    partial_locator = self.build_locator(self.locator["tenant_option"], partial_name)
                    
                    if self.is_displayed(partial_locator, timeout=3):
                        self.click_element(partial_locator)
                        self.logger.info(f"Successfully selected tenant using partial match: {partial_name}")
                    else:
                        raise Exception(f"Could not find tenant option: {tenant_name}")
                else:
                    raise Exception(f"Could not find tenant option: {tenant_name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to select tenant {tenant_name}: {e}")
            raise Exception(f"Unable to select tenant: {tenant_name}")

    @allure.step("Scroll to Sign In button")
    def scroll_to_signin(self, max_scrolls=10):
        """
        Scroll the screen container until the 'Log In' button is visible.
        """
        self.logger.info("Scrolling to 'Log In' button...")

        # Hide keyboard if visible
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass

        # Wait for scrollable container
        container = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.locator["screen"])
        )

        target = None
        for i in range(max_scrolls):
            try:
                target = self.driver.find_element(*self.locator["signin"])
                if target.is_displayed():
                    self.logger.info("'Log In' button is visible on screen.")
                    break
            except:
                # Scroll down inside the container
                self.driver.execute_script("mobile: scrollGesture", {
                    'elementId': container.id,
                    'direction': 'down',
                    'percent': 0.6  # scroll ~60% of container
                })
                self.logger.info(f"Scroll attempt {i+1}: scrolling down...")

        if target is None or not target.is_displayed():
            raise Exception("Failed to find 'Log In' button after scrolling!")

        return target

    def is_country_dropdown_displayed(self):
        """Check if country/tenant dropdown is displayed"""
        return self.is_displayed(self.locator["country_field"]) or self.is_displayed(self.locator["country_dropdown"])

    def get_current_tenant(self):
        """Get the currently selected tenant from the dropdown"""
        try:
            if self.is_displayed(self.locator["country_field"]):
                return self.get_element_text(self.locator["country_field"])
            return None
        except Exception as e:
            self.logger.error(f"Error getting current tenant: {e}")
            return None

    @allure.step("Verify login page is displayed")
    def is_login_page_displayed(self):
        return self.is_displayed(self.locator['login_screen'])

    @allure.step("Enter email: {email}")
    def enter_email(self, email):
        self.logger.info(f"Entering email: {email}")
        time.sleep(3)
        self.click_element(self.locator["email"])
        self.send_keys(self.locator["email"], email)
        self.logger.info("Email entered successfully")

    @allure.step("Enter password")
    def enter_password(self, password):
        self.logger.info("Entering password")
        self.click_element(self.locator["password"])

        self.logger.info("Scrolling password field into view")
       # Scroll to the password field
        self.scroll_to_signin()
        self.send_keys(self.locator["password"], password)
        self.logger.info("Password entered successfully")

    @allure.step("Tap Sign In button")
    def click_signin_button(self):
        self.logger.info("Clicking sign in button")
        self.click_element(self.locator["signin"])
        self.logger.info("Sign in button clicked")

    def is_continue_btn_displayed(self):
        return self.is_displayed(self.locator["continue"])


    def is_signin_btn_displayed(self):
        return self.is_displayed(self.locator["signin"])

    def is_email_field_displayed(self):
        return self.is_displayed(self.locator["email"])

    def is_password_field_displayed(self):
        return self.is_displayed(self.locator["password"])

    def is_forgetPassword_button_displayed(self):
        return self.is_displayed(self.locator["forgot_password_button"])

    def is_error_msg_displayed(self, err_msg):
        try:
            error_element = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_element_located(
                    (AppiumBy.XPATH, f"//android.view.View[contains(@content-desc,'{err_msg}')]")
                )
            )
            return error_element.is_displayed()
        except Exception:
            return False
        
    @allure.step("Validate login page elements")
    def validate_login_page_elements(self):
        validations = []
        elements_to_check = [
            (self.locator['screen'], "Login screen"),
            (self.locator['email_display'], "Email field in view mode"), 
            (self.locator['password'], "Password field"),
            (self.locator['forgot_password_button'], "Forgot password button"),
            (self.locator['create_account_button'], "Create account button"),
            (self.locator['contact_support_button'], "Contact support button")
            ]
        
        for key, description in elements_to_check:
            if self.is_displayed(key, 5):
                validations.append(f"{description} is visible")
            else:
                validations.append(f"{description} is not visible")
        
        return validations 
    
    def clear_login_fields(self):
        """Clear email and password fields"""
        try:
            email_element = self.find_element(self.locator["email"])
            email_element.clear()
            password_element = self.find_element(self.locator["password"])
            password_element.clear()
        except Exception as e:
            self.logger.error(f"Error clearing fields: {e}")

    def get_email_value(self):
        """Return current text/value in the email field"""
        return self.get_input_value(self.locator["email"]) or ""

    def get_password_value(self):
        """Return current text/value in the password field"""
        return self.get_input_value(self.locator["password"]) or ""
    
    def get_field_validation_message(self, field_type):
        """Get validation message for specific field"""
        try:
            if field_type == "email":
                return self.get_element_text(self.locator["email_validation"])
            elif field_type == "password":
                return self.get_element_text(self.locator["password_validation"])
        except:
            return None
        
    @allure.step("Login as user: {username}")
    def login(self, username, password, tenant=None, stop_after_email=False, stop_after_password=False):
        try:
            self.logger.info(f"Starting login process for user: {username}")
        
            self.enter_email(username)
            self.click_element(self.locator["continue"])

            if stop_after_email:
                self.logger.info("Stopping after username entered for email validation")
                return 

            # Enter password
            self.enter_password(password)

            self.click_signin_button()

            if stop_after_password:
                self.logger.info("Stopping after password entered for password validation")
                return 
            
            self.logger.info("Login button clicked, waiting for navigation to complete...")
            login_successful = self.wait_for_login_completion(timeout=60, tenant=tenant)

            if login_successful:
                self.logger.info("Login successful - navigated to MyEvents page")
                return "Login - Successful"
            else:
                self.logger.warning("Navigation to MyEvents failed, checking for error messages...")
                if self.is_error_msg_displayed(self.login_message['invalid_email_or_password']) or self.is_error_msg_displayed(self.login_message['incorrect_username_or_password']):
                    self.logger.error("Login failed - invalid credentials detected")
                    return "Login Failure - Incorrect username or password."
                else:
                    self.logger.error("Login failed - navigation timeout but no error message found")
                    return "Login Failure - Navigation timeout"

        except Exception as e:
            self.logger.error(f"Login failed with exception: {str(e)}")
            raise Exception(f"Login failed: {str(e)}")
    
    @allure.step("Wait for login completion (timeout: {timeout}s)")
    def wait_for_login_completion(self, timeout=60, tenant=None):
        """Wait for login to complete by checking for dashboard elements"""
        self.logger.info(f"Waiting for login completion (timeout: {timeout}s)")
        from pages.my_events_page import MyEventsPage
        my_events_page = MyEventsPage(self.driver, self.platform)
        my_events_page_locator = MyEventLocator.get_locators(self.platform)

        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                # Check if we're still on login page
                if self.is_login_page_displayed():
                    self.logger.debug("Still on login page, waiting...")
                    time.sleep(3)
                    continue

                # Check for Jai Gurudev! title
                if my_events_page.is_displayed(my_events_page_locator['Jai_Gurudev_title'], 20):
                    self.logger.info("Jai Gurudev! title detected, login successful")
                    return True

                # Check for bottom navigation as backup
                if my_events_page.is_bottom_navigation_displayed():
                    self.logger.info("Bottom navigation detected, login successful")
                    return True
                    
                self.logger.info("Waiting for dashboard to appear...")
                time.sleep(3)
                
            except Exception as e:
                self.logger.info(f"Exception while waiting for login completion: {e}")
                time.sleep(3)
        
        self.logger.warning(f"Login completion not detected after {timeout} seconds")
        return False

