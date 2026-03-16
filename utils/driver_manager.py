from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config import TestConfig
import logging
from appium.options.android import UiAutomator2Options


class DriverManager:    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
    
    def start_driver(self):
        try:
            appium_url = f"http://{TestConfig.APPIUM_HOST}:{TestConfig.APPIUM_PORT}"
            raw_caps = TestConfig.get_appium_capabilities()
            # print("raw_caps",raw_caps)
            if TestConfig.MOBILE_PLATFORM == 'android':
                options = UiAutomator2Options().load_capabilities(raw_caps)
            else:
                from appium.options.ios import XCUITestOptions
                options = XCUITestOptions().load_capabilities(raw_caps)

            self.driver = webdriver.Remote(
            command_executor=appium_url,
            options=options
            )

            self.driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, TestConfig.EXPLICIT_WAIT)
            
            self.logger.info("Appium driver initialized successfully")
            return self.driver

        except Exception as e:
            self.logger.error(f"Failed to initialize Appium driver: {str(e)}")
            raise
    
    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Appium driver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing driver: {str(e)}")

     