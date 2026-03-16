import allure
from constants.locator.onboard_locator import OnBoardLocator
from pages.base_page import BasePage

class OnBoardPage(BasePage):

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = OnBoardLocator.get_locators(platform)

    @allure.step("Tap Continue on onboarding")
    def click_continue_button(self):
        self.click_element(self.locator["continue_button"])

    @allure.step("Verify onboarding Continue button is displayed")
    def is_continue_btn_displayed(self):
        return self.is_displayed(self.locator["continue_button"])