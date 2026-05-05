from appium.webdriver.common.appiumby import AppiumBy


class MeetupCreateLocator:
    android = {
        "event_mode": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "product_dropdown": (AppiumBy.ACCESSIBILITY_ID, 'Program Select Dropdown'),
        "is_private": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),

        # Product/Program selection - uses tenant-specific label
        "product_txt_field": (AppiumBy.XPATH, lambda value: f'//android.view.View[@content-desc="{value}"]/following-sibling::android.widget.EditText[1]'),
        "first_product_name": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "no_result_msg": (AppiumBy.ACCESSIBILITY_ID, 'No results found'),

        "search_result": (AppiumBy.ACCESSIBILITY_ID, lambda name: f'{name}'),

        # Max attendees - uses tenant-specific label
        "max_attendees_txt_field": (AppiumBy.XPATH, lambda value: f'//android.view.View[@content-desc="{value} *"]/following-sibling::android.widget.EditText[1]'),
        
        # Team member buttons
        "add_teacher": (AppiumBy.ACCESSIBILITY_ID, 'Add Teacher Button'),
        "add_organizer": (AppiumBy.ACCESSIBILITY_ID, 'Add Organizer Button'),

        "first_teacher_name": (AppiumBy.ACCESSIBILITY_ID, 'teacher 1'),
        "first_organizer_name": (AppiumBy.ACCESSIBILITY_ID, 'teacher 1'),

               # Done and navigation buttons
        "done_button": (AppiumBy.ACCESSIBILITY_ID, 'Done Button'),
        "back_button": (AppiumBy.ACCESSIBILITY_ID, 'Back Button'),

         # Notifications
        "add_notifications_button": (AppiumBy.ACCESSIBILITY_ID, 'Add Notifications Button'),
        "notification_person": (AppiumBy.XPATH, lambda name: f'//android.view.View[contains(@content-desc,"{name}")]'),
        "enable_notification_button": (AppiumBy.XPATH, lambda name: f'//android.view.View[contains(@content-desc,"{name}")]'),
        # "enable_notification_button": (AppiumBy.XPATH, lambda name: f'//android.widget.CheckBox[contains(@content-desc,"{name}")]'),

        # Organizer
        "organizer_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Organizer(s) *"]/following-sibling::android.view.View)[1]'),
        
          # Contact person
        "add_point_of_contact_button": (AppiumBy.ACCESSIBILITY_ID, 'Add Point of contact Button'),
        "add_new_contact_button": (AppiumBy.ACCESSIBILITY_ID, 'Add Contact Button'),
        "contact_name_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Name *"]/following-sibling::android.widget.EditText)[1]'),
        "contact_email_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Mail Id *"]/following-sibling::android.widget.EditText)[1]'),
        "contact_phone_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Mobile Number *"]/following-sibling::android.widget.EditText)[1]'),
        "create_contact_button": (AppiumBy.ACCESSIBILITY_ID, 'Create Contact Button'),
        "contact_searchBox": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Point of contact"]/following-sibling::android.widget.EditText)[1]'),
        # "first_contact_option": (AppiumBy.ACCESSIBILITY_ID, 'member 1'),
        "first_contact_option": (AppiumBy.ACCESSIBILITY_ID, 'teacher 1'),


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
        "meeting_link_txt_field": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Meeting URL"]/following-sibling::android.widget.EditText)[1]'),
        # AOL Center (US tenant)
        "aol_center_select_dropdown": (AppiumBy.ACCESSIBILITY_ID, 'AOL Center Select Dropdown'),
        "aol_center_searchBox": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Center"]/following-sibling::android.widget.EditText)[1]'),
        "first_aol_center_option": (AppiumBy.ACCESSIBILITY_ID, 'AOL Center 1'),
        
    
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

        # recurring meetup
        "recurring_meetup_button": (AppiumBy.ACCESSIBILITY_ID, 'Enable/Disable Recurring Event Button'),
        "recurring_count_txt_field": (AppiumBy.XPATH, '//android.view.View[@content-desc="Every *"]/following-sibling::android.widget.EditText[1]'),
        "frequency_dropdown": (AppiumBy.ACCESSIBILITY_ID, 'Frequency Expandable Dropdown'),
        "monthly_dropdown": (AppiumBy.ACCESSIBILITY_ID, 'Monthly Expandable Dropdown'),
        "Ends_ON_radioButton" : (AppiumBy.ACCESSIBILITY_ID, 'Ends On Radio Button'),
        "Ends_After_radioButton" : (AppiumBy.ACCESSIBILITY_ID, 'Ends After Radio Button'),
        "Ends_On_Date_txt_field" : (AppiumBy.ACCESSIBILITY_ID, 'Ends On Date Field'),
        "Occurence_count_txt_field": (AppiumBy.XPATH, '//android.view.View[@content-desc="After"]/following-sibling::android.widget.EditText[1]'),
        "Frequency_dropdown_Daily": (AppiumBy.ACCESSIBILITY_ID, 'Daily'),
        "Frequency_dropdown_Weekly": (AppiumBy.ACCESSIBILITY_ID, 'Weekly'),
        "Frequency_dropdown_Monthly": (AppiumBy.ACCESSIBILITY_ID, 'Monthly'),
        "Monthly_dropdown_value": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "Weekly_select_value" : (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
  
        "item": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "new_meetup_header": (AppiumBy.ACCESSIBILITY_ID, 'New Meetup'),
        "meetup_info_header": (AppiumBy.ACCESSIBILITY_ID, 'Meetup Information'),
        "select_teacher_header": (AppiumBy.ACCESSIBILITY_ID, 'Select Teacher'),
        "select_org_header": (AppiumBy.ACCESSIBILITY_ID, 'Select Organizer'),
        "select_date_header": (AppiumBy.ACCESSIBILITY_ID, 'Event Dates'),
        "select_date_header": (AppiumBy.ACCESSIBILITY_ID, 'Event Dates'),
        "location_header": (AppiumBy.ACCESSIBILITY_ID, 'Location'),
        "meeting_url_header": (AppiumBy.ACCESSIBILITY_ID, 'Meeting URL'),
        "revenue_header": (AppiumBy.ACCESSIBILITY_ID, 'Revenue & Expense Details'),
        "max_attendees_err_msg": (AppiumBy.XPATH, '(//android.view.View[@content-desc="Please enter a valid input"])[1]'),
        "teacher_err_msg": (AppiumBy.ACCESSIBILITY_ID , "Select Teacher"), 
        "address_err_field": (AppiumBy.XPATH, lambda msg: f'(//android.widget.EditText[@hint="Address"]/following-sibling::android.view.View[@content-desc="{msg}"])[1]'),
        "city_err_filed": (AppiumBy.XPATH, lambda msg: f'(//android.widget.EditText[@hint="City"]/following-sibling::android.view.View[@content-desc="{msg}"])[1]'),
        "out_of_range_err": (AppiumBy.ACCESSIBILITY_ID , 'Out of range.'),
        "final_msg": (AppiumBy.XPATH, '//android.widget.ImageView/following-sibling::android.view.View[1]')
    }


    ios = {
        "meetup_type": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "select_meetup_txt_box": (AppiumBy.ACCESSIBILITY_ID, 'Select meetup...'),
        "is_private": (AppiumBy.ACCESSIBILITY_ID, 'Private Meetup'),
        "max_attendees_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Max Attendees'),
        "teacher_ith_txt_field": (AppiumBy.ACCESSIBILITY_ID, lambda ith: 'Select Teacher(Primary)...' if str(ith) == '1' else 'Select Teacher(Additional)...'),
        "add_teacher": (AppiumBy.ACCESSIBILITY_ID, 'Add Teacher'),
        "organizer_txt_field": (AppiumBy.XPATH,'(//XCUIElementTypeStaticText[contains(@name, "Organizer(s)")]/following-sibling::XCUIElementTypeStaticText)[1]'),
        "timezone_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Select Timezone...'),
        # "date_ith_txt_field": (AppiumBy.XPATH, lambda ith: f"(//XCUIElementTypeStaticText[contains(@label, 'Date & Time *')]/following-sibling::XCUIElementTypeOther)[{ith}]"),
        "date_ith_txt_field": (AppiumBy.XPATH, lambda date : f"//XCUIElementTypeStaticText[@name='{date}']"),       
        # "time_ith_txt_field": (AppiumBy.XPATH, lambda time : f"//XCUIElementTypeStaticText[@name='{time}']"),   
        "time_ith_txt_field": (AppiumBy.XPATH, "(//XCUIElementTypeStaticText[@name='Date & Time *']/following-sibling::* )[2]"),
        "msg": (AppiumBy.ACCESSIBILITY_ID,lambda msg: f'{msg}'),
        "search": (AppiumBy.XPATH, '//XCUIElementTypeTextField'),
        "search_alt": (AppiumBy.XPATH, '//XCUIElementTypeSearchField'),
        "item": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'{value}'),
        "out_of_range_err": (AppiumBy.ACCESSIBILITY_ID, "Invalid maximum attendees"),
        # "time_dropdown": (AppiumBy.XPATH, lambda dropdown: f"//XCUIElementTypeOther[@name='{dropdown}']"),
        # "start_time_txt_field": (AppiumBy.XPATH, lambda timeFormat: f'(//XCUIElementTypeOther[@name="Start Time *"]/following-sibling::XCUIElementTypeOther)[1]'),
        # "date_dropdown": (AppiumBy.XPATH, lambda value: f"//XCUIElementTypeOther[@name='{value}']"),
        # "start_date_txt_field": (AppiumBy.XPATH, lambda dateFormat: f'(//XCUIElementTypeOther[@name="Start Date *"]/following-sibling::XCUIElementTypeOther)[1]'),
        # Course-like iOS date/time fields
        "start_date_field": (AppiumBy.ACCESSIBILITY_ID, 'Start Date'),
        "start_time_field": (AppiumBy.ACCESSIBILITY_ID, 'Start Time'),
        "meeting_link_txt_field": (AppiumBy.XPATH, '(//XCUIElementTypeOther[@name="Meeting URL *"]/following-sibling::XCUIElementTypeTextField)[1]'),
        "address": (AppiumBy.ACCESSIBILITY_ID, "Address"),
        "city": (AppiumBy.ACCESSIBILITY_ID, "City"),
        "zipcode": (AppiumBy.ACCESSIBILITY_ID, "ZIP Code"),
        "centerOrState": (AppiumBy.IOS_PREDICATE, lambda val: f'name CONTAINS "{val}"'),
        "aol_center_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Select Center...'),
        "location": (AppiumBy.XPATH, lambda loc: f"//XCUIElementTypeTextField[@value='{loc}']"),
        "add_contact": (AppiumBy.ACCESSIBILITY_ID, 'Add Contact'),
        "contact_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'Select Contact...'),
        "create_now": (AppiumBy.ACCESSIBILITY_ID, 'Create Now'),
        "new_meetup_header": (AppiumBy.ACCESSIBILITY_ID, 'New Meetup'),
        "meetup_info_header": (AppiumBy.ACCESSIBILITY_ID, 'Meetup Information'),
        "select_teacher_header": (AppiumBy.ACCESSIBILITY_ID, 'Select Teacher'),
        "select_org_header": (AppiumBy.ACCESSIBILITY_ID, 'Select Organizer'),
        "select_date_header": (AppiumBy.ACCESSIBILITY_ID, 'Event Dates'),
        "location_header": (AppiumBy.ACCESSIBILITY_ID, 'Location'),
        "meeting_url_header": (AppiumBy.ACCESSIBILITY_ID, 'Meeting URL'),
        "revenue_header": (AppiumBy.ACCESSIBILITY_ID, 'Revenue & Expense Details'),
        "state_txt_field": (AppiumBy.ACCESSIBILITY_ID, 'State'),
        "scroll": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeScrollView"),
        "date_pencil": (AppiumBy.ACCESSIBILITY_ID, "Switch to input"),
        "time_keyboard": (AppiumBy.ACCESSIBILITY_ID, 'Switch to text input mode'),
        "time_hour": (AppiumBy.ACCESSIBILITY_ID, 'Hour'),
        "time_min": (AppiumBy.ACCESSIBILITY_ID, 'Minute'),
        "time_period": (AppiumBy.ACCESSIBILITY_ID, lambda period: f'{period}'),
        "date_enter_field": (AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField'),
        "option_ok": (AppiumBy.ACCESSIBILITY_ID, "OK"),
    }


    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return MeetupCreateLocator.android
        elif platform.lower() == 'ios':
            return MeetupCreateLocator.ios
        else:
            raise Exception(f"Invalid platform :: {platform}")