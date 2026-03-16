from appium.webdriver.common.appiumby import AppiumBy


class AttendanceLocator:
    android = {
        "attendance_screen": (AppiumBy.ID, "attendance_screen"),
        "event_card": (AppiumBy.ID, "event_card"),
        "mark_attendance_button": (AppiumBy.ID, "mark_attendance_btn"),
        "qr_scanner_button": (AppiumBy.ID, "qr_scanner_btn"),
        "manual_attendance_button": (AppiumBy.ID, "manual_attendance_btn"),
        "participant_list": (AppiumBy.ID, "participant_list"),
        "participant_item": (AppiumBy.XPATH, "//android.widget.RecyclerView//android.widget.LinearLayout"),
        "participant_name": (AppiumBy.ID, "participant_name"),
        "attendance_toggle": (AppiumBy.ID, "attendance_toggle"),
        "notes_field": (AppiumBy.ID, "notes_field"),
        "save_attendance_button": (AppiumBy.ID, "save_attendance_btn"),
        "qr_camera_view": (AppiumBy.ID, "qr_camera"),
        "qr_scan_result": (AppiumBy.ID, "qr_result"),
        "attendance_success_message": (AppiumBy.ID, "success_msg"),
        "attendance_error_message": (AppiumBy.ID, "error_msg"),
        "search_participant": (AppiumBy.ID, "search_participant"),
        "filter_button": (AppiumBy.ID, "filter_btn"),
        "present_count": (AppiumBy.ID, "present_count"),
        "absent_count": (AppiumBy.ID, "absent_count"),
        "total_count": (AppiumBy.ID, "total_count"),
    }

    ios = {
        "attendance_screen": (AppiumBy.ACCESSIBILITY_ID, "Attendance"),
        "event_card": (AppiumBy.ACCESSIBILITY_ID, "Event Card"),
        "mark_attendance_button": (AppiumBy.ACCESSIBILITY_ID, "Mark Attendance"),
        "qr_scanner_button": (AppiumBy.ACCESSIBILITY_ID, "QR Scanner"),
        "manual_attendance_button": (AppiumBy.ACCESSIBILITY_ID, "Manual Attendance"),
        "participant_list": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeTable"),
        "participant_item": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeCell"),
        "participant_name": (AppiumBy.XPATH, "//XCUIElementTypeStaticText[contains(@label, 'participant')]"),
        "attendance_toggle": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeSwitch"),
        "notes_field": (AppiumBy.ACCESSIBILITY_ID, "Notes"),
        "save_attendance_button": (AppiumBy.ACCESSIBILITY_ID, "Save Attendance"),
        "qr_camera_view": (AppiumBy.XPATH, "//XCUIElementTypeCamera"),
        "qr_scan_result": (AppiumBy.ACCESSIBILITY_ID, "QR Scan Result"),
        "attendance_success_message": (AppiumBy.XPATH, "//*[contains(@label, 'Attendance saved successfully')]"),
        "attendance_error_message": (AppiumBy.XPATH, "//*[contains(@label, 'Error')]"),
        "search_participant": (AppiumBy.ACCESSIBILITY_ID, "Search Participant"),
        "filter_button": (AppiumBy.ACCESSIBILITY_ID, "Filter"),
        "present_count": (AppiumBy.ACCESSIBILITY_ID, "Present Count"),
        "absent_count": (AppiumBy.ACCESSIBILITY_ID, "Absent Count"),
        "total_count": (AppiumBy.ACCESSIBILITY_ID, "Total Count"),
        "scroll": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeScrollView"),
    }

    @classmethod
    def get_locators(cls, platform):
        return cls.ios if platform.lower() == "ios" else cls.android
