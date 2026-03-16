from pages.login_page import LoginPage
from pages.onboard_page import OnBoardPage
from pages.my_events_page import MyEventsPage
from pages.meetup_create_page import MeetupCreatePage
from constants.locator.login_locator import LoginLocator
from constants.locator.onboard_locator import OnBoardLocator
from constants.locator.myevent_locator import MyEventLocator
from constants.locator.logout_locator import LogoutLocator
from pages.logout_page import LogoutPage
from pages.my_events_page import MyEventsPage
from constants.locator.course_create_locator import CourseCreateLocator
from pages.course_create_page import CourseCreatePage
from config.config import TestConfig
import logging

class Navigator:
    def __init__(self, driver, platform: str):
        self.driver = driver
        self.platform = platform
        self.logger = logging.getLogger(self.__class__.__name__)

    def is_user_logged_in(self):
        """Check if user is currently logged in by verifying MyEvents page elements"""
        self.logger.debug("Checking if user is already logged in")
        my_events_page = MyEventsPage(self.driver, self.platform)
        is_logged_in = my_events_page.is_dashboard_displayed() or my_events_page.is_bottom_navigation_displayed()
        self.logger.info(f"User login status: {'logged in' if is_logged_in else 'not logged in'}")
        return is_logged_in

    def navigate_to_login(self):
        self.locator = OnBoardLocator.get_locators(self.platform)
        onboard_page = OnBoardPage(self.driver, self.platform)
        if onboard_page.is_continue_btn_displayed():
            onboard_page.click_continue_button()

    def navigate_to_meetup_create_page(self, email, password, tenant=None):
        self.navigate_to_my_events_page(email, password, tenant)
        self.locator = MyEventLocator.get_locators(self.platform)
        my_events_page = MyEventsPage(self.driver, self.platform)
        my_events_page.click_add_event_button()
        my_events_page.select_create_event_button('Meetup')

    def navigate_to_my_events_page(self, email, password, tenant=None):
        self.navigate_to_login()
        
        from pages.my_events_page import MyEventsPage
        my_events_page = MyEventsPage(self.driver, self.platform)
        from pages.login_page import LoginPage
        login_page = LoginPage(self.driver, self.platform)
        
        # Use default tenant from config if not specified
        if tenant is None:
            tenant = 'us'
            
        try:
            self.logger.debug("Checking if login page is displayed")
            if login_page.is_login_page_displayed():
                self.logger.info("Login page detected - proceeding with login")
                status = login_page.login(email, password, tenant)
                
                if "Successful" in status:
                    my_events_page.wait_for_dashboard_to_load(timeout=60)
                
                return status
            else:
                self.logger.debug("Login page not detected - checking if already logged in")
                
        except Exception as e:
            self.logger.warning(f"Could not determine if on login page: {e} - falling back to logged-in check")
        
        if self.is_user_logged_in():
            self.logger.info("User already logged in - skipping login process")
            return "Login - Already logged in"
        
        self.logger.error("Unexpected state: Not on login page and not logged in")
        return "Login Failure - Unexpected state" 

    def navigate_to_course_create_page(self, email, password, tenant=None):
        self.logger.info("Navigating to course creation page")
        self.navigate_to_my_events_page(email, password, tenant)
        self.locator = MyEventLocator.get_locators(self.platform)
        my_events_page = MyEventsPage(self.driver, self.platform)
        self.logger.info("Clicking add event button")
        my_events_page.click_add_event_button()
        if(tenant.lower() == 'us'):
            self.logger.debug("Selecting course creation option")
            my_events_page.select_create_event_button('Course')
            self.logger.info("Successfully navigated to course creation page")

    
    def navigate_to_course_create_from_dashboard(self):
        self.locator = MyEventLocator.get_locators(self.platform)
        my_events_page = MyEventsPage(self.driver, self.platform)
        
        # Verify user is logged in and on dashboard before proceeding
        if not self.is_user_logged_in():
            my_events_page.logger.error("User not logged in or not on dashboard - cannot navigate from dashboard")
            raise Exception("Navigation failed: User must be logged in and on dashboard to use this method")
            
        my_events_page.navigate_to_events()
        my_events_page.click_add_event_button()
        my_events_page.select_create_event_button('Course')
    
    def navigate_to_meetup_create_from_dashboard(self):
        self.locator = MyEventLocator.get_locators(self.platform)
        my_events_page = MyEventsPage(self.driver, self.platform)
        
        # Verify user is logged in and on dashboard before proceeding
        if not self.is_user_logged_in():
            my_events_page.logger.error("User not logged in or not on dashboard - cannot navigate from dashboard")
            raise Exception("Navigation failed: User must be logged in and on dashboard to use this method")
            
        my_events_page.navigate_to_events()
        my_events_page.click_add_event_button()
        my_events_page.select_create_event_button('Meetup')

    def navigate_to_logout(self):
        self.locator = LogoutLocator.get_locators(self.platform)
        logout_page = LogoutPage(self.driver, self.platform)
        logout_page.logout()

        


