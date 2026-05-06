import json
import time
import pandas as pd
import allure
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from appium.webdriver.webdriver import WebDriver
from config.config import TestConfig
from constants.locator.course_create_locator import CourseCreateLocator
from constants.locator.course_details_locator import CourseDetailsLocator
from constants.locator.myevent_locator import MyEventLocator
from constants.tenant_config import TenantConfig, TenantConfiguration
from pages.base_page import BasePage
from pages.course_details_page import CourseDetailsPage
from pages.my_events_page import MyEventsPage
from utils.time_zone_util import TimezoneFormatter
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig


@dataclass
class CourseData:
    """Data class to hold parsed course creation data from CSV row."""
    test_case_id: str = ""
    tenant: str = ""
    event_mode: str = ""
    product_name: str = ""
    is_private: bool = False
    max_attendees: int = 0
    timezone: str = ""
    languages: List[str] = None
    teachers: List[str] = None
    organizers: List[str] = None
    teaching_assistants: List[str] = None
    volunteers: List[str] = None
    notify_persons: List[str] = None
    contact_persons: List[str] = None
    new_contact_person: Dict[str, str] = None
    mode_of_select_contact: str = ""
    event_dates: List[Dict[str, str]] = None
    is_change_weekend_timing: bool = False
    weekend_start_time: str = ""
    address_details: Dict[str, str] = None
    is_use_existing_venue: bool = False
    aol_center: str = ""
    apex: str = ""
    ic: str = ""
    contribution: str = ""
    
    def __post_init__(self):
        self.languages = self.languages or []
        self.teachers = self.teachers or []
        self.organizers = self.organizers or []
        self.teaching_assistants = self.teaching_assistants or []
        self.volunteers = self.volunteers or []
        self.notify_persons = self.notify_persons or []
        self.contact_persons = self.contact_persons or []
        self.event_dates = self.event_dates or []
        self.address_details = self.address_details or {}
    
    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> 'CourseData':
        """Parse a CSV row dictionary into CourseData object."""
        tenant = row.get("tenant", "").strip().lower()
        
        # Parse comma-separated lists
        def parse_list(value: str) -> List[str]:
            if not value:
                return []
            return [item.strip() for item in value.split(',') if item.strip()]
        
        # Parse event dates based on tenant
        dates_str = row.get("dates", "")
        start_times_str = row.get("start_times", "")
        end_times_str = row.get("end_times", "")
        
        dates = parse_list(dates_str)
        start_times = parse_list(start_times_str)
        end_times = parse_list(end_times_str)
        
        event_dates = []
        for i in range(len(dates)):
            event_dates.append({
                "date": dates[i] if i < len(dates) else "",
                "start_time": start_times[i] if i < len(start_times) else "",
                "end_time": end_times[i] if i < len(end_times) else ""
            })
        
        # Parse address details
        if row.get("isUseExistingVenue", "").strip().lower() == "true":
            address_details = {"address": row.get("ExistingAddressName", "")}
        else:
            address_details = {
                "addressName": row.get("addressName", ""),
                "address": row.get("address", ""),
                "city": row.get("city", ""),
                "zipcode": row.get("zipcode", ""),
                "state": row.get("state", ""),
            }
        
        # Parse new contact person JSON
        new_contact = None
        if row.get("modeOfSelectContact") == "ByCreatingNewContact" and tenant == "india":
            try:
                new_contact = json.loads(row.get("newContactPerson", "{}"))
            except json.JSONDecodeError:
                new_contact = {}
        
        return cls(
            test_case_id=row.get("Test Case ID", "N/A"),
            tenant=tenant,
            event_mode=row.get("event_mode", ""),
            product_name=row.get("product_name", ""),
            is_private=row.get("is_private", "").strip().lower() == "true",
            max_attendees=int(row.get("max_attendees", 0) or 0),
            timezone=row.get("timezone", ""),
            languages=parse_list(row.get("languages", "")),
            teachers=parse_list(row.get("teachers", "")),
            organizers=parse_list(row.get("organizers", "")),
            teaching_assistants=parse_list(row.get("teaching_assistant", "")) if tenant == "india" else [],
            volunteers=parse_list(row.get("volunteer", "")) if tenant == "india" else [],
            notify_persons=parse_list(row.get("NotifyPersons", "")),
            contact_persons=parse_list(row.get("contact_person", "")),
            new_contact_person=new_contact,
            mode_of_select_contact=row.get("modeOfSelectContact", ""),
            event_dates=event_dates,
            is_change_weekend_timing=row.get("is_change_weekend_timing", "").strip().lower() == "true",
            weekend_start_time=row.get("weekend_start_time", "").strip(),
            address_details=address_details,
            is_use_existing_venue=row.get("isUseExistingVenue", "").strip().lower() == "true",
            aol_center=row.get("aol_center", ""),
            apex=row.get("apex", ""),
            ic=row.get("ic", ""),
            contribution=row.get("contribution", ""),
        )


class CourseCreatePage(BasePage):
    """
    Page object for Course Creation page.
    
    Uses TenantConfig for all tenant-specific logic to ensure consistency
    and maintainability. All field labels and feature flags are centralized.
    """

    def __init__(self, driver: WebDriver, platform: str):
        super().__init__(driver, platform)
        self.locator = {
            **CourseCreateLocator.get_locators(platform),
            **MyEventLocator.get_locators(platform),
            **CourseDetailsLocator.get_locators(platform),
         }
        from constants.message.event_create_message import EventCreateMessage
        self.event_create_message = EventCreateMessage.get_message()
        self.course_details = CourseDetailsPage(self.driver, platform)
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self._tenant_config: Optional[TenantConfiguration] = None
    
    def _get_tenant_config(self, tenant: str) -> TenantConfiguration:
        """Get and cache tenant configuration."""
        if self._tenant_config is None or self._tenant_config.tenant_id != tenant.lower():
            self._tenant_config = TenantConfig.get_config(tenant)
        return self._tenant_config
    
    def _get_field_label(self, tenant: str, field_name: str) -> str:
        """Get tenant-specific field label."""
        config = self._get_tenant_config(tenant)
        return config.get_field_label(field_name)
    
    def _has_feature(self, tenant: str, feature_name: str) -> bool:
        """Check if tenant has a specific feature."""
        config = self._get_tenant_config(tenant)
        return config.has_feature(feature_name)


    @allure.step("entering product for course creation: {value}")
    def enter_search_field_value(self,locator, value):
        try:
            self.logger.info(f"Entering product: {value}")

            element = self.find_element(locator)
            element.click()
            self.clear_search_field(element)
            self.driver.execute_script("mobile: type", {"text": value})

            # Trigger search
            self.driver.press_keycode(66)

            self.logger.info(f"Successfully entered value in search field: {value}")

        except Exception as e:
            self.logger.error(f"Failed to enter value in search field {value}: {e}")
            raise Exception(f"Unable to enter value in search field as {value}")

    @allure.step("Select event mode: {value}")
    def select_event_mode(self, value):
        try:
            self.logger.info(f"Selecting event mode: {value}")
            if value.lower() == 'in-person':
                value = 'In-person Button'
                self.logger.debug("Converting 'in-person' to 'In-person'")
            elif value.lower() == 'online':
                value = 'Online Button'
                self.logger.debug("Converting 'online' to 'Online'")
            event_mode = self.build_locator(self.locator["event_mode"], value)
            self.click_element(event_mode)
            self.logger.info(f"Successfully selected event mode: {value}")
        except Exception as e:
            self.logger.error(f"Failed to select event mode {value}: {e}")
            raise Exception(f"Unable to select event mode as {value} {e}")

    def select_product(self, value: str, tenant: str):
        """
        Select a course/product from the dropdown.
        
        Args:
            value: Course name to select
            tenant: Tenant identifier for field label lookup
        """
        try:
            self.click_element(self.locator["product_dropdown"])
            self.logger.debug("Clicked on course dropdown")

            # Get tenant-specific labels from config
            config = self._get_tenant_config(tenant)
            product_label = config.field_labels.product
            # first_product_label = config.field_labels.first_product
            
            product_txt_field = self.build_locator(self.locator["product_txt_field"], product_label)
            first_product_name = self.build_locator(self.locator["first_product_name"],value )
            
            self.logger.debug(f"Using labels - product: {product_label}, first_product: {value}")

            self.click_element(product_txt_field)
            self.logger.debug("Clicked on course text field")

            self.enter_search_field_value(product_txt_field, value)
            time.sleep(3)

            if self.is_displayed(first_product_name, timeout=10):
                self.click_element(first_product_name)
            elif self.is_displayed(self.locator["no_result_msg"], timeout=10):
                self.logger.error(f"Product not found: {value}")
                raise Exception(f"Product '{value}' not found")
            else:
                raise Exception("Unexpected search result")

            self.logger.info(f"Successfully selected course: {value}")

        except Exception as e:
            self.logger.error(f"Failed to select course {value}: {e}")
            raise

    def check_is_private(self, value: bool, tenant: str):
        """
        Set the private/public status of the course.
        
        Args:
            value: True to make private, False to keep public
            tenant: Tenant identifier for checkbox label lookup
        """
        try:
            if value:
                config = self._get_tenant_config(tenant)
                checkbox_label = config.field_labels.is_private_checkbox
                is_private_checkbox = self.build_locator(self.locator["is_private"], checkbox_label)
                self.click_element(is_private_checkbox)
                self.logger.info("Setting course as private")
                self.logger.debug(f"Clicked private checkbox with label: {checkbox_label}")
            else:
                self.logger.info("Keeping course as public")
        except Exception as e:
            self.logger.error(f"Failed to set private status {value}: {e}")
            raise Exception(f"Unable to check is private value as {value}")

    @allure.step("Enter max attendees: {value}")
    def enter_max_attendees(self, value: int, tenant: str):
        """
        Enter max attendees/participants value.
        
        Args:
            value: Maximum number of attendees
            tenant: Tenant identifier for field label lookup
        """
        try:
            self.logger.info(f"Entering max attendees: {value}")
            
            config = self._get_tenant_config(tenant)
            field_label = config.field_labels.max_attendees
            max_attendees_txt_field = self.build_locator(self.locator["max_attendees_txt_field"], field_label)
            
            self.logger.debug(f"Using max attendees label: {field_label}")

            self.scroll_to_element_by_touch(max_attendees_txt_field)
            self.click_element(max_attendees_txt_field)
            try:
                self.driver.hide_keyboard()
            except Exception:
                pass
            self.send_keys(max_attendees_txt_field, str(value))
            self.logger.info(f"Successfully entered max attendees: {value}")
        except Exception as e:
            self.logger.error(f"Failed to enter max attendees {value}: {e}")
            raise Exception(f"Unable to enter max attendees as {value}")

    def select_people(self, names: list[str], add_button, role_name: str):
        """
        Generic method to select teachers / organizers / teaching assistants / volunteers
        """
        try:
            self.click_add_person_button(add_button,role_name)

            self.logger.info(f"Selecting {len(names)} {role_name}(s): {names}")
            for name in names:
                try:
                    result = self.build_locator(self.locator["search_result"], name)
                    self.logger.info(f"result: {result}")
                    search_box = self.locator["search"]
                    self.click_element(search_box)
                    self.logger.info("search box clicked")
                    self.enter_search_field_value(search_box, name)
                    self.logger.info(f"search field value entered: {name}")
                    time.sleep(3)
                    if self.is_displayed(result, timeout=10):
                        self.logger.info(f"{role_name} found: {name}")
                        self.click_element(result)
                        self.logger.info(f"{role_name} selected: {name}")

                    elif self.is_displayed(self.locator["no_result_msg"], timeout=10):
                        self.logger.info(f"{role_name} not found: {name}")
                        raise Exception(f"{role_name} '{name}' not found")

                    else:
                        self.logger.info(f"Unexpected search result: {name}")
                        raise Exception("Unexpected search result")

                except Exception as person_error:
                    self.logger.warning(f"Failed selecting {role_name} '{name}': {person_error}")

            if self.is_displayed(self.locator["done_button"], timeout=10):
                self.click_element(self.locator["done_button"])
            else:
                raise Exception(f"{role_name} Done button not found")

            self.logger.info(f"Successfully selected {len(names)} {role_name}(s)")

        except Exception as e:
            self.logger.error(f"Error while selecting {role_name}(s) {names}: {e}")
            raise


    def select_n_languages(self, languages: list[str]):
        try:
            self.click_element(self.locator["language_add_button"])
            for language in languages:
                try:
                    self.enter_search_field_value(self.locator["language_search_box"], language)
                    time.sleep(3)
                    first_language_option = self.build_locator(self.locator["first_language_option"], language)
                    if self.is_displayed(first_language_option, timeout=10):
                        self.click_element(first_language_option)

                    elif self.is_displayed(self.locator["no_result_msg"], timeout=10):
                        raise Exception(f"Language '{language}' not found")

                    else:
                        raise Exception("Unexpected search result")

                except Exception as language_error:
                    self.logger.warning(f"Failed selecting language '{language}': {language_error}")

            if self.is_displayed(self.locator["done_button"], timeout=10):
                self.click_element(self.locator["done_button"])
            else:
                raise Exception("Language Done button not found")

            self.logger.info(f"Successfully selected {len(languages)} languages")

        except Exception as e:
            self.logger.error(f"Error while selecting languages {languages}: {e}")
            raise
   
    def select_n_teachers(self, teachers: list[str]):
        self.select_people(
            names=teachers,
            add_button=self.locator["add_teacher"],
            role_name="Teacher"
        )

    def select_n_organizers(self, organizers: list[str]):
        self.select_people(
            names=organizers,
            add_button=self.locator["add_organizer"],
            role_name="Organizer"
        )

    def select_n_teaching_assistants(self, organizers: list[str]):
        self.select_people(
            names=organizers,
            add_button=self.locator["add_teaching_assistant"],
            role_name="Teaching Assistant"
        )

    def select_n_volunteers(self, organizers: list[str]):
        self.select_people(
            names=organizers,
            add_button=self.locator["add_volunteer"],
            role_name="Volunteer"
        )

    def select_teacher(self, teacher_name: str, teacher_type: str = "primary"):
        """
        Select a teacher by name and type (primary/assistant)

        Args:
            teacher_name: Name of the teacher to select
            teacher_type: Type of teacher - "primary" or "assistant"
        """
        try:
            # Determine which teacher field to use based on type
            if teacher_type.lower() == "primary":
                teacher_field = self.locator["teacher_primary_txt_field"]
            elif teacher_type.lower() == "assistant":
                teacher_field = self.locator["teacher_additional_txt_field"]
            else:
                raise Exception(f"Invalid teacher type: {teacher_type}. Must be 'primary' or 'assistant'")

            # Scroll to and click the teacher field
            self.scroll_to_element(self.locator["scroll"], teacher_field)
            self.click_element(teacher_field)
            time.sleep(3)

            # Search for the teacher
            self.send_keys(self.locator["search"], teacher_name, timeout=10, is_necessary=False)

            # Handle keyboard
            if self.platform == "android":
                self.driver.press_keycode(66)  # KEYCODE_ENTER
            else:
                self.driver.hide_keyboard(key_name='Done')

            # Select the teacher from search results
            teacher_locator = self.build_locator(self.locator["item"], teacher_name)
            self.click_element(teacher_locator, 10)

            self.logger.info(f"Successfully selected {teacher_type} teacher: {teacher_name}")

        except Exception as e:
            self.logger.error(f"Error selecting {teacher_type} teacher {teacher_name}: {e}")
            raise Exception(f"Unable to select {teacher_type} teacher: {teacher_name}")

    def is_add_teacher_option_available(self):
        """Check if add teacher option is available"""
        try:
            return self.is_displayed(self.locator["add_teacher"])
        except Exception as e:
            self.logger.error(f"Error checking add teacher option: {e}")
            return False

    def click_add_person_button(self,locator,role_name: str):
        """Click add (teacher/organizer) button to add more persons"""
        try:
            self.scroll_to_element(self.locator["scroll"], locator)
            self.click_element(locator)
            time.sleep(2)
            self.logger.info(f"Clicked add {role_name} button")
        except Exception as e:
            self.logger.error(f"Error clicking add {role_name} button: {e}")
            raise Exception(f"Unable to click add {role_name} button")

    def is_teacher_selection_available(self):
        """Check if teacher selection interface is available"""
        try:
            # Check if teacher selection fields are available
            primary_available = self.is_displayed(self.locator["teacher_primary_txt_field"])
            additional_available = self.is_displayed(self.locator["teacher_additional_txt_field"])
            return primary_available or additional_available
        except Exception as e:
            self.logger.error(f"Error checking teacher selection availability: {e}")
            return False

    def create_new_contact_person(self, contact_person: str):
        """Create a new contact person"""
        try:
            if self.is_displayed(self.locator["add_new_contact_button"]):
                self.click_element(self.locator["add_new_contact_button"])
                time.sleep(3)
                self.click_element(self.locator["contact_name_txt_field"])
                self.send_keys(self.locator["contact_name_txt_field"], contact_person.get('name'))
                self.click_element(self.locator["contact_email_txt_field"])
                self.send_keys(self.locator["contact_email_txt_field"], contact_person.get('email'))
                self.click_element(self.locator["contact_phone_txt_field"])
                self.send_keys(self.locator["contact_phone_txt_field"], contact_person.get('phone'))
                self.click_element(self.locator["create_contact_button"])
                self.logger.info(f"Created new contact person: {contact_person.get('name')}")
            else:
                raise Exception(f"Add new contact button not found")
        except Exception as e:
            self.logger.error(f"Error creating new contact person: {e}")
            raise Exception(f"Unable to create new contact person: {contact_person}")
        

    def fill_remaining_fields(self, row):
        """Fill remaining course creation fields from test data"""
        try:
            self.logger.info("Starting to fill remaining course creation fields")
            filled_fields = []

            # Fill organizer if provided
            if row.get("organizer"):
                self.logger.debug(f"Setting organizer: {row['organizer']}")
                self.select_organizers(row["organizer"])
                filled_fields.append("organizer")

            # Fill contact person if provided
            if row.get("contact_person"):
                self.logger.debug(f"Setting contact person: {row['contact_person']}")
                self.select_contact_person(row["contact_person"])
                filled_fields.append("contact_person")

            # Select timezone if provided
            if row.get("timezone"):
                self.logger.debug(f"Setting timezone: {row['timezone']}")
                self.select_timezone(row["timezone"])
                filled_fields.append("timezone")

            # Fill date/time if provided
            if row.get("date1") and row.get("start_time1"):
                self.logger.debug(f"Setting date/time: {row['date1']} {row['start_time1']}")
                self.enter_date_time(row["date1"], row["start_time1"], row.get("end_time1", ""))
                filled_fields.append("date_time")

            # Select AOL center if provided
            if row.get("aol_center"):
                self.logger.debug(f"Setting AOL center: {row['aol_center']}")
                self.select_aol_center(row["aol_center"])
                filled_fields.append("aol_center")

            self.logger.info(f"Successfully filled fields: {', '.join(filled_fields)}")

        except Exception as e:
            self.logger.error(f"Error filling remaining fields: {e}")
            raise Exception(f"Unable to fill remaining fields: {e}")

    def is_publish_button_enabled(self):
        """Check if publish button is enabled"""
        try:
            # This would check if the publish/submit button is clickable/enabled
            # For now, we'll assume it's enabled if visible
            return self.is_displayed(self.locator.get("publish_button", "submit_button"))
        except Exception as e:
            self.logger.error(f"Error checking publish button state: {e}")
            return False

    def is_publish_button_disabled(self):
        """Check if publish button is disabled"""
        try:
            # Return the opposite of enabled
            return not self.is_publish_button_enabled()
        except Exception as e:
            self.logger.error(f"Error checking publish button disabled state: {e}")
            return True

    def click_publish_button(self):
        """Click publish/submit button"""
        try:
            publish_button = self.locator.get("publish_button", "submit_button")
            self.click_element(publish_button)
            self.logger.info("Clicked publish button")
        except Exception as e:
            self.logger.error(f"Error clicking publish button: {e}")
            raise Exception("Unable to click publish button")

    def enter_date_time(self, date, start_time, end_time=""):
        """Enter date and time for course"""
        try:
            # Select date
            if date:
                self.click_element(self.locator["start_date_field"])
                self.send_keys(self.locator["start_date_field"], date)

            # Select start time
            if start_time:
                self.click_element(self.locator["start_time_field"])
                self.send_keys(self.locator["start_time_field"], start_time)

            # Select end time if provided
            if end_time:
                self.click_element(self.locator["end_time_field"])
                self.send_keys(self.locator["end_time_field"], end_time)

            self.logger.info(f"Entered date/time: {date} {start_time}-{end_time}")

        except Exception as e:
            self.logger.error(f"Error entering date/time: {e}")
            raise Exception(f"Unable to enter date/time: {date} {start_time}")



    def select_timezone(self, value):
        try:
            self.logger.info(f"Selecting time zone: {value}")
            self.scroll_to_element(self.locator["scroll"], self.locator["timezone_txt_field"])
            self.click_element(self.locator["timezone_txt_field"])
            self.enter_search_field_value(self.locator["timezone_dropdown"], value)
            time.sleep(3)
            timezone_result = self.build_locator(self.locator["search_result"], value)
            if self.is_displayed(timezone_result, timeout=10):
                self.click_element(timezone_result)
            elif self.is_displayed(self.locator["no_result_msg"], timeout=10):
                self.logger.error(f"Timezone not found: {value}")
                raise Exception(f"Timezone '{value}' not found")
            else:
                raise Exception("Unexpected search result")

            self.logger.info(f"Successfully selected time zone: {value}")

        except Exception as e:
            self.logger.error(f"Failed to select time zone {value}: {e}")
            raise Exception(f"Unable to select time zone as {value}")

    def enter_existing_address(self, value: str, tenant: str):
        """
        Select an existing address/location from dropdown.
        
        Args:
            value: Address/location name to select
            tenant: Tenant identifier for field label lookup
        """
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["LocationDropDown"], ensure=True)
            self.click_element(self.locator["LocationDropDown"])
            
            config = self._get_tenant_config(tenant)
            search_label = config.field_labels.location_search
            # first_option_label = config.field_labels.first_location
            
            location_searchBox = self.build_locator(self.locator["Location_searchBox"], search_label)
            location_result = self.build_locator(self.locator["search_result"], value)
            
            self.logger.debug(f"Using location labels - search: {search_label}, first: {value}")

            self.enter_search_field_value(location_searchBox, value)
            time.sleep(3)
            
            if self.is_displayed(location_result, timeout=10):
                self.click_element(location_result)
            elif self.is_displayed(self.locator["no_result_msg"], timeout=10):
                raise Exception(f"Location not found: {value}")
            else:
                raise Exception("Unexpected search result")

            self.logger.info(f"Successfully selected location: {value}")

        except Exception as e:
            raise Exception(f"Unable to enter address as {value}: {e}")
    
    def enter_addressName(self,value):
        try:
            self.click_element(self.locator["addressName_txt_field"])
            self.send_keys(self.locator["addressName_txt_field"], value)
        except:
            raise Exception(f"Unable to enter address name as {value}")

    def enter_address(self,value):
        try:
            self.click_element(self.locator["Streest_Address_txt_field"])
            self.send_keys(self.locator["Streest_Address_txt_field"], value)
        except:
            raise Exception(f"Unable to enter address as {value}")

    def enter_city(self, value: str, tenant: str):
        """
        Enter city value.
        
        Args:
            value: City name
            tenant: Tenant identifier for field label lookup
        """
        try:
            config = self._get_tenant_config(tenant)
            city_label = config.field_labels.city
            city_txt_field = self.build_locator(self.locator["city_txt_field"], city_label)
            
            self.logger.debug(f"Using city label: {city_label}")
            self.click_element(city_txt_field)
            self.send_keys(city_txt_field, value)
        except Exception as e:
            raise Exception(f"Unable to enter city as {value}: {e}")

    def enter_zipcode(self, value: str, tenant: str):
        """
        Enter zipcode/pincode value.
        
        Args:
            value: Zipcode/Pincode
            tenant: Tenant identifier for field label lookup
        """
        try:
            config = self._get_tenant_config(tenant)
            zipcode_label = config.field_labels.zipcode
            zipcode_txt_field = self.build_locator(self.locator["zipcode_txt_field"], zipcode_label)
            
            self.logger.debug(f"Using zipcode label: {zipcode_label}")
            self.click_element(zipcode_txt_field)
            self.send_keys(zipcode_txt_field, value)
        except Exception as e:
            raise Exception(f"Unable to enter zipcode as {value}: {e}")

    def select_state(self, value):
        try:
            self.click_element(self.locator["state_txt_field"])
            time.sleep(2)
            self.send_keys(self.locator["search"], value, timeout=10, is_necessary=False)
            self.driver.press_keycode(66) if self.platform == "android" else self.driver.hide_keyboard(key_name='Done')
            state = self.build_locator(self.locator["centerOrState"], value)
            time.sleep(2)
            self.click_element(state, 10)
        except:
            raise Exception(f"Unable to select state as {value}")

    def select_aol_center(self, value: str):
        """
        Select AOL center from dropdown (US tenant).
        
        Args:
            value: AOL center name to select
        """
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["aol_center_select_dropdown"])
            self.click_element(self.locator["aol_center_select_dropdown"])

            self.enter_search_field_value(self.locator["aol_center_searchBox"], value)
            time.sleep(3)
            aol_center_result = self.build_locator(self.locator["search_result"], value)
            if self.is_displayed(aol_center_result, timeout=10):
                self.click_element(aol_center_result)
            elif self.is_displayed(self.locator["no_result_msg"], timeout=10):
                raise Exception(f"AOL center not found: {value}")
            else:
                raise Exception("Unexpected search result")

            self.logger.info(f"Successfully selected AOL center: {value}")
        except Exception as e:
            raise Exception(f"Unable to select aol center as {value}: {e}")

    def enter_apex(self, value: str):
        """
        Select apex from dropdown (India tenant).
        
        Args:
            value: Apex value to select
        """
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["apex_select_dropdown"])
            self.click_element(self.locator["apex_select_dropdown"])
            apex_option = self.build_locator(self.locator["item"], value)
            time.sleep(2)
            if self.is_displayed(apex_option, timeout=10):
                self.click_element(apex_option)
            else:
                raise Exception(f"Apex option not found: {value}")
            self.logger.info(f"Successfully selected Apex: {value}")
        except Exception as e:
            raise Exception(f"Unable to select apex as {value}: {e}")

    def enter_ic(self, value: str):
        """
        Select IC from dropdown (India tenant).
        
        Args:
            value: IC value to select
        """
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["ic_select_dropdown"])
            self.click_element(self.locator["ic_select_dropdown"])
            ic_option = self.build_locator(self.locator["item"], value)
            time.sleep(2)
            if self.is_displayed(ic_option, timeout=10):
                self.click_element(ic_option)
            else:
                raise Exception(f"IC option not found: {value}")
            self.logger.info(f"Successfully selected IC: {value}")
        except Exception as e:
            raise Exception(f"Unable to select IC as {value}: {e}")

    def enter_contribution(self, value: str):
        """
        Select contribution from dropdown (India tenant).
        
        Args:
            value: Contribution value to select
        """
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator["contribution_select_dropdown"])
            self.click_element(self.locator["contribution_select_dropdown"])
            contribution_option = self.build_locator(self.locator["item"], value)
            time.sleep(2)
            if self.is_displayed(contribution_option, timeout=10):
                self.click_element(contribution_option)
            else:
                raise Exception(f"Contribution option not found: {value}")
            self.logger.info(f"Successfully selected Contribution: {value}")
        except Exception as e:
            raise Exception(f"Unable to select contribution as {value}: {e}")

    def select_contact_person(self, contact_names: str):
        try:

            self.logger.info(f"Selecting contact person: {contact_names}")

            for name in contact_names:
                try:
                    search_box = self.locator["search"]
                    self.click_element(search_box)
                    self.enter_search_field_value(search_box, name)
                    time.sleep(3)
                    contact_person = self.build_locator(self.locator["search_result"], name)
                    if self.is_displayed(contact_person, timeout=10):
                        self.click_element(contact_person)
                        self.logger.info(f"Contact person selected: {name}")
                    elif self.is_displayed(self.locator["no_result_msg"], timeout=10):
                        raise Exception(f"Contact person not found: {name}")
                    else: 
                        raise Exception("Unexpected search result")

                except Exception as person_error:
                    self.logger.warning(f"Failed selecting contact person '{name}': {person_error}")

            self.logger.info(f"Successfully selected {len(contact_names)} contact persons")

        except Exception as e:
            self.logger.error(f"Error while selecting contact persons {contact_names}: {e}")
            raise


    def enable_notification_for_person(self,driver, locators, person_name):

        by, locator = self.get_locator(locators, "enable_notification_button", person_name)
        print(f"by: {by}, locator: {locator}")
        try:
            enable_btn = self.find_element((by, locator),20)
            self.click_element(enable_btn)
            self.logger.info(f"Notification enabled for {person_name}")
        except Exception as e:
            raise Exception(f"Unable to enable notification for {person_name}: {e}")

    def select_n_date(self, dates: list[str], defaultDays = 0, timezone: str = ""):
        print(f"dates:{dates}")
        try:
            for index, date_tobe_updated in enumerate(dates):
                self.logger.info(f"Selecting date {index+1}: {date_tobe_updated}")
                txtField = self.build_locator(self.locator["date_ith_txt_field"], index+1)
                self.scroll_to_element(self.locator["scroll"], txtField)
                self.click_element(txtField)
                self.click_element(self.locator["date_pencil"])
                self.click_element(self.locator["date_enter_field"])
                self.send_keys(self.locator["date_enter_field"], date_tobe_updated, timeout=10, is_necessary=False)
                ok = self.find_element(self.locator["option_ok"], 5)
                self.click_element(ok)
                if self.is_msg_displayed(self.event_create_message["past_date_msg"]):
                    self.logger.info(f"Date {index+1} is past date")
                    return self.event_create_message["past_date_msg"]
                if self.is_msg_displayed(self.event_create_message["out_of_range_err_msg"]):
                    self.logger.info(f"Date {index+1} is out of range")
                    return self.event_create_message["out_of_range_err_msg"]
                if self.is_msg_displayed(self.event_create_message["date_invalid_err_msg"]):
                    self.logger.info(f"Date {index+1} is invalid")
                    return self.event_create_message["date_invalid_err_msg"]
                else:
                    self.logger.info(f"Date {index+1} is valid")
                    if len(dates) > index + 1 and defaultDays == 0:
                        if self.is_displayed(self.locator['add_date']):
                            self.scroll_to_element(self.locator["scroll"], self.locator['add_date'])
                            self.click_element(self.locator['add_date'])
                        else:
                            self.scroll_to_element(self.locator["scroll"], self.locator['aol_center_txt_field'])
                            break
            self.logger.info("Completed selecting date")
            return "success"
        except Exception as e:
            raise Exception(f"Unable to select date: {e}")

    def select_n_time(self, times: list[tuple[str,str]]):
        print(f"times: {times}")
        try:
            for index, time_tobe_updated in enumerate(times):
                txtField = self.build_locator(self.locator['time_ith_txt_field'],index+1)
                self.scroll_to_element(self.locator["scroll"], txtField)
                self.click_element(txtField)
                valueHour = [time_tobe_updated[0].split()[0].split(":")[0], time_tobe_updated[1].split()[0].split(":")[0]]
                valueMin =  [time_tobe_updated[0].split()[0].split(":")[1], time_tobe_updated[1].split()[0].split(":")[1]]
                valuePeriod = [time_tobe_updated[0].split()[1], time_tobe_updated[1].split()[1]]
                for i in range(0,2):
                    # self.click_element(self.locator['time_keyboard'], 10)
                    hour = self.find_element(self.locator['time_hour'])
                    min = self.find_element(self.locator['time_min'])
                    period = self.build_locator(self.locator['time_period'], str(valuePeriod[i]))
                    self.click_element(hour)
                    self.send_keys(hour, valueHour[i], timeout=10, is_necessary=False)
                    self.click_element(min)
                    self.send_keys(min, valueMin[i], timeout=10, is_necessary=False)
                    self.click_element(period)
                    self.click_element(self.locator['option_ok'], 10)
            self.logger.info("Completed selecting time")
        except Exception as e:
            raise Exception(f"Unable to select time: {e}")

    def handle_date_and_time(self, event_dates: List[Dict[str, str]], timezone: str = "", 
                              tenant: str = "us", is_change_weekend_timing: bool = False, 
                              weekend_start_time: str = ""):
        """
        Handle date and time entry based on tenant configuration.
        
        Uses TenantConfig feature flags to determine workflow:
        - requires_end_time=True: Enter each date with both start and end time
        - requires_end_time=False: Enter start date/time only (end auto-populates)
        - has_weekend_timing=True: Handle weekend timing checkbox
        
        Args:
            event_dates: List of date/time dictionaries
            timezone: Timezone string (for US tenant)
            tenant: Tenant identifier
            is_change_weekend_timing: Whether to change weekend timing (India)
            weekend_start_time: Weekend start time if different (India)
        """
        if not event_dates:
            return "success"

        config = self._get_tenant_config(tenant)
        
        if config.features.requires_end_time:
            # US-style: Multiple dates with explicit start and end times
            dates = [event["date"] for event in event_dates]
            times = [(event["start_time"], event["end_time"]) for event in event_dates]
            return self.select_n_date_and_time_us(dates, times, timezone)
        else:
            # India-style: Single start date/time, auto-populated end time
            start_date = event_dates[0]["date"]
            start_time = event_dates[0]["start_time"]
            return self.select_date_and_time_india(start_date, start_time, weekend_start_time, is_change_weekend_timing)

            
    def select_date_and_time_india(self, start_date: str, start_time: str,weekend_start_time: str = "", is_change_weekend_timing: bool = False):
        try:
            self.logger.info(f"Setting India tenant date and time")

            # Start Date
            self.logger.info(f"Selecting start date: {start_date}")
            self.scroll_to_element_by_touch(self.locator["start_date"])
            self.click_element(self.locator["start_date"])
            self.click_element(self.locator["date_pencil"])
            self.click_element(self.locator["date_enter_field"])
            self.send_keys(self.locator["date_enter_field"], start_date, timeout=10, is_necessary=False)
            ok = self.find_element(self.locator["option_ok"], 5)
            self.click_element(ok)
            if self.is_msg_displayed(self.event_create_message["past_date_msg"]):
                self.logger.info(f"Date is past date")
                return self.event_create_message["past_date_msg"]
            if self.is_msg_displayed(self.event_create_message["out_of_range_err_msg"]):
                self.logger.info(f"Date is out of range")
                return self.event_create_message["out_of_range_err_msg"]
            if self.is_msg_displayed(self.event_create_message["date_invalid_err_msg"]):
                self.logger.info(f"Date is invalid")
                return self.event_create_message["date_invalid_err_msg"]
            self.logger.info(f"Date is valid")


            self.logger.info(f"Start date set: {start_date}")

            # Start Time
            self.click_element(self.locator["start_time"])

            hour = start_time.split()[0].split(":")[0]
            minute = start_time.split()[0].split(":")[1]
            period = start_time.split()[1]

            # self.click_element(self.locator["time_keyboard"], 10)
            hour_ele = self.find_element(self.locator["time_hour"])
            min_ele = self.find_element(self.locator["time_min"])
            period_ele = self.build_locator(self.locator["time_period"], period)

            self.click_element(hour_ele)
            self.send_keys(hour_ele, hour, timeout=10, is_necessary=False)
            self.click_element(min_ele)
            self.send_keys(min_ele, minute, timeout=10, is_necessary=False)
            self.click_element(period_ele)
            self.click_element(self.locator["option_ok"], 10)
            self.logger.info(f"Start time set: {start_time}")

            # Handle weekend timing
            if is_change_weekend_timing:
                # Uncheck "Same as weekdays"
                self.scroll_to_element_by_touch(self.locator["same_as_weekdays_checkbox"])
                if self.is_displayed(self.locator["same_as_weekdays_checkbox"]):
                    self.click_element(self.locator["same_as_weekdays_checkbox"])
                    self.logger.info(f"Same as weekdays checkbox clicked - weekend uses same timing")
                    if weekend_start_time:
                        # Enter different weekend start time (end time auto-populates for India)
                        self.scroll_to_element_by_touch(self.locator["weekend_start_time"])
                        self.click_element(self.locator["weekend_start_time"])
                        self.logger.info(f"Entering weekend start time: {weekend_start_time}")

                        hour = weekend_start_time.split()[0].split(":")[0]
                        minute = weekend_start_time.split()[0].split(":")[1]
                        period = weekend_start_time.split()[1]

                        # self.click_element(self.locator["time_keyboard"], 10)
                        hour_ele = self.find_element(self.locator["time_hour"])
                        min_ele = self.find_element(self.locator["time_min"])
                        period_ele = self.build_locator(self.locator["time_period"], period)

                        self.click_element(hour_ele)
                        self.send_keys(hour_ele, hour, timeout=10, is_necessary=False)
                        self.click_element(min_ele)
                        self.send_keys(min_ele, minute, timeout=10, is_necessary=False)
                        self.click_element(period_ele)
                        self.click_element(self.locator["option_ok"], 10)
                        self.logger.info(f"Weekend start time set: {weekend_start_time}")
                    else:
                        self.logger.info(f"No weekend time specified, skipping weekend time entry")
                else:
                    self.logger.info(f"Same as weekdays checkbox is not displayed")
            else:
                self.logger.info(f"Same as weekdays true, skipping weekend time entry")
            return "success"

        except Exception as e:
            raise Exception(f"Unable to set India tenant date/time: {e}")

    def select_n_date_and_time_us(self, dates: list[str], times: list[tuple[str, str]], timezone: str = ""):
        """
        US Tenant: For each of the N days: enter date, enter both start and end time, 
        then click Add Date (except after the last day).
        """
        print(f"[US] dates: {dates}, times: {times}")

        try:
            num_days = len(dates)

            if num_days != len(times):
                raise Exception(f"dates and times length mismatch: {num_days} dates vs {len(times)} times")

            for index in range(num_days):
                slot = index + 1
                date_tobe_updated = dates[index]
                time_tobe_updated = times[index]

                start_time = time_tobe_updated[0] if len(time_tobe_updated) > 0 else ""
                end_time = time_tobe_updated[1] if len(time_tobe_updated) > 1 else ""

                self.logger.info(
                    f"[US] Day {slot}/{num_days}: date={date_tobe_updated}, start_time={start_time}, end_time={end_time}"
                )

                # ✅ Case 1: both date and time empty → skip بالكامل
                if not date_tobe_updated and not start_time and not end_time:
                    self.logger.info(f"Skipping slot {slot} as both date and time are empty")
                    continue

                # =========================
                # ✅ ENTER DATE (only if present)
                # =========================
                if date_tobe_updated:
                    txtField = self.build_locator(self.locator["date_ith_txt_field"], slot)
                    self.scroll_to_element_by_touch(txtField)
                    self.click_element(txtField)
                    self.logger.info(f"Date {slot} field clicked")

                    self.click_element(self.locator["date_pencil"])
                    self.logger.info(f"Date {slot} pencil clicked")

                    self.click_element(self.locator["date_enter_field"])
                    self.send_keys(self.locator["date_enter_field"], date_tobe_updated, timeout=10, is_necessary=False)

                    ok = self.find_element(self.locator["option_ok"], 5)
                    self.click_element(ok)

                    # Validation checks
                    if self.is_msg_displayed(self.event_create_message["past_date_msg"]):
                        self.logger.info(f"Date {slot} is past date")
                        return self.event_create_message["past_date_msg"]

                    if self.is_msg_displayed(self.event_create_message["out_of_range_err_msg"]):
                        self.logger.info(f"Date {slot} is out of range")
                        return self.event_create_message["out_of_range_err_msg"]

                    if self.is_msg_displayed(self.event_create_message["date_invalid_err_msg"]):
                        self.logger.info(f"Date {slot} is invalid")
                        return self.event_create_message["date_invalid_err_msg"]

                    self.logger.info(f"Date {slot} is valid")

                # =========================
                # ✅ ENTER TIME (only if BOTH start & end exist)
                # =========================
                if start_time and end_time:
                    try:
                        time_txt_field = self.build_locator(self.locator["time_ith_txt_field"], slot)
                        self.scroll_to_element_by_touch(time_txt_field)
                        self.click_element(time_txt_field)
                        self.logger.info(f"Time {slot} field clicked")

                        valueHour = [
                            start_time.split()[0].split(":")[0],
                            end_time.split()[0].split(":")[0]
                        ]
                        valueMin = [
                            start_time.split()[0].split(":")[1],
                            end_time.split()[0].split(":")[1]
                        ]
                        valuePeriod = [
                            start_time.split()[1],
                            end_time.split()[1]
                        ]

                        for i in range(2):  # start & end
                            hour = self.find_element(self.locator["time_hour"])
                            min_ele = self.find_element(self.locator["time_min"])
                            period = self.build_locator(self.locator["time_period"], str(valuePeriod[i]))

                            self.click_element(hour)
                            self.send_keys(hour, valueHour[i], timeout=10, is_necessary=False)

                            self.click_element(min_ele)
                            self.send_keys(min_ele, valueMin[i], timeout=10, is_necessary=False)

                            self.click_element(period)

                            self.logger.info(f"Time {slot} set: {start_time if i == 0 else end_time}")

                            self.click_element(self.locator["option_ok"], 10)

                    except Exception as e:
                        raise Exception(f"Invalid time format for slot {slot}: {time_tobe_updated} | Error: {e}")

                else:
                    self.logger.info(f"Skipping time entry for slot {slot} (missing start/end time)")

                # =========================
                # ✅ Add next date slot
                # =========================
                if index < num_days - 1:
                    self.scroll_to_element_by_touch(self.locator["add_date"])
                    self.click_element(self.locator["add_date"])
                    self.logger.info("Clicked Add Date for next slot")

            self.logger.info(f"[US] Completed selecting {num_days} date(s) and time(s)")
            return "success"

        except Exception as e:
            raise Exception(f"Unable to select date and time (US): {e}")

    def select_date_from_the_calender(self, formattedDate, defaultDays = 0):
        try:
            txtField = self.build_locator(self.locator['date_ith_txt_field'], "1")
            self.scroll_to_element(self.locator["scroll"], txtField)
            self.click_element(txtField)
            locator = self.build_locator(self.locator['calender_date'], formattedDate)
            self.click_element(locator)
            time.sleep(2)
            self.click_element(self.locator["option_ok"])
        except:
            raise Exception(f"Unable to select date from calendar")

    @allure.step("Tap Create  button")
    def click_create_button(self):
        try:
            self.scroll_to_element(self.locator["scroll"], self.locator['create_button'])
            self.click_element(self.locator['create_button'])
        except:
            raise Exception(f"Unable to click Create button")

    def is_add_date_button_available(self):
        """Check if Add Date button is available on the page"""
        try:
            self.logger.info("Checking if Add Date button is available")
            is_available = self.is_displayed(self.locator['add_date'], timeout=5)
            self.logger.info(f"Add Date button availability: {is_available}")
            return is_available
        except Exception as e:
            self.logger.error(f"Error checking Add Date button availability: {e}")
            return False

    def get_text_from_mark_attendance_text_field(self):
        return self.get_input_value(self.locator['max_attendees_txt_field'])

    def is_msg_displayed(self, msg: str):
        try:
            msgLoc = self.build_locator(self.locator['msg'], msg)
            if self.is_displayed(msgLoc): return True
            else: return False
        except:
            return False

    def is_error_message_displayed(self, message):
        errMsg = self.build_locator(self.locator['msg'], message)
        try:
            self.scroll_to_element(self.locator['scroll'], errMsg, direction="up")
            return self.is_displayed(errMsg)
        except:
            return False

    def is_zipcode_error_msg_displayed(self):
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator['zipcode_err_msg'], direction="up")
            return self.is_displayed(self.locator['zipcode_err_msg'])
        except Exception as e:
            self.logger.error(f"Exception in method: {e}")
            return False

    def is_city_error_msg_displayed(self):
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator['city_err_msg'], direction="up")
            return self.is_displayed(self.locator['city_err_msg'])
        except:
            return False

    def is_address_err_msg_displayed(self):
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator['address_err_msg'], direction="up")
            return self.is_displayed(self.locator['address_err_msg'])
        except Exception as e:
            return False

    def is_teacher_err_msg_displayed(self):
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator['teacher_err_msg'], direction="up")
            return self.is_displayed(self.locator['teacher_err_msg'])
        except:
            return False

    def is_max_attendees_err_msg_displayed(self):
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator['max_attendees_err_msg'], direction="up")
            return self.is_displayed(self.locator['max_attendees_err_msg'])
        except:
            return False

    def is_max_attendees_zero_err_msg_displayed(self):
        try:
            return self.is_msg_displayed(self.event_create_message["max_attendees_zero_msg"])
        except Exception as e:
            self.logger.error(f"Error checking max attendees zero error message: {e}")
            return False

    def is_datetime_err_displayed(self):
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator['datetime_err_msg'])
            return self.is_displayed(self.locator['datetime_err_msg'])
        except Exception as e:
            return False

    def is_timezone_err_msg_displayed(self):
        try:
            self.scroll_to_element(self.locator['scroll'], self.locator['timezone_err_msg'])
            return self.is_displayed(self.locator['timezone_err_msg'])
        except Exception as e:
            return False

    def scroll_to_create_now_button(self):
        self.scroll_to_element(self.locator['scroll'], self.locator['create_now'])

    def create_course(self, row: Dict[str, Any],message: str) -> str:
        """
        Create a course based on the provided test data row.
        
        Uses TenantConfig for all tenant-specific logic. The workflow is:
        1. Parse row data into CourseData object
        2. Select event mode and course
        3. Configure privacy settings
        4. Select team members (tenant-specific: languages, teaching assistants, volunteers)
        5. Handle notifications and contact persons
        6. Set timezone (US only)
        7. Configure date/time (tenant-specific workflow)
        8. Handle address (for in-person events)
        9. Set max attendees and center/apex details
        10. Submit and verify result
        
        Args:
            row: Dictionary containing course creation data from CSV
            
        Returns:
            Result string indicating success or failure with details
        """
        test_case_id = row.get("Test Case ID", "N/A")
        
        try:
            # Parse row data using CourseData dataclass
            data = CourseData.from_row(row)
            config = self._get_tenant_config(data.tenant)
            
            self.logger.info(f"Processing Test Case: {data.test_case_id} for tenant: {data.tenant}")
            
            # Step 1: Select event mode
            if data.event_mode:
                self.select_event_mode(data.event_mode)
                self.logger.info(f"Selected event mode: {data.event_mode}")
            
            # Step 2: Select course
            if data.product_name:
                self.select_product(data.product_name, data.tenant)
                self.logger.info(f"Selected course: {data.product_name}")
            
            # Step 3: Set privacy
            self.check_is_private(data.is_private, data.tenant)
            self.logger.info(f"Private course: {data.is_private}")

            # Step 4: Select languages (India tenant only)
            if config.features.has_languages and data.languages:
                self.select_n_languages(data.languages)
                self.logger.info(f"Selected languages: {data.languages}")

            # Step 5: Select teachers
            if data.teachers:
                self.select_n_teachers(data.teachers)
                self.logger.info(f"Selected teachers: {data.teachers}")
            
            # Step 6: Select organizers
            if data.organizers:
                self.select_n_organizers(data.organizers)
                self.logger.info(f"Selected organizers: {data.organizers}")

            # Step 7: Select teaching assistants (India tenant only)
            if config.features.has_teaching_assistants and data.teaching_assistants:
                self.select_n_teaching_assistants(data.teaching_assistants)
                self.logger.info(f"Selected teaching assistants: {data.teaching_assistants}")

            # Step 8: Select volunteers (India tenant only)
            if config.features.has_volunteers and data.volunteers:
                self.select_n_volunteers(data.volunteers)
                self.logger.info(f"Selected volunteers: {data.volunteers}")

            # Step 9: Handle notifications
            if data.notify_persons:
                self._handle_notifications(data.notify_persons)

            # Step 10: Handle contact persons
            self._handle_contact_persons(data, config)

            # Step 11: Select timezone (US tenant only)
            if config.features.has_timezone_selection and data.timezone:
                self.select_timezone(data.timezone)
                self.logger.info(f"Selected timezone: {data.timezone}")

            # Step 12: Handle date and time
            if data.event_dates:
                result = self.handle_date_and_time(
                    data.event_dates, 
                    data.timezone, 
                    data.tenant, 
                    data.is_change_weekend_timing, 
                    data.weekend_start_time
                )
                if result != "success":
                    return result
                self.logger.info(f"Set date(s) and time(s) for tenant: {data.tenant}")

            # Step 13: Handle address (for in-person events)
            if data.event_mode.lower() == 'in-person':
                self._handle_address(data)

            # Step 14: Enter max attendees
            if data.max_attendees:
                self.enter_max_attendees(data.max_attendees, data.tenant)
                self.logger.info(f"Max attendees: {data.max_attendees}")

            # Step 15: Handle center/apex/ic/contribution
            self._handle_center_details(data, config)
            
            # Step 16: Submit course
            self.click_create_button()
            time.sleep(1)

            content = self.extract_page_contents()
            print("contents in meetup success page:",content)
            result = message in content
            self.logger.info(f"Testcase:{test_case_id} is {'passed' if result else 'failed'}")
            self.logger.info(f"Observed Screen content: {content}")
            return result, self.__get_error_message(result)
        except Exception as e:
            self.logger.info(f"Observed Screen content: {content}")
            return False, f'Testcase:{test_case_id} is failed due to {str(e)}'
            
    def get_final_error_msg(self):
        try:
            return self.get_txt_from_attr(self.locator["final_msg"]), "Unable to get the Final Error message"
        except Exception as e:
            self.logger.error(f"Exception raised while getting the final page error message, exception:: {str(e)}")
            return False, f"Unable to get the Final Error message"

    def __get_error_message(self, result):
        if result == False:
            message, expMsg = self.get_final_error_msg()
            return f"{message}"
        else:
            return f"Observed Content::{self.extract_page_contents()}"

    
    def _handle_notifications(self, notify_persons: List[str]):
        """Handle notification settings for persons."""
        self.logger.info("Clicking add notifications button")
        self.scroll_to_element_by_touch(self.locator["add_notifications_button"])
        self.click_element(self.locator["add_notifications_button"])
        
        for person in notify_persons:
            self.enable_notification_for_person(self.driver, self.locator, person)
            self.logger.info(f"Selected notify person: {person}")
        
        self.click_element(self.locator["back_button"])
        self.logger.info("Clicked back button")
    
    def _handle_contact_persons(self, data: CourseData, config: TenantConfiguration):
        """Handle contact person selection or creation."""
        if not data.contact_persons and not data.new_contact_person:
            self.logger.warning("No contact person selected")
            return 

        self.scroll_to_element(self.locator["scroll"], self.locator["add_point_of_contact_button"])
        element = self.find_element(self.locator["add_point_of_contact_button"])
        location = element.location
        size = element.size
        x = location['x'] + 10
        y = location['y'] + size['height'] // 2
        self.driver.tap([(x, y)])
        self.logger.info("Clicked add point of contact button")
        time.sleep(3)
        
        if data.mode_of_select_contact == "ByCreatingNewContact" and config.features.can_create_new_contact:
            self.logger.info(f"Creating new contact person for tenant: {data.tenant}")
            self.create_new_contact_person(data.new_contact_person)
            self.logger.info(f"Entered contact person: {data.new_contact_person}")
            time.sleep(3)
        elif data.mode_of_select_contact == "BySearch":
            self.logger.info("Selecting contact person by search")
            contact_persons = data.contact_persons if data.contact_persons else []
            self.select_contact_person(contact_persons)
            self.logger.info(f"Selected contact persons: {contact_persons}")
        elif data.mode_of_select_contact == "ByExistingTeam":
            self.logger.info("Selecting contact person from existing team")
            contact_person = self.build_locator(self.locator["search_result"], data.contact_persons[0])
            if self.is_displayed(contact_person, timeout=10):
                self.click_element(contact_person)
                self.logger.info("Selected contact person from existing team")
            else:
                raise Exception("Contact person not found in existing team")
        
        self.click_element(self.locator["done_button"], 10)
        self.logger.info("Clicked done button")
    
    def _handle_address(self, data: CourseData):
        """Handle address entry for in-person events."""
        if data.is_use_existing_venue:
            if data.address_details.get("address"):
                self.enter_existing_address(data.address_details["address"], data.tenant)
                self.logger.info(f"Entered address: {data.address_details['address']}")
        else:
            self.scroll_to_element(self.locator["scroll"], self.locator["add_new_address_button"])
            self.click_element(self.locator["add_new_address_button"])
            self.logger.info("Clicked add new address button")
            
            if data.address_details.get("addressName"):
                self.enter_addressName(data.address_details["addressName"])
                self.logger.info(f"Entered address Name: {data.address_details['addressName']}")
            
            if data.address_details.get("zipcode"):
                self.enter_zipcode(data.address_details["zipcode"], data.tenant)
                self.logger.info(f"Entered zipcode: {data.address_details['zipcode']}")
            
            if data.address_details.get("city"):
                self.enter_city(data.address_details["city"], data.tenant)
                self.logger.info(f"Entered city: {data.address_details['city']}")

            if data.address_details.get("address"):
                self.enter_address(data.address_details["address"])
                self.logger.info(f"Entered address: {data.address_details['address']}")
            
            if self.is_displayed(self.locator["create_button"]):
                self.click_element(self.locator["create_button"])
                self.logger.info("Address created successfully")
            else:
                raise Exception("Done button not found for address creation")
            
            self.enter_existing_address(data.address_details["addressName"], data.tenant)
            self.logger.info(f"Entered address: {data.address_details['addressName']}")
    
    def _handle_center_details(self, data: CourseData, config: TenantConfiguration):
        """Handle AOL center (US) or apex/ic/contribution (India) details."""
        if config.features.has_aol_center:
            if data.aol_center:
                self.select_aol_center(data.aol_center)
                self.logger.info(f"Selected AOL center: {data.aol_center}")
        
        if config.features.has_apex_ic_contribution:
            if data.apex:
                self.enter_apex(data.apex)
                self.logger.info("Entered apex")
            if data.ic:
                self.enter_ic(data.ic)
                self.logger.info("Entered ic")
            if data.contribution:
                self.enter_contribution(data.contribution)
                self.logger.info("Entered contribution")
    
    def _verify_course_creation_result(self, test_case_id: str) -> str:
        """Verify course creation result and return appropriate message."""
        if self.is_msg_displayed(self.event_create_message["course_create_success_msg"]):
            result_text = f"Success - Course created successfully for test case: {test_case_id}"
            self.logger.info(result_text)
            return result_text
        
        error_messages = self._collect_error_messages()
        
        if error_messages:
            result_text = f"Unable to create course - {'; '.join(error_messages)} for test case: {test_case_id}"
        else:
            result_text = f"Unable to create course - Unknown error occurred for test case: {test_case_id}"
        
        self.logger.info(result_text)
        return result_text
    
    def _collect_error_messages(self) -> List[str]:
        """Collect all displayed error messages."""
        error_messages = []
        common_errors = [
            "teacher_conflict_msg", "product_error_msg", "center_err_msg",
            "contact_err_msg", "past_date_msg", "invalid_attendee_count_msg",
            "teacher_err_msg", "datetime_err_msg", "address_err_msg",
            "city_err_msg", "zipcode_err_msg", "state_err_msg",
            "timezone_err_msg", "max_attendees_err_msg", "out_of_range_err_msg",
            "date_invalid_err_msg",
        ]
        
        for error_key in common_errors:
            error_msg = self.event_create_message.get(error_key, "")
            if error_msg and self.is_msg_displayed(error_msg):
                error_messages.append(f"Error: {error_msg}")
        
        return error_messages

    def isStatusCancelledDisplayed(self,event_code):
        self.logger.info(f"Checking if course is displayed on the UI")
        event_elements = self.get_all_event_cards(self.locator["event_cards"])
        if not event_elements:
            raise Exception("No event cards found")

        for el in event_elements:
            desc = el.get_attribute("content-desc")
            event_data = self.parse_event_data(desc)
            if event_data["code"] == event_code:
                if event_data["status"] == "canceled":
                    self.logger.info(f"Course with event code {event_code} is cancelled")
                    return True
                else:
                    self.logger.error(f"Course with event code {event_code} is not cancelled")
                    return False
        self.logger.error(f"Course with event code {event_code} not found on the UI")


    def get_validation_errors(self) -> list:
        """
        Helper method to collect all current validation errors on the page
        Returns list of error descriptions
        """
        errors = []
        
        if self.is_teacher_err_msg_displayed():
            errors.append("Teacher selection required")
        
        if self.is_max_attendees_err_msg_displayed():
            errors.append("Invalid max attendees value")
        
        if self.is_datetime_err_displayed():
            errors.append("Date/time validation error")
        
        if self.is_address_err_msg_displayed():
            errors.append("Invalid address")
        
        if self.is_city_error_msg_displayed():
            errors.append("Invalid city")
        
        if self.is_zipcode_error_msg_displayed():
            errors.append("Invalid zipcode")
        
        return errors

    def cancel_course(self, eventCode):
        searchButton = self.locator["search_button"]
        searchField = self.locator["search"]
        self.logger.info(f"Cancelling course with event code: {eventCode}")
        self.enterEventCode(eventCode,searchButton, searchField)
        self.click_event_row_containing(self.locator["event_row_contains"], eventCode)
        self.click_element(self.locator["Event_option_button"])
        self.click_element(self.locator["Cancel_course_button"])
        self.click_element(self.locator["confirm_button"])
        assert self.is_msg_displayed(
            self.event_create_message["course_cancel_success_msg"]
        ), "Course cancellation success message not displayed"
        self.click_element(self.locator["Events_search_close_button"])

    
    def validate_cancel_course(self, eventCode):
        self.logger.info(f"Validating course cancellation with event code: {eventCode}")
        self.enterEventCode(eventCode,self.locator["search_button"], self.locator["search"])
        isCancelled = self.isStatusCancelledDisplayed(eventCode)
        if isCancelled:
            self.logger.info(f"Course cancellation validation result: {isCancelled}")
            return True
        else:
            self.logger.error(f"Course cancellation validation result: {isCancelled}")
            return False

    def get_course_details_page(self, event_code,data: dict):
        self.logger.info(f"Getting course details page for event code: {event_code}")   
        self.enterEventCode(event_code)
        self.click_event_row_containing(self.locator["event_row_contains"], event_code)
        return self.course_details.verify_course_details(data)