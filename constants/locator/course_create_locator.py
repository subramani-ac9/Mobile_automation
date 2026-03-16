from appium.webdriver.common.appiumby import AppiumBy
from typing import Tuple, Callable, Union

# Type alias for locator tuple
LocatorType = Tuple[str, Union[str, Callable[[str], str]]]


class LocatorBuilder:
    """
    Helper class to build dynamic locators based on tenant configuration.
    Use this to construct locators with tenant-specific field labels.
    """
    
    @staticmethod
    def build_xpath_for_field(field_label: str, suffix: str = "") -> str:
        """Build XPATH for a field following the standard pattern."""
        return f'(//android.view.View[@content-desc="{field_label}{suffix}"]/following-sibling::android.widget.EditText)[1]'
    
    @staticmethod
    def build_xpath_for_dropdown(field_label: str, suffix: str = "") -> str:
        """Build XPATH for a dropdown following the standard pattern."""
        return f'(//android.view.View[@content-desc="{field_label}{suffix}"]/following-sibling::android.view.View)[1]'


class CourseCreateLocator:
    """
    Locators for course creation page.
    
    Locators with lambda functions are dynamic and should be built using
    build_locator() method in the page object.
    
    For tenant-specific locators, use the TenantConfig to get the correct
    field label before building the locator.
    """
    
    android = {
        # Event mode and course selection
        "event_mode": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "course_dropdown": (AppiumBy.ACCESSIBILITY_ID, 'Program Select Dropdown'),
        "item": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "centerOrState": (AppiumBy.XPATH, lambda val: f'//android.view.View[contains(@content-desc, "{val}")]'),
        
        # Private checkbox - uses tenant-specific label
        "is_private": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        
        # Language selection (India tenant only)
        "language_add_button": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Languages *"]/following-sibling::android.view.View)[1]'),
        "language_search_box": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Languages"]/following-sibling::android.widget.EditText)[1]'),
        "first_language_option": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        
        # Product/Program selection - uses tenant-specific label
        "product_txt_field": (AppiumBy.XPATH, lambda value: f'//android.view.View[@content-desc="{value}"]/following-sibling::android.widget.EditText[1]'),
        "first_product_name": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "no_result_msg": (AppiumBy.ACCESSIBILITY_ID, 'No results found'),
        
        # Max attendees - uses tenant-specific label
        "max_attendees_txt_field": (AppiumBy.XPATH, lambda value: f'//android.view.View[@content-desc="{value} *"]/following-sibling::android.widget.EditText[1]'),
        
        # Team member buttons
        "add_teacher": (AppiumBy.ACCESSIBILITY_ID, 'Add Teacher Button'),
        "add_organizer": (AppiumBy.ACCESSIBILITY_ID, 'Add Organizer Button'),
        "add_teaching_assistant": (AppiumBy.ACCESSIBILITY_ID, 'Add Teaching Assistant Button'),
        "add_volunteer": (AppiumBy.ACCESSIBILITY_ID, 'Add Volunteer Button'),
        
        # Teacher selection
        "teacher_primary_txt_field": (AppiumBy.XPATH, '//android.widget.EditText'),
        "first_teacher_name": (AppiumBy.ACCESSIBILITY_ID, 'teacher 1'),
        "first_organizer_name": (AppiumBy.ACCESSIBILITY_ID, 'teacher 1'),
        "search_results_displayed": (AppiumBy.XPATH, '//android.view.View[@content-desc="Search results displayed"]'),
        "teacher_additional_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Select Teacher(Additional)...'),
        
        # Done and navigation buttons
        "done_button": (AppiumBy.ACCESSIBILITY_ID, 'Done Button'),
        "back_button": (AppiumBy.ACCESSIBILITY_ID, 'Back Button'),
        
        # Contact person
        "add_point_of_contact_button": (AppiumBy.ACCESSIBILITY_ID, 'Add Point of contact Button'),
        "add_new_contact_button": (AppiumBy.ACCESSIBILITY_ID, 'Add Contact Button'),
        "contact_name_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Name *"]/following-sibling::android.widget.EditText)[1]'),
        "contact_email_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Mail Id *"]/following-sibling::android.widget.EditText)[1]'),
        "contact_phone_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Mobile Number *"]/following-sibling::android.widget.EditText)[1]'),
        "create_contact_button": (AppiumBy.ACCESSIBILITY_ID, 'Create Contact Button'),
        "contact_searchBox": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Point of contact"]/following-sibling::android.view.View)[1]'),
        "first_contact_option": (AppiumBy.ACCESSIBILITY_ID, 'teacher 1'),
        
        # Notifications
        "add_notifications_button": (AppiumBy.ACCESSIBILITY_ID, 'Add Notifications Button'),
        "notification_person": (AppiumBy.XPATH, lambda name: f'//android.view.View[contains(@content-desc,"{name}")]'),
        "enable_notification_button": (AppiumBy.XPATH, lambda name: f'//android.view.View[contains(@content-desc,"{name}")]//android.widget.Button'),
        
        # Organizer
        "organizer_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Organizer(s) *"]/following-sibling::android.view.View)[1]'),
        
        # Timezone
        "timezone_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Timezone *"]/following-sibling::android.view.View)[1]'),
        "timezone_dropdown": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Timezone"]/following-sibling::android.widget.EditText)[1]'),
        "first_timezone_option": (AppiumBy.ACCESSIBILITY_ID, 'TimeZone 1'),
        
        # Date and time
        "add_date": (AppiumBy.XPATH, '//android.view.View[@content-desc="Add Date"]'),
        "start_date": (AppiumBy.XPATH, '//android.view.View[@content-desc="Start Date *"]/following-sibling::android.widget.Button[1]'),
        "start_time": (AppiumBy.XPATH, '//android.view.View[@content-desc="Weekdays"]/following-sibling::android.widget.Button[1]'),
        "weekend_start_time": (AppiumBy.XPATH, '//android.view.View[@content-desc="Weekend"]/following-sibling::android.widget.Button[1]'),
        "same_as_weekdays_checkbox": (AppiumBy.ACCESSIBILITY_ID, 'Same as Weekdays Checkbox'),
        
        # Location - uses tenant-specific labels
        "LocationDropDown": (AppiumBy.ACCESSIBILITY_ID, "Location Select Dropdown"),
        "Location_searchBox": (AppiumBy.XPATH, lambda value: f'(//android.view.View[@content-desc="{value}"]/following-sibling::android.widget.EditText)[1]'),
        "first_Location_option": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        
        # Address fields
        "add_new_address_button": (AppiumBy.ACCESSIBILITY_ID, 'Add Address'),
        "addressName_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Address Name *"]/following-sibling::android.widget.EditText)[1]'),
        "city_txt_field": (AppiumBy.XPATH, lambda value: f'(//android.view.View[@content-desc="{value} *"]/following-sibling::android.widget.EditText)[1]'),
        "zipcode_txt_field": (AppiumBy.XPATH, lambda value: f'(//android.view.View[@content-desc="{value} *"]/following-sibling::android.widget.EditText)[1]'),
        "state_drodown": (AppiumBy.ACCESSIBILITY_ID, 'State Select Dropdown'),
        "Streest_Address_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Street Address *"]/following-sibling::android.widget.EditText)[1]'),
        
        # AOL Center (US tenant)
        "aol_center_select_dropdown": (AppiumBy.ACCESSIBILITY_ID, 'AOL Center Select Dropdown'),
        "aol_center_searchBox": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Center"]/following-sibling::android.widget.EditText)[1]'),
        "first_aol_center_option": (AppiumBy.ACCESSIBILITY_ID, 'AOL Center 1'),
        
        # Apex/IC/Contribution (India tenant)
        "apex_select_dropdown": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Apex *"]/following-sibling::android.view.View[@content-desc="Dropdown Input"])[1]'),
        "ic_select_dropdown": (AppiumBy.XPATH, '(//android.view.View[@content-desc="IC *"]/following-sibling::android.view.View[@content-desc="Dropdown Input"])[1]'),
        "contribution_select_dropdown": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Contribution *"]/following-sibling::android.view.View[@content-desc="Dropdown Input"])[1]'),
        
        # Date/Time picker
        "date_pencil": (AppiumBy.ACCESSIBILITY_ID, "Switch to input"),
        "date_enter_field": (AppiumBy.XPATH, '//android.widget.EditText'),
        "option_ok": (AppiumBy.ACCESSIBILITY_ID, 'OK'),
        "time_keyboard": (AppiumBy.ACCESSIBILITY_ID, 'Switch to text input mode'),
        "time_hour": (AppiumBy.XPATH, '(//following-sibling::android.widget.EditText)[1]'),
        "time_min": (AppiumBy.XPATH, '(//following-sibling::android.widget.EditText)[2]'),
        "time_period": (AppiumBy.XPATH, lambda period: f'//android.widget.RadioButton[@content-desc="{period}"]'),
        
        # Create/Save button
        "create_button": (AppiumBy.ACCESSIBILITY_ID, 'Save Button'),
        
        # Dynamic date/time fields
        "date_ith_txt_field": (AppiumBy.ACCESSIBILITY_ID, lambda ith: f"Event Date Field {ith}"),
        "time_ith_txt_field": (AppiumBy.ACCESSIBILITY_ID, lambda ith: f"Event Time Field {ith}"),
        
        # Background/overlay
        "background": (AppiumBy.XPATH, '//android.view.View[@content-desc="Scrim"]'),
        
        # Messages
        "message": (AppiumBy.XPATH, lambda msg: f'//android.view.View[@content-desc="{msg}"]'),
        "msg": (AppiumBy.ACCESSIBILITY_ID, lambda msg: f'{msg}'),
        
        # Search
        "search": (AppiumBy.XPATH, '//android.widget.EditText'),
        "scroll": (AppiumBy.XPATH, "//android.widget.ScrollView"),
        
        # Error messages
        "zipcode_err_msg": (AppiumBy.XPATH, '(//android.widget.EditText[@hint="ZIP Code"]/following-sibling::android.view.View[@content-desc="Please enter a valid input"])[1]'),
        "datetime_err_msg": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Start time must be in the future"])[1]'),
        "address_err_msg": (AppiumBy.XPATH, '(//android.widget.EditText[@hint="Address"]/following-sibling::android.view.View[@content-desc="Please enter a valid input"])[1]'),
        "city_err_msg": (AppiumBy.XPATH, '(//android.widget.EditText[@hint="City"]/following-sibling::android.view.View[@content-desc="Please enter a valid input"])[1]'),
        "teacher_err_msg": (AppiumBy.XPATH, '//android.view.View[@content-desc="Select Teacher..."]/following-sibling::android.view.View[@content-desc = "Select Teacher"]'),
        "max_attendees_err_msg": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Please enter a valid input"])[1]'),
        
        # Calendar
        "calender_year_selector": (AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Select year")]'),
        "year": (AppiumBy.ACCESSIBILITY_ID, lambda year: f'{year}'),
        "calender_date": (AppiumBy.ACCESSIBILITY_ID, lambda date: f'{date}'),
        "month_forward": (AppiumBy.XPATH, "(//android.widget.Button[contains(@content-desc, 'Select year')]/following-sibling::android.view.View[1]//android.widget.Button)[2]"),
        "month_backward": (AppiumBy.XPATH, "(//android.widget.Button[contains(@content-desc, 'Select year')]/following-sibling::android.view.View[1]//android.widget.Button)[1]"),
        
        # Publish/Submit buttons
        "publish_button": (AppiumBy.ACCESSIBILITY_ID, 'Publish Course'),
        "submit_button": (AppiumBy.ACCESSIBILITY_ID, 'Create Now'),
        "start_date_field": (AppiumBy.ACCESSIBILITY_ID, 'Start Date'),
        "start_time_field": (AppiumBy.ACCESSIBILITY_ID, 'Start Time'),
        "end_time_field": (AppiumBy.ACCESSIBILITY_ID, 'End Time'),
    }


    ios = {
        "event_mode": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "course_txt_field": (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@label="Course *"]/following-sibling::XCUIElementTypeStaticText)[1]'),
        "item": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "centerOrState": (AppiumBy.IOS_PREDICATE, lambda val: f'name CONTAINS "{val}"'),
        "is_private": (AppiumBy.ACCESSIBILITY_ID, 'Private Course'),
        "max_attendees_txt_field":(AppiumBy.XPATH, '(//XCUIElementTypeStaticText[contains(@name,"Max Attendees")]/following-sibling::XCUIElementTypeTextField)[1]'),
        "teacher_primary_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Select Teacher(Primary)...'),
        "teacher_additional_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Select Teacher(Additional)...'),
        "add_teacher": (AppiumBy.ACCESSIBILITY_ID, 'Add Teacher'),
        "organizer_txt_field": (AppiumBy.XPATH,'(//XCUIElementTypeStaticText[contains(@name, "Organizer(s)")]/following-sibling::XCUIElementTypeStaticText)[1]'),
        "timezone_txt_field": (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@name="Timezone *"]/following-sibling::XCUIElementTypeStaticText)[1]'),
        "add_date": (AppiumBy.ACCESSIBILITY_ID, 'Add Date'),
        "LocationDropDown": (AppiumBy.ACCESSIBILITY_ID, "Location Select Dropdown"),
        "city": (AppiumBy.ACCESSIBILITY_ID, "City"),
        "state_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'State'),
        "aol_center_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Select Center...'),
        "contact_txt_field": (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[contains(@name, "Contact")]/following-sibling::XCUIElementTypeStaticText)[1]'),
        "date_pencil": (AppiumBy.ACCESSIBILITY_ID, "Switch to input"),
        "date_enter_field": (AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField'),
        "option_ok": (AppiumBy.ACCESSIBILITY_ID, 'OK'),
        "time_keyboard": (AppiumBy.ACCESSIBILITY_ID, 'Switch to text input mode'),
        "time_hour": (AppiumBy.ACCESSIBILITY_ID, 'Hour'),
        "time_min": (AppiumBy.ACCESSIBILITY_ID, 'Minute'),
        "time_period": (AppiumBy.ACCESSIBILITY_ID, lambda period: f'{period}'),
        "create_now": (AppiumBy.ACCESSIBILITY_ID, 'Create Now'),
        "date_ith_txt_field": (AppiumBy.ACCESSIBILITY_ID, lambda i : f"event_date_setter_{i}"),
        "time_ith_txt_field": (AppiumBy.ACCESSIBILITY_ID, lambda i : f"event_time_setter_{i}"),
        "background": (AppiumBy.ACCESSIBILITY_ID, 'Scrim'),
        # "message": (AppiumBy.XPATH, lambda msg: f'//android.view.View[@content-desc="{msg}"]'),
        "search": (AppiumBy.XPATH, '//XCUIElementTypeTextField'),
        "zipcode": (AppiumBy.ACCESSIBILITY_ID, "ZIP Code"),
        "scroll": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeScrollView"),
        "msg": (AppiumBy.ACCESSIBILITY_ID, lambda msg: f'{msg}'),
        "zipcode_err_msg": (AppiumBy.XPATH, '(//XCUIElementTypeTextField[@name="ZIP Code"]/following-sibling::XCUIElementTypeStaticText[@name="Please enter a valid input"])[1]'),
        "calender_year_selector": (AppiumBy.XPATH, '//XCUIElementTypeButton[contains(@name, "Select year")]'),
        "year": (AppiumBy.ACCESSIBILITY_ID, lambda year: f'{year}'),
        "calender_date": (AppiumBy.ACCESSIBILITY_ID, lambda date: f'{date}'),
        "datetime_err_msg": (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@name="Start time must be in the future"])[1]'),
        "month_forward": (AppiumBy.XPATH, "(//XCUIElementTypeButton[contains(@name, 'Select year')]/following-sibling::XCUIElementTypeOther[1]//XCUIElementTypeButton)[2]"),
        "month_backward": (AppiumBy.XPATH, "(//XCUIElementTypeButton[contains(@name, 'Select year')]/following-sibling::XCUIElementTypeOther[1]//XCUIElementTypeButton)[1]"),
        "address_err_msg": (AppiumBy.XPATH, '(//XCUIElementTypeTextField[@name="Address"]/following-sibling::XCUIElementTypeStaticText[@name="Please enter a valid input"])[1]'),
        "city_err_msg": (AppiumBy.XPATH, '(//XCUIElementTypeTextField[@name="City"]/following-sibling::XCUIElementTypeStaticText[@name="Please enter a valid input"])[1]'),
        "teacher_err_msg": (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@name="Select Teacher"])[2]'),
        "max_attendees_err_msg": (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@name="Please enter a valid input"])[1]'),
        "publish_button": (AppiumBy.ACCESSIBILITY_ID, 'Publish Course'),
        "submit_button": (AppiumBy.ACCESSIBILITY_ID, 'Create Now'),
        "start_date_field": (AppiumBy.ACCESSIBILITY_ID, 'Start Date'),
        "start_time_field": (AppiumBy.ACCESSIBILITY_ID, 'Start Time'),
        "end_time_field": (AppiumBy.ACCESSIBILITY_ID, 'End Time'),
    }


    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return CourseCreateLocator.android
        elif platform.lower() == 'ios':
            return CourseCreateLocator.ios
        else:
            raise Exception(f"Invalid platform :: {platform}")