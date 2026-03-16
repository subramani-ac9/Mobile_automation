import time
import allure
from constants.locator.logout_locator import LogoutLocator
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.onboard_page import OnBoardPage
from pages.my_events_page import MyEventsPage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LogoutPage(BasePage):

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = LogoutLocator.get_locators(platform)
        self.login_page = LoginPage(driver, platform)
        self.onboard_page = OnBoardPage(driver, platform)
        self.my_events_page = MyEventsPage(driver, platform)

    @allure.step("Verify logout page is displayed")
    def is_logout_page_displayed(self):
        return self.is_displayed(self.locator['logout'])

    @allure.step("Tap Logout button")
    def click_logout_button(self):
        self.click_element(self.locator['logout'])

    @allure.step("Verify confirm logout button is displayed")
    def is_confirm_logout_button_displayed(self):
        return self.is_displayed(self.locator['confirm_logout'])

    @allure.step("Tap Confirm Logout button")
    def click_confirm_logout_button(self):
        self.click_element(self.locator['confirm_logout'])

    @allure.step("Verify account icon is displayed")
    def is_account_icon_displayed(self):
        return self.is_displayed(self.locator['account_icon'])

    @allure.step("Open Account (tap account icon)")
    def click_account_icon(self):
        self.click_element(self.locator['account_icon'])

    @allure.step("Validate logout (login screen shown)")
    def validate_logout(self):
        if self.onboard_page.is_continue_btn_displayed():
            self.onboard_page.click_continue_button()  
        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
    
    def validate_logout_page_elements(self):
        validations = []
        elements_to_check = [
            (self.locator['logout'], "Logout button"),
            (self.locator['account_icon'], "Account icon")
        ]
        
        for locator, description in elements_to_check:
            if not self.is_displayed(locator):
                validations.append(f"{description} is not displayed")
        
        return validations
    
    def validate_logout_page(self):
        validations = self.validate_logout_page_elements()
        for validation in validations:
            assert "not" not in validation.lower(), f"Validation failed: {validation}"

    @allure.step("Logout from app")
    def logout(self):
        self.click_account_icon()
        assert self.is_logout_page_displayed(), "Logout page should be displayed"
        self.click_logout_button()
        if self.is_confirm_logout_button_displayed():
            self.click_confirm_logout_button()
            self.validate_logout()
        else:
            self.validate_logout()