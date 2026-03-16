from appium.webdriver.common.appiumby import AppiumBy


class EventEditLocator:
    android = {
        "edit_button": (AppiumBy.ID, "edit_btn"),
        "edit_screen": (AppiumBy.ID, "edit_screen"),
        "event_name_field": (AppiumBy.ID, "event_name"),
        "description_field": (AppiumBy.ID, "description"),
        "max_attendees_field": (AppiumBy.ID, "max_attendees"),
        "visibility_toggle": (AppiumBy.ID, "visibility_toggle"),
        "start_date_field": (AppiumBy.ID, "start_date"),
        "start_time_field": (AppiumBy.ID, "start_time"),
        "end_time_field": (AppiumBy.ID, "end_time"),
        "timezone_dropdown": (AppiumBy.ID, "timezone"),
        "organizer_field": (AppiumBy.ID, "organizer"),
        "contact_person_field": (AppiumBy.ID, "contact_person"),
        "teacher_dropdown": (AppiumBy.ID, "teacher_dropdown"),
        "add_teacher_button": (AppiumBy.ID, "add_teacher"),
        "remove_teacher_button": (AppiumBy.ID, "remove_teacher"),
        "location_field": (AppiumBy.ID, "location"),
        "address_field": (AppiumBy.ID, "address"),
        "city_field": (AppiumBy.ID, "city"),
        "state_field": (AppiumBy.ID, "state"),
        "zipcode_field": (AppiumBy.ID, "zipcode"),
        "meeting_url_field": (AppiumBy.ID, "meeting_url"),
        "aol_center_dropdown": (AppiumBy.ID, "aol_center"),
        "save_changes_button": (AppiumBy.ID, "save_changes"),
        "cancel_button": (AppiumBy.ID, "cancel"),
        "success_message": (AppiumBy.ID, "success_msg"),
        "error_message": (AppiumBy.ID, "error_msg"),
        "validation_error": (AppiumBy.XPATH, "//*[contains(@text, 'Required field')]"),
        "mode_not_editable": (AppiumBy.XPATH, "//*[contains(@text, 'Mode cannot be changed')]"),
        "product_not_editable": (AppiumBy.XPATH, "//*[contains(@text, 'Product cannot be changed')]"),
    }

    ios = {
        "edit_button": (AppiumBy.ACCESSIBILITY_ID, "Edit"),
        "edit_screen": (AppiumBy.ACCESSIBILITY_ID, "Edit Event"),
        "event_name_field": (AppiumBy.ACCESSIBILITY_ID, "Event Name"),
        "description_field": (AppiumBy.ACCESSIBILITY_ID, "Description"),
        "max_attendees_field": (AppiumBy.ACCESSIBILITY_ID, "Max Attendees"),
        "visibility_toggle": (AppiumBy.ACCESSIBILITY_ID, "Visibility"),
        "start_date_field": (AppiumBy.ACCESSIBILITY_ID, "Start Date"),
        "start_time_field": (AppiumBy.ACCESSIBILITY_ID, "Start Time"),
        "end_time_field": (AppiumBy.ACCESSIBILITY_ID, "End Time"),
        "timezone_dropdown": (AppiumBy.ACCESSIBILITY_ID, "Timezone"),
        "organizer_field": (AppiumBy.ACCESSIBILITY_ID, "Organizer"),
        "contact_person_field": (AppiumBy.ACCESSIBILITY_ID, "Contact Person"),
        "teacher_dropdown": (AppiumBy.ACCESSIBILITY_ID, "Select Teacher"),
        "add_teacher_button": (AppiumBy.ACCESSIBILITY_ID, "Add Teacher"),
        "remove_teacher_button": (AppiumBy.ACCESSIBILITY_ID, "Remove Teacher"),
        "location_field": (AppiumBy.ACCESSIBILITY_ID, "Location"),
        "address_field": (AppiumBy.ACCESSIBILITY_ID, "Address"),
        "city_field": (AppiumBy.ACCESSIBILITY_ID, "City"),
        "state_field": (AppiumBy.ACCESSIBILITY_ID, "State"),
        "zipcode_field": (AppiumBy.ACCESSIBILITY_ID, "Zip Code"),
        "meeting_url_field": (AppiumBy.ACCESSIBILITY_ID, "Meeting URL"),
        "aol_center_dropdown": (AppiumBy.ACCESSIBILITY_ID, "AOL Center"),
        "save_changes_button": (AppiumBy.ACCESSIBILITY_ID, "Save Changes"),
        "cancel_button": (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
        "success_message": (AppiumBy.XPATH, "//*[contains(@label, 'Changes saved successfully')]"),
        "error_message": (AppiumBy.XPATH, "//*[contains(@label, 'Error')]"),
        "validation_error": (AppiumBy.XPATH, "//*[contains(@label, 'Required field')]"),
        "mode_not_editable": (AppiumBy.XPATH, "//*[contains(@label, 'Mode cannot be changed')]"),
        "product_not_editable": (AppiumBy.XPATH, "//*[contains(@label, 'Product cannot be changed')]"),
        "scroll": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeScrollView"),
    }

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return EventEditLocator.android
        elif platform.lower() == 'ios':
            return EventEditLocator.ios
        else:
            raise Exception(f"Invalid platform :: {platform}")