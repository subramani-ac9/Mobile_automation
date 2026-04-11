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
from constants.locator.resource_locator import ResourceLocator
from constants.tenant_config import TenantConfig, TenantConfiguration
from pages.base_page import BasePage
from pages.course_create_page import CourseCreatePage
from pages.my_events_page import MyEventsPage
from utils.time_zone_util import TimezoneFormatter
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig


class ResourcePage(BasePage):

    def __init__(self, driver: WebDriver, platform: str):
        super().__init__(driver, platform)
        self.locator = ResourceLocator.get_locators(platform)
        self.course_create = CourseCreatePage(driver, platform)
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    
        # ✅ Wait for authentication screen
    def is_authentication_screen_displayed(self):
        try:
           if self.is_displayed(self.locator["title"],20):
            self.logger.info("Authentication screen displayed")
            return True
        except:
            self.logger.info("Authentication screen not displayed")
            return False

    # ✅ Enter PIN
    def enter_pin(self, pin: str):
        try:
            if self.is_displayed(self.locator["pin_field"]):
                pin_field = self.find_element(self.locator["pin_field"])
                pin_field.clear()
                self.send_keys(pin_field, pin)
                self.logger.info("PIN entered")
            else:
                self.logger.info("PIN field not displayed")
                raise Exception("PIN field not displayed")
        except:
            self.logger.info("PIN field not displayed")
            raise Exception("PIN field not displayed")

    # ✅ Click Continue
    def click_continue(self):
        with allure.step("Click Continue"):
            try:
                if self.is_displayed(self.locator["continue_button"]):
                    continue_btn = self.find_element(self.locator["continue_button"])
                    continue_btn.click()
                    self.logger.info("Clicked Continue")
            except:
                self.logger.info("Continue button not displayed , automatically clicking continue button and moving forward")
                raise Exception("Continue button not displayed")

    # ✅ Click Cancel
    def click_cancel(self):
        with allure.step("Click Cancel"):
            try:
                if self.is_displayed(self.locator["cancel_button"]):
                    cancel_btn = self.find_element(self.locator["cancel_button"])
                    cancel_btn.click()
                    self.logger.info("Clicked Cancel")
            except:
                self.logger.info("Cancel button not displayed")
                raise Exception("Cancel button not displayed")

    # ✅ Check Continue enabled
    def is_continue_enabled(self):
        return self.is_element_clickable(self.locator["continue_button"])

    # ✅ Main method (IMPORTANT)
    def handle_authentication_if_present(self, pin: str):
        with allure.step("Handle authentication if present"):
            if self.is_authentication_screen_displayed():   
                self.enter_pin(pin)
                self.click_continue()
                self.logger.info("Authentication handled successfully")
                return True
            else:
                self.logger.info("Authentication screen not displayed")
                return False

    def is_resources_page_displayed(self):
        return self.is_displayed(self.locator["resources_template"])

    def click_resource_product_card(self, productName: str):
        self.logger.info(f"Clicking resource product card: {productName}")
        try:
            resource_product_card = self.build_locator(self.locator["resource_product_card"], productName)
            self.scroll_to_element_by_touch(resource_product_card)
            self.click_element(resource_product_card)
            self.logger.info(f"Resource product card clicked: {productName}")
        except:
            self.logger.error(f"Failed to click resource product card: {productName}")
            raise Exception(f"Failed to click resource product card: {productName}")


    def click_resource_download_button(self,type: str, resourceName: str):
        self.logger.info(f"Clicking resource download {type}: {resourceName}")
        try:
            resource_download_button = self.build_locator(self.locator[f"resource_download_{type}"], resourceName)
            self.scroll_to_element_by_touch(resource_download_button)
            self.click_element(resource_download_button)
            self.logger.info(f"Resource download {type} clicked: {resourceName}")
        except:
            self.logger.error(f"Failed to click resource download {type}: {resourceName}")
            raise Exception(f"Failed to click resource download {type}: {resourceName}")

    def click_resource_delete_button(self, type: str, resourceName: str):
        self.logger.info(f"Clicking resource delete {type}: {resourceName}")
        try:
            resource_delete_button = self.build_locator(self.locator[f"resource_delete_{type}"], resourceName)
            self.scroll_to_element_by_touch(resource_delete_button)
            self.click_element(resource_delete_button)
            self.logger.info(f"Resource delete {type} clicked: {resourceName}")
        except:
            self.logger.error(f"Failed to click resource delete {type}: {resourceName}")
            raise Exception(f"Failed to click resource delete {type}: {resourceName}")

    def click_resource_pause_download_button(self, type: str, resourceName: str):
        self.logger.info(f"Clicking resource pause download {type}: {resourceName}")
        try:
            resource_pause_download_button = self.build_locator(self.locator[f"resourse_pause_download_{type}"], resourceName)
            self.scroll_to_element_by_touch(resource_pause_download_button)
            self.click_element(resource_pause_download_button)
            self.logger.info(f"Resource pause download {type} clicked: {resourceName}")
        except:
            self.logger.error(f"Failed to click resource pause download {type}: {resourceName}")
            raise Exception(f"Failed to click resource pause download {type}: {resourceName}")
        
    def isDeleteButtonDisplayed(self, type: str, resourceName: str):
        self.logger.info(f"Checking if delete button is displayed for {type}: {resourceName}")
        try:
            delete_button = self.build_locator(self.locator[f"resource_delete_{type}"], resourceName)
            return self.is_displayed(delete_button,120)
        except:
            self.logger.error(f"Failed to check if delete button is displayed for {type}: {resourceName}")
            raise Exception(f"Failed to check if delete button is displayed for {type}: {resourceName}")

    def isPauseDownloadButtonDisplayed(self, type: str, resourceName: str):
        self.logger.info(f"Checking if pause download button is displayed for {type}: {resourceName}")
        try:
            pause_download_button = self.build_locator(self.locator[f"resourse_pause_download_{type}"], resourceName)
            return self.is_displayed(pause_download_button)
        except:
            self.logger.error(f"Failed to check if pause download button is displayed for {type}: {resourceName}")
            raise Exception(f"Failed to check if pause download button is displayed for {type}: {resourceName}")

    def isDownloadButtonDisplayed(self, type: str, resourceName: str):
        self.logger.info(f"Checking if download button is displayed for {type}: {resourceName}")
        try:
            download_button = self.build_locator(self.locator[f"resource_download_{type}"], resourceName)
            return self.is_displayed(download_button,20)
        except:
            self.logger.error(f"Failed to check if download button is displayed for {type}: {resourceName}")
            raise Exception(f"Failed to check if download button is displayed for {type}: {resourceName}")

    def click_resourse_card(self,type: str, resourceName: str):
        self.logger.info(f"Clicking resource card: {resourceName}")
        try:
            resource_card = self.build_locator(self.locator["resource_list"], resourceName)
            self.scroll_to_element_by_touch(resource_card)
            if self.isDeleteButtonDisplayed(type, resourceName):
                self.click_element(resource_card)
                self.logger.info(f"Resource card clicked: {resourceName}")
            else:
                self.logger.error(f"resource is not downloaded yet to click resource card: {resourceName}")
                raise Exception(f"resource is not downloaded yet to click resource card: {resourceName}")
        except:
            self.logger.error(f"Failed to click resource card: {resourceName}")

    def isResourceTitleDisplayed(self, resourceName: str):
        self.logger.info(f"Checking if resource title is displayed: {resourceName}")
        try:
            resource_title = self.build_locator(self.locator["resourse_title"], resourceName)
            return self.is_displayed(resource_title)
        except:
            self.logger.error(f"Failed to check if resource title is displayed: {resourceName}")
            raise Exception(f"Failed to check if resource title is displayed: {resourceName}")

    def isResourceBackButtonDisplayed(self):
        self.logger.info(f"Checking if resource back button is displayed")
        try:
            return self.is_displayed(self.locator["back_button"])
        except:
            self.logger.error(f"Failed to check if resource back button is displayed")
            raise Exception(f"Failed to check if resource back button is displayed")

    def isResourceRewindButtonDisplayed(self):
        self.logger.info(f"Checking if resource rewind button is displayed")
        try:
            return self.is_displayed(self.locator["rewind_button"])
        except:
            self.logger.error(f"Failed to check if resource rewind button is displayed")
            raise Exception(f"Failed to check if resource rewind button is displayed")

    def isResourceForwardButtonDisplayed(self):
        self.logger.info(f"Checking if resource forward button is displayed")
        try:
            return self.is_displayed(self.locator["forward_button"])
        except:
            self.logger.error(f"Failed to check if resource forward button is displayed")
            raise Exception(f"Failed to check if resource forward button is displayed")

    def isResourcePlayButtonDisplayed(self):
        self.logger.info(f"Checking if resource play button is displayed")
        try:
            return self.is_displayed(self.locator["play_button"])
        except:
            self.logger.error(f"Failed to check if resource play button is displayed")
            raise Exception(f"Failed to check if resource play button is displayed")

    def isResourcePauseButtonDisplayed(self):
        self.logger.info(f"Checking if resource pause button is displayed")
        try:
            if self.isResourcePlayButtonDisplayed():
                self.click_element(self.locator["play_button"])
            return self.is_displayed(self.locator["pause_button"])
        except:
            self.logger.error(f"Failed to check if resource pause button is displayed")
            raise Exception(f"Failed to check if resource pause button is displayed")

    def isResourceVolumeUpButtonDisplayed(self):
        self.logger.info(f"Checking if resource volume up button is displayed")
        try:
            return self.is_displayed(self.locator["volume_up_button"])
        except:
            self.logger.error(f"Failed to check if resource volume up button is displayed")
            raise Exception(f"Failed to check if resource volume up button is displayed")
            
    def isResourceVolumeDownButtonDisplayed(self):
        self.logger.info(f"Checking if resource volume down button is displayed")
        try:
            return self.is_displayed(self.locator["volume_down_button"])
        except:
            self.logger.error(f"Failed to check if resource volume down button is displayed")
            raise Exception(f"Failed to check if resource volume down button is displayed")
            
            
    def isResourceAudioOutputButtonDisplayed(self):
        self.logger.info(f"Checking if resource audio output button is displayed")
        try:
            return self.is_displayed(self.locator["audio_output_button"])
        except:
            self.logger.error(f"Failed to check if resource audio output button is displayed")
            raise Exception(f"Failed to check if resource audio output button is displayed")
            
    def isAllElementsDispalyed(self, resourceName: str):
        self.logger.info(f"Checking if all elements are displayed in resource playing page")
        return self.isResourceTitleDisplayed(resourceName) and self.isResourceBackButtonDisplayed() and self.isResourceRewindButtonDisplayed() and self.isResourceForwardButtonDisplayed() and self.isResourcePlayButtonDisplayed() and self.isResourcePauseButtonDisplayed()  and self.isResourceVolumeUpButtonDisplayed() and self.isResourceVolumeDownButtonDisplayed() and self.isResourceAudioOutputButtonDisplayed()
