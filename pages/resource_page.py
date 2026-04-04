import json
import time
import pandas as pd
import allure
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from appium.webdriver.webdriver import WebDriver
from constants.locator.address_locator import AddressLocator
from constants.locator.course_create_locator import CourseCreateLocator
from constants.tenant_config import TenantConfig, TenantConfiguration
from pages.base_page import BasePage
from pages.course_create_page import CourseCreatePage
from pages.my_events_page import MyEventsPage
from utils.time_zone_util import TimezoneFormatter
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig


class ResourcePage(BasePage):
    """
    Page object for Course Creation page.
    
    Uses TenantConfig for all tenant-specific logic to ensure consistency
    and maintainability. All field labels and feature flags are centralized.
    """

    def __init__(self, driver: WebDriver, platform: str):
        super().__init__(driver, platform)
        self.locator = AddressLocator.get_locators(platform)
        from constants.message.address_message import AddressMessage
        self.course_create = CourseCreatePage(driver, platform)
        self.address_message = AddressMessage.get_message()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        
   