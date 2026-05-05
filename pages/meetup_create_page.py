import time
from datetime import datetime
from typing import List
import pandas as pd
import logging
import allure
from constants.locator.meetup_create_locator import MeetupCreateLocator
from constants.message.meetup_create_message import MeetupCreateMsg
from pages.base_page import BasePage
from selenium.webdriver.support import expected_conditions as EC
from utils.time_zone_util import TimezoneFormatter
from pages.course_create_page import CourseCreatePage
class MeetupCreatePage(CourseCreatePage):

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = MeetupCreateLocator.get_locators(platform)
        self.meetup_msg = MeetupCreateMsg.get_meetup_create_message()
        self.logger = logging.getLogger(__name__)


    def parse_list(self,value: str) -> List[str]:
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]

    
    @allure.step("Select meetup mode: {value}")
    def select_meetup_mode(self, value):
        if not value:
            raise Exception(f"Meetup mode is not present on the given data")
        try:
            eventType = self.build_locator(self.locator["meetup_type"], value.capitalize())
            self.click_element(eventType)
        except Exception as e:
            self.logger.error(f"Exception while selecting the meetup_mode as {value}, exception:: {str(e)}")
            raise Exception(f"Unable to select EventMode as {value}")
        
    def select_meetup_product(self, value):
        if not value:
            raise Exception(f"Meetup product is not present on the given data")
        try:
            self.click_element(self.locator["select_meetup_txt_box"])
            time.sleep(1)
            # self.send_keys(self.locator["search"], value, is_necessary=False)
            product = self.build_locator(self.locator["item"], value)
            time.sleep(2)
            self.click_element(product)
        except Exception as e:
            self.logger.error(f"Exception while selecting meetup product as {value}, Exception:: {str(e)}")
            raise Exception(f"Unable to select MeetupProduct as {value}")
        
    def select_meetup_mode_and_product(self, mode, product):
        self.select_meetup_mode(mode)
        self.select_meetup_product(product)
    
    def is_private_checkbox_checked(self) -> bool:
        """
        Check if the private meetup checkbox is currently checked/enabled
        Returns True if checked, False if unchecked
        """
        try:
            self.logger.info("Checking private meetup checkbox status")
            checkbox_element = self.find_element(self.locator["is_private"], timeout=10)

            self.logger.info(f"Checkbox element found. Platform: {self.platform}")
            self.logger.info(f"Element tag name: {checkbox_element.tag_name}")
            
            all_attributes = {}
            try:
                attributes_to_check = ['value', 'checked', 'selected', 'enabled', 'clickable', 'focusable']
                for attr in attributes_to_check:
                    try:
                        val = checkbox_element.get_attribute(attr)
                        all_attributes[attr] = val
                        self.logger.info(f"Attribute '{attr}': {val}")
                    except:
                        pass
            except Exception as attr_e:
                self.logger.warning(f"Could not get attributes: {attr_e}")
            
            if self.platform.lower() == 'ios':
                # Try different iOS checkbox attributes (only valid ones)
                value_attr = checkbox_element.get_attribute('value')
                selected_attr = checkbox_element.get_attribute('selected')
                enabled_attr = checkbox_element.get_attribute('enabled')
                
                self.logger.info(f"iOS attributes - value: {value_attr}, selected: {selected_attr}, enabled: {enabled_attr}")
                
                # iOS checkboxes typically use 'value' or 'selected' attributes
                is_checked = (value_attr == '1' or 
                            value_attr == 'true' or
                            selected_attr == 'true' or
                            selected_attr == '1')
                
                self.logger.info(f"iOS Private checkbox status: {'Checked' if is_checked else 'Unchecked'}")
                return is_checked
            # For Android, check the 'checked' attribute
            else:
                checked_attr = checkbox_element.get_attribute('checked')
                value_attr = checkbox_element.get_attribute('value')
                
                self.logger.info(f"Android attributes - checked: {checked_attr}, value: {value_attr}")
                
                is_checked = (checked_attr == 'true' or value_attr == '1')
                self.logger.info(f"Android Private checkbox status: {'Checked' if is_checked else 'Unchecked'}")
                return is_checked
                
        except Exception as e:
            self.logger.error(f"Exception while checking private checkbox status: {str(e)}")
            return False

    def check_private_meetup_checkbox(self, value: bool):
        try:
            current_status = self.is_private_checkbox_checked()
            self.logger.info(f"Current private checkbox status: {current_status}, Target status: {value}")
            
            if current_status != value:
                self.logger.info(f"Toggling private checkbox from {current_status} to {value}")
                checkbox_element = self.find_element(self.locator["is_private"], timeout=10)
                self.logger.info(f"Checkbox element found: {checkbox_element}")
                self.logger.info(f"Checkbox is_displayed: {checkbox_element.is_displayed()}")
                self.logger.info(f"Checkbox is_enabled: {checkbox_element.is_enabled()}")
                
                self.click_element(self.locator["is_private"])
                self.logger.info("Checkbox clicked successfully")
                
                import time
                time.sleep(1)
                
                new_status = self.is_private_checkbox_checked()
                if new_status == value:
                    self.logger.info(f"Successfully toggled private checkbox to {value}")
                else:
                    self.logger.warning(f"Checkbox toggle may have failed. Expected: {value}, Actual: {new_status}")
            else:
                self.logger.info(f"Private checkbox already in desired state: {value}")
                
        except Exception as e:
            self.logger.error(f"Exception while making meetup as is_private:: {value}, Exception:: {str(e)}")
            raise Exception(f"Unable to check is_private as {value}")
    
    def click_add_teacher(self):
        try:
            self.click_element(self.locator["add_teacher"])
        except Exception as e:
            self.logger.error(f"Exception while clicking the add_teacher, exception:: {str(e)}")
            raise Exception(f"Unable to click the add_teacher")
     
    def select_organizer(self, value: str):
        try:
            self.scroll_to_element(self.locator["scroll"],self.locator["organizer_txt_field"])
            self.click_element(self.locator["organizer_txt_field"])
            time.sleep(3)
            self.send_keys(self.locator["search"], value, is_necessary=False)
            self.driver.press_keycode(66) if self.platform == "android" else self.driver.hide_keyboard(key_name='Done')
            organizer = self.build_locator(self.locator["item"], value)
            self.click_element(organizer)
        except Exception as e:
            self.logger.error(f"Exception raised while selecting organizer as {value}, Exception:: {str(e)}")
            raise Exception(f"Unable to select Organizer as {value}")
      
    def select_start_date(self, start_date: str, recurring: bool = False):
        try: 
                print(f"recurring: {recurring}")
                if recurring:
                    txtField = self.locator["Ends_On_Date_txt_field"]
                else:
                    txtField = self.build_locator(self.locator["date_ith_txt_field"], "1")
                    self.scroll_to_element(self.locator["scroll"], txtField)
                self.click_element(txtField)
                self.click_element(self.locator["date_pencil"])
                self.click_element(self.locator["date_enter_field"])
                self.send_keys(self.locator["date_enter_field"], start_date, timeout=10, is_necessary=False)
                ok = self.find_element(self.locator["option_ok"], 5)
                self.click_element(ok)
        except Exception as e:
            self.logger.error(f"Exception raised while selecting StartDate as {start_date}, Exception:: {str(e)}")
            raise Exception(f"Unable to select StartDate as {start_date}")

    def select_start_time(self, start_time: str, timezone: str = ""):
        try:
            if timezone:
                # current_time = TimezoneFormatter.get_the_current_time_for_given_timezone(timezone)
                txtField = self.build_locator(self.locator['time_ith_txt_field'], "1")
                self.scroll_to_element(self.locator["scroll"], txtField)
                self.click_element(txtField)
                valueHour,valueMin = start_time.split()[0].split(":")
                valuePeriod = start_time.split()[1]
                # self.click_element(self.locator['time_keyboard'], 10)
                hour = self.find_element(self.locator['time_hour'])
                min = self.find_element(self.locator['time_min'])
                period = self.build_locator(self.locator['time_period'], str(valuePeriod))
                self.click_element(hour)
                self.send_keys(hour, valueHour, timeout=10, is_necessary=False)
                self.click_element(min)
                self.send_keys(min, valueMin, timeout=10, is_necessary=False)
                self.click_element(period)
                self.click_element(self.locator['option_ok'], 10)
        except Exception as e:
            self.logger.error(f"Exception raised while selecting StartTime as {start_time}, Exception:: {str(e)}")
            raise Exception(f"Unable to select StartTime as {start_time}")
    
    def enter_meeting_url(self, url):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["meeting_link_txt_field"],ensure=True)
            time.sleep(2)
            self.click_element(self.locator["meeting_link_txt_field"])
            self.send_keys_without_enter(self.locator["meeting_link_txt_field"], url)
            self.driver.hide_keyboard()
        except Exception as e:
            self.logger.error(f"Exception raised while entering MeetingURL as {url}, Exception:: {str(e)}")
            raise Exception (f"Unable to enter MeetingURL as {url}")
    
    def _handle_contact_persons(self, data: List[str], modeOfSelectContact: str):
        """Handle contact person selection or creation."""
        if not data:
            raise Exception("No contact person selected")
        
        self.scroll_to_element(self.locator["scroll"], self.locator["add_point_of_contact_button"])
        element = self.find_element(self.locator["add_point_of_contact_button"])
        location = element.location
        size = element.size
        x = location['x'] + 10
        y = location['y'] + size['height'] // 2
        self.driver.tap([(x, y)])
        self.logger.info("Clicked add point of contact button")
        time.sleep(3)
    
        if modeOfSelectContact == "BySearch":
            self.logger.info("Selecting contact person by search")
            contact_person = data
            print(f"contact_person: {contact_person}")
            self.select_contact_person(contact_person)
            self.logger.info(f"Selected contact person: {contact_person}")
        elif modeOfSelectContact == "ByExistingTeam":
            self.logger.info("Selecting contact person from existing team")
            contact_person_result  = self.build_locator(self.locator["search_result"], data[0])
            self.logger.info(f"contact_person_result: {contact_person_result}")
            if self.is_displayed(contact_person_result, timeout=10):
                self.click_element(contact_person_result)
                self.logger.info("Selected contact person from existing team")
            else:
                raise Exception("Contact person not found in existing team")
        
        self.click_element(self.locator["done_button"], 10)
        self.logger.info("Clicked done button")
    
  

    
    def enter_address(self, value):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["address"],ensure=True)
            time.sleep(2)
            self.click_element(self.locator["address"])
            self.send_keys(self.locator["address"], value)
        except Exception as e:
            self.logger.error(f"Exception raised while entering Address as {value}, Exception:: {str(e)}")
            raise Exception(f"Unable to enter Address as {value}")

    def enter_city(self, value):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["city"], ensure=True)
            time.sleep(1)
            self.click_element(self.locator["city"])
            self.send_keys(self.locator["city"], value)
        except Exception as e:
            self.logger.error(f"Exception while entering city as {value}, exception:: {str(e)}")
            raise Exception(f"Unable to enter City as {value}")
        
    def enter_zipcode(self, value):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["zipcode"], ensure=True)
            self.click_element(self.locator["zipcode"])
            self.send_keys(self.locator["zipcode"], str(int(float(value))))
        except Exception as e:
            self.logger.error(f"Exception while entering zipcode as {value}, exception:: {str(e)}")
            raise Exception(f"Unable to enter ZipCode as {value}")
    
    def select_state(self, value):
        try:
            self.click_element(self.locator["state_txt_field"])
            time.sleep(2)
            self.send_keys(self.locator["search"], value, is_necessary=False)
            self.driver.press_keycode(66) if self.platform == "android" else self.driver.hide_keyboard(key_name='Done')
            state = self.build_locator(self.locator["centerOrState"], value)
            time.sleep(2)
            self.click_element(state)
        except Exception as e:
            self.logger.error(f"Exception while selecting state as {value}, exception:: {str(e)}")
            raise Exception(f"Unable to select State as {value}")
    
    # use in the cases where you can locate the element using ACCESSIBILITY_ID
    def is_txt_displayed(self, msg: str):
        try:
            msgLoc = self.build_locator(self.locator['msg'], msg)
            self.scroll_to_element(self.locator["scroll"], msgLoc)
            return self.is_displayed(msgLoc), f"Text:: {msg} is not displayed"
        
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the text:: {msg}, exception:: {str(e)}")
            return False, f"Text:: {msg} is not displayed"
        
    # use this method in the case where you want to verify a text (should has ACCESSIBILITY_ID ) by moving upward~
    def  is_error_message_displayed(self, message):
        errMsg = self.build_locator(self.locator['msg'], message)
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator["create_now"])
            self.scroll_to_element(self.locator['scroll'], errMsg, direction="up")
            return self.is_displayed(errMsg), "ErrorMessage:: {message} is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the error:: {message}, exception:: {str(e)}")
            return False, f"ErrorMessage:: {message} is not displayed"
    
    def is_meetup_mode_displayed(self, mode):
        try:
            inPersonLoc = self.build_locator(self.locator['meetup_type'], mode)
            self.scroll_to_element(self.locator["scroll"], inPersonLoc)
            return self.is_displayed(inPersonLoc), "MeetupMode::{mode} is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the MeetupMode:: {mode}, exception:: {str(e)}")
            return False, f"MeetupMode::{mode} is not displayed"
    
    def is_select_meetup_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['select_meetup_txt_box'])
            return self.is_displayed(self.locator['select_meetup_txt_box']), "MeetupProduct selction field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the MeetupProductSelectField, exception:: {str(e)}")
            return False, f"MeetupProduct selction field is not exist"

    def is_max_attendees_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['max_attendees_txt_field'])
            return self.is_displayed(self.locator['max_attendees_txt_field']), "MaxAttendees field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the MaxAttendeesField, exception:: {str(e)}")
            return False, "MaxAttendees field is not exist"
        
    def is_private_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['is_private'])
            return self.is_displayed(self.locator['is_private']), "IsPrivate CheckBox is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the IsPrivateField, exception:: {str(e)}")
            return False, "IsPrivate CheckBox is not exist"
        
    def is_private_checked(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['is_private'])
            return self.is_element_selected(self.locator["is_private"]), "isPrivate checkbox is not interactable"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the isPrivate value as checked, exception:: {str(e)}")
            return False, "isPrivate checkbox is not interactable"
    
    def is_add_teacher_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['add_teacher'])
            return self.is_displayed(self.locator['add_teacher']), "Add Teacher field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Add Teacher, exception:: {str(e)}")
            return False, "Add Teacher field is not exist"
    
    def is_organizer_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['organizer_txt_field'])
            return self.is_displayed(self.locator['organizer_txt_field']), "OrganizerSelection field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the OrganizerSelectionFiled, exception:: {str(e)}")
            return False, "OrganizerSelection field is not exist"

    def is_timezone_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['timezone_txt_field'])
            return self.is_displayed(self.locator['timezone_txt_field']), "Timezone field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the TimezoneField, exception:: {str(e)}")
            return False, "Timezone field is not exist"
    
    def is_date_selection_txt_field_displayed(self):
        try:
            dateLoc = self.build_locator(self.locator["date_ith_txt_field"], str(1))
            self.scroll_to_element(self.locator["scroll"], dateLoc)
            return self.is_displayed(dateLoc), "DateField is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for DateField, exception:: {str(e)}")
            return False, "DateField is not exist"
    
    def is_end_time_displayed(self):
        try:
            dateLoc = self.build_locator(self.locator["time_ith_txt_field"], '1')
            self.scroll_to_element(self.locator['scroll'], dateLoc)
            content = self.get_txt_from_attr(dateLoc).upper()
            countOfAM = content.count("AM")
            countOfPM = content.count("PM")
            return (countOfAM + countOfPM > 1), "EndTime is displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the EndTime, exception:: {str(e)}")
            return False, "EndTime is displayed"
    
    def is_out_range_err_displayed(self):
        try:
            return self.is_displayed(self.locator['out_of_range_err']), "OutOfRangeError message is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the OutOfRangeError, exception:: {str(e)}")
            return False, "OutOfRangeError message is not displayed"
    
    def is_time_selection_txt_field_displayed(self):
        try:
            timeLoc = self.build_locator(self.locator["time_ith_txt_field"], str(1))
            self.scroll_to_element(self.locator["scroll"], timeLoc)
            return self.is_displayed(timeLoc), "TimeSelection field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the TimeSelectionField, exception:: {str(e)}")
            return False, "TimeSelection field is not exist"
    
    def is_link_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['link_txt_field'])
            return self.is_displayed(self.locator['link_txt_field']), "MeetingUrlField is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the MeetingUrlField, exception:: {str(e)}")
            return False, "MeetingUrlField is not exist"
    
    def is_given_location_field_displayed(self, loc):
        try:
            LocationLoc = self.build_locator(self.locator["location"], loc)
            return self.is_displayed(LocationLoc), "AddressValue:: {loc} is displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the LocationValue:: {loc}, exception:: {str(e)}")
            return False, f"AddressValue:: {loc} is displayed"
    
    def is_given_state_appr_displayed(self, state):
        try:
            LocationLoc = self.build_locator(self.locator["centerOrState"], state)
            return self.is_displayed(LocationLoc), "StateValue:: {state} is displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the StateValue:: {state}, exception:: {str(e)}")
            return False, f"StateValue:: {state} is displayed"


    def is_address_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['address'])
            return self.is_displayed(self.locator['address']), "AddressTxtField is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the AddressTxtField, exception:: {str(e)}")
            return False, f"AddressTxtField is not exist"

    def is_zipcode_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['zipcode'])
            return self.is_displayed(self.locator['zipcode']), "ZipCodeTxtField is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the ZipCodeTxtField, exception:: {str(e)}")
            return False, f"ZipCodeTxtField is not exist"

    def is_city_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['city'])
            return self.is_displayed(self.locator['city']), "CityTxtField is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the CityTxtField, exception:: {str(e)}")
            return False, f"CityTxtField is not exist"

    def is_state_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['state_txt_field'])
            return self.is_displayed(self.locator['state_txt_field']), "State selection field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the StateSelectionField, exception:: {str(e)}")
            return False, f"State selection field is not exist"

    def is_aol_center_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['aol_center_txt_field'])
            return self.is_displayed(self.locator['aol_center_txt_field']), "AOlCenter selection field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the AolCenterSelectionField, exception:: {str(e)}")
            return False, f"AOlCenter selection field is not exist"

    def is_add_contact_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['add_contact'])
            return self.is_displayed(self.locator['add_contact']), "Add Contact field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Add Contact, exception:: {str(e)}")
            return False, f"Add Contact field is not exist"
    
    def is_contact_txt_field_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['contact_txt_field'])
            return self.is_displayed(self.locator['contact_txt_field']), "ContactPerson selection field is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the ContactSelectionField, exception:: {str(e)}")
            return False, f"ContactPerson selection field is not exist"
        
    def is_new_meetup_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['new_meetup_header'])
            return self.is_displayed(self.locator['new_meetup_header']), "New Meetup Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the New Meetup Header, exception:: {str(e)}")
            return False, f"New Meetup Header is not displayed"
    
    def is_meetup_information_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['new_meetup_header'])
            return self.is_displayed(self.locator['new_meetup_header']), "Meetup Information Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Meetup Information Header, exception:: {str(e)}")
            return False, f"Meetup Information Header is not displayed"
        
    def is_select_teacher_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['select_teacher_header'])
            return self.is_displayed(self.locator['select_teacher_header']), "Select Teacher Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Select Teacher Header, exception:: {str(e)}")
            return False, f"Select Teacher Header is not displayed"

    def is_select_organizer_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['select_org_header'])
            return self.is_displayed(self.locator['select_org_header']), "Select Organizer Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Select Organizer Header, exception:: {str(e)}")
            return False, f"Select Organizer Header is not displayed"

    def is_event_date_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['select_date_header'])
            return self.is_displayed(self.locator['select_date_header']), "Event Date Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Event Date Header, exception:: {str(e)}")
            return False, f"Event Date Header is not displayed"

    def is_location_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['location_header'])
            return self.is_displayed(self.locator['location_header']), "Location Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Location Header, exception:: {str(e)}")
            return False, f"Location Header is not displayed"
    
    def is_meeting_url_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['meeting_url_header'])
            return self.is_displayed(self.locator['meeting_url_header']), "MeetingURL Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the MeetingURL Header, exception:: {str(e)}")
            return False, f"MeetingURL Header is not displayed"
    
    def is_revenue_header_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['revenue_header'])
            return self.is_displayed(self.locator['revenue_header']), "Revenue & Detail Header is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the Revenue & Details Header, exception:: {str(e)}")
            return False, f"Revenue & Detail Header is not displayed"
    
    def is_create_now_displayed(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['create_now'])
            return self.is_displayed(self.locator['create_now']), "CreateNow Button is not exist"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the CreateNow Button, exception:: {str(e)}")
            return False, f"CreateNow Button is not exist"
    
    def is_max_attendees_err_displayed(self, msg):
        try:
            loc = self.build_locator(self.locator["max_attendees_err_msg"], msg)
            self.scroll_to_element(self.locator["scroll"], loc, "up")
            return self.is_displayed(loc), "MaxAttendees Error is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the MaxAttendeesError, exception:: {str(e)}")
            return False, f"MaxAttendees Error is not displayed"
    
    def is_no_teachers_err_displayed(self, count):
        try:
            field = self.build_locator(self.locator["teacher_ith_txt_field"], "1")
            self.scroll_to_element(self.locator["scroll"], field, "up")
            locators = self.find_elements(self.locator["teacher_err_msg"])
            if len(locators) == count + 1:
                return True, "Passed"
            return False, "NoTeacher Error is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the NoTeacherError, exception:: {str(e)}")
            return False, f"NoTeacher Error is not displayed"

    def is_no_address_err_displayed(self, msg):
        try:
            loc = self.build_locator(self.locator["address_err_field"], msg)
            self.scroll_to_element(self.locator["scroll"], self.locator['create_now'])
            self.scroll_to_element(self.locator["scroll"], loc, "up")
            return self.is_displayed(loc), "No Address Error is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the NoAddressError, exception:: {str(e)}")
            return False, f"No Address Error is not displayed"

    def is_no_city_err_displayed(self, msg):
        try:
            loc = self.build_locator(self.locator["city_err_filed"], msg)
            self.scroll_to_element(self.locator["scroll"], self.locator['create_now'])
            self.scroll_to_element(self.locator["scroll"], loc, "up")
            return self.is_displayed(loc), "No City Error is not displayed"
        except Exception as e:
            self.logger.error(f"Exception raised while checking for the NoCityError, exception:: {str(e)}")
            return False, f"No City Error is not displayed"
    
    def get_max_attendees_value(self):
        try:
            return self.get_element_text(self.locator["max_attendees_txt_field"]).strip(), "Unable to get MaxAttendees value"
        except Exception as e:
            self.logger.error(f"Exception raised while getting for the MaxAttendeesValue, exception:: {str(e)}")
            return False, f"Unable to get MaxAttendees value"
    
    def get_selected_organizer(self):
        try:
            return self.get_element_text(self.locator["organizer_txt_field"]).strip(), "Unable to get selected organizer"
        except Exception as e:
            self.logger.error(f"Exception raised while getting for the OrganizerValue, exception:: {str(e)}")
            return False, f"Unable to get selected organizer"
    
    def get_entered_link(self):
        try:
            return self.get_element_text(self.locator["link_txt_field"]).strip(), "Unable to get MeetingUrl value"
        except Exception as e:
            self.logger.error(f"Exception raised while getting for the MeetingURLValue, exception:: {str(e)}")
            return False, f"Unable to get MeetingUrl value"
    
    def get_entered_address(self):
        try:
            loc = self.build_locator(self.locator["location_ith_filed"], "1")
            self.scroll_to_element(self.locator['scroll'], loc)
            return self.get_element_text(loc), "Unable to get address value"
        except Exception as e:
            self.logger.error(f"Exception raised while getting for AddrerssValue, exception:: {str(e)}")
            return False, f"Unable to get address value"
    
    def get_selected_aol_center(self):
        try:
            return self.get_element_text(self.locator["aol_center_txt_field"]).strip(), "Unable to get selected Center"
        except Exception as e:
            self.logger.error(f"Exception raised while getting for AOLCenterValue, exception:: {str(e)}")
            return False, f"Unable to get selected Center"
    
    def get_selected_contact_person(self):
        try:
            return self.get_element_text(self.locator["meetup_contact_txt_field"]).strip(), "Unable to get selected ContactPerson"
        except Exception as e:
            self.logger.error(f"Exception raised while getting for ContactPersonValue, exception:: {str(e)}")
            return False, f"Unable to get selected ContactPerson"
        
    def get_final_error_msg(self):
        try:
            return self.get_txt_from_attr(self.locator["final_msg"]), "Unable to get the Final Error message"
        except Exception as e:
            self.logger.error(f"Exception raised while getting the final page error message, exception:: {str(e)}")
            return False, f"Unable to get the Final Error message"

    def _handle_address(self, data):
        """Handle address entry for in-person events."""

        if data['isUseExistingVenue'].lower() == 'true':
            if data['ExistingAddressName']:
                self.enter_existing_address(data['ExistingAddressName'], data['tenant'])
                self.logger.info(f"Entered address: {data['ExistingAddressName']}")
        else:
            self.scroll_to_element(self.locator["scroll"], self.locator["add_new_address_button"])
            self.click_element(self.locator["add_new_address_button"])
            self.logger.info("Clicked add new address button")
            
            if data['addressName']:
                self.enter_addressName(data['addressName'])
                self.logger.info(f"Entered address Name: {data['addressName']}")
            
            if data['zipcode']:
                self.enter_zipcode(data['zipcode'], data['tenant'])
                self.logger.info(f"Entered zipcode: {data['zipcode']}")
            
            if data['city']:
                self.enter_city(data['city'], data['tenant'])
                self.logger.info(f"Entered city: {data['city']}")

            if data['address']:
                self.enter_address(data['address'])
                self.logger.info(f"Entered address: {data['address']}")
            
            if self.is_displayed(self.locator["create_button"]):
                self.click_element(self.locator["create_button"])
                self.logger.info("Address created successfully")
            else:
                raise Exception("Done button not found for address creation")
            
            self.enter_existing_address(data.address_details["addressName"], data.tenant)
            self.logger.info(f"Entered address: {data.address_details['addressName']}")


    def selectFrequencyOn_After(self, data):
        try:
            print(data['EndsChoice'])
            print(data['FrequencyValue'])
            print(data['EndsValue'])
            if(data['EndsChoice'].lower() == 'on'):
                self.logger.info(f"Selecting Ends On radio button")
                self.click_element(self.locator["Ends_ON_radioButton"])
                self.select_start_date(data['EndsValue'],True)
                self.logger.info(f"Selected start date: {data['EndsValue']}")
            else:
                self.logger.info(f"Selecting Ends After radio button")
                # self.click_element(self.locator["Ends_After_radioButton"])
                self.click_element(self.locator["Occurence_count_txt_field"])
                self.enter_search_field_value(self.locator["Occurence_count_txt_field"], data['EndsValue'])
                self.logger.info(f"Selected occurrence count: {data['EndsValue']}")
            self.click_element(self.locator["done_button"])
        except Exception as e:
            self.logger.error(f"Exception while selecting Daily On After, exception:: {str(e)}")
            raise Exception(f"Unable to select Daily On After")

    def select_recurring_meetup(self, data):
        try:
            self.click_element(self.locator["recurring_count_txt_field"])
            self.enter_search_field_value(self.locator["recurring_count_txt_field"], data['recurring_count'])
            time.sleep(2)
            self.click_element(self.locator["frequency_dropdown"])
            if data['FrequencyValue']  == 'Daily':
                self.click_element(self.locator["Frequency_dropdown_Daily"])
            elif data['FrequencyValue']  == 'Weekly':
                self.click_element(self.locator["Frequency_dropdown_Weekly"])
                time.sleep(2)
                day = self.build_locator(self.locator["Weekly_select_value"], data['OnValues'])
                date_obj = datetime.strptime(data['dates'], "%m/%d/%Y")
                day_name = date_obj.strftime("%A")
                print(f"day_name: {day_name}")
                print(f"data['OnValues']: {data['OnValues']}")
                if day_name != data['OnValues']:
                    extra_day = self.build_locator(self.locator["Weekly_select_value"], day_name)
                    self.click_element(extra_day)
                    self.click_element(day)
                self.logger.info(f"Selected weekly day: {data['OnValues']}")
            elif data['FrequencyValue']  == 'Monthly':
                self.click_element(self.locator["Frequency_dropdown_Monthly"])
                self.click_element(self.locator["monthly_dropdown"])
                month = self.build_locator(self.locator["Monthly_dropdown_value"],data['OnValues'])
                self.click_element(month)
                self.logger.info(f"Selected monthly month: {data['OnValues']}")
            self.selectFrequencyOn_After(data)
            self.logger.info(f"Selected frequency: {data['FrequencyValue']} on {data['OnValues']}")
        except Exception as e:
            self.logger.error(f"Exception while selecting recurring meetup, exception:: {str(e)}")
            raise Exception(f"Unable to select recurring meetup")
    
    def create_meetup(self, data, message):
        content = None

        teachers = self.parse_list(data['teachers'])
        organizers = self.parse_list(data['organizers'])
        notify_persons = self.parse_list(data['NotifyPersons'])
        contact_persons = self.parse_list(data['contact_person'])
        try:
            
            # self.select_meetup_mode_and_product(data['event_mode'], data['product_name'])
            if data['event_mode']:
                print(f"Selected event mode: {data['event_mode']}")
                self.select_event_mode(data['event_mode'])
                self.logger.info(f"Selected event mode: {data['event_mode']}")
            
            # Step 2: Select course
            if data['product_name']:
                self.select_product(data['product_name'], data['tenant'])
                self.logger.info(f"Selected course: {data['product_name']}")
            
            # Step 3: Set privacy
            self.check_is_private(data['is_private'], data['tenant'])
            self.logger.info(f"Private meetup: {data['is_private']}")

            # Step 5: Select teachers
            if teachers:
                self.select_n_teachers(teachers)
                self.logger.info(f"Selected teachers: {teachers}")
            
            # Step 6: Select organizers
            if organizers:
                self.select_n_organizers(organizers)
                self.logger.info(f"Selected organizers: {organizers}")

            # Step 9: Handle notifications
            if notify_persons:
                self._handle_notifications(notify_persons)

            # Step 10: Handle contact persons
            print(contact_persons)
            self._handle_contact_persons(contact_persons,data["modeOfSelectContact"])

            if data['timezone']:
                self.select_timezone(data['timezone'])
            self.logger.info(f"Timezone selected: {data['timezone']}")
            if data['timezone'] and data['dates']:
                self.select_start_date(data['dates'],False)
            self.logger.info(f"Start date selected: {data['dates']}")
            self.select_start_time(data['start_times'].upper(),data['timezone'])
            self.logger.info(f"Start time selected: {data['start_times']}")

            if(data['isRecurring'].lower() == 'true'):
                self.scroll_to_element(self.locator["scroll"], self.locator["recurring_meetup_button"])
                self.logger.info(f"Clicking Recurring meetup button")
                self.click_element(self.locator["recurring_meetup_button"])
                time.sleep(2)
                self.select_recurring_meetup(data)
                self.logger.info(f"Recurring meetup selected: {data['recurring_count']}")

            # Step 13: Handle address (for in-person events)
            if data['event_mode'].lower() == 'in-person':
                self._handle_address(data)
            elif data['event_mode'].lower() == 'online':
                self.enter_meeting_url(data["meeting_url"])

            #     # Step 14: Enter max attendees
            if data['max_attendees']:
                self.enter_max_attendees(data['max_attendees'], data['tenant'])
                self.logger.info(f"Max attendees: {data['max_attendees']}")

            if data['aol_center']:
                self.select_aol_center(data['aol_center'])
                self.logger.info(f"Selected AOL center: {data['aol_center']}")

          
            self.click_create_button()
            print('Create now button clicked')
            time.sleep(1)
            content = self.extract_page_contents()
            print("contents in meetup success page:",content)
            result = message in content
            self.logger.info(f"Meetup Create is {'passed' if result else 'failed'}")
            self.logger.info(f"Observed Screen content:: {content}")
            return result, self.__get_error_message(result)
        except Exception as e:
            self.logger.info(f"Observed Screen content:: {content}")
            return False, f'Meetup Creation is failed due to {str(e)}'
        
    def __get_error_message(self, result):
        if result == False:
            message, expMsg = self.get_final_error_msg()
            return f"{message}"
        else:
            return f"Observed Content::{self.extract_page_contents()}"



















    


    

    
    

    
