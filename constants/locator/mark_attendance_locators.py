from appium.webdriver.common.appiumby import AppiumBy


class MarkAttendanceLocator:

    android = {
        "mark_attendance_search_icon": (AppiumBy.ACCESSIBILITY_ID,'Search Participants Button',),
        "participants_search_field": (AppiumBy.XPATH,"//android.widget.EditText",),
        "participant_filter": (AppiumBy.ACCESSIBILITY_ID,'Participants Filter Button',),
        "participant_list_scroll": (AppiumBy.XPATH,"(//XCUIElementTypeScrollView)[1]",),
        "participant_name_header": (AppiumBy.ACCESSIBILITY_ID,'Participant name',),
        "attendance_column_header": (AppiumBy.ACCESSIBILITY_ID, "Attendance status"),
        "attendance_status_dropdown": (AppiumBy.XPATH,'(//android.widget.Button[@content-desc="Attendance Status Dropdown Expandable Dropdown"])[1]',
        ),
       "attendance_dropdown_in_participant_row": (
            AppiumBy.XPATH,
            lambda name: (
                f'//android.view.View[contains(@content-desc,"{name}")]'
                f'//android.widget.Button[contains(@content-desc,"Attendance Status")]'
            ),
        ),
        "back_button" : (AppiumBy.ACCESSIBILITY_ID,"Back Button"),
        "dropdown_attended": (AppiumBy.ACCESSIBILITY_ID, "Attended"),
        "dropdown_dropout": (AppiumBy.ACCESSIBILITY_ID,"Drop-out"),
        "dropdown_no_show": (AppiumBy.ACCESSIBILITY_ID,"No-Show"),
        "select_all_checkbox": (AppiumBy.ACCESSIBILITY_ID, "Select all"),
        "bottom_send_email": (AppiumBy.ACCESSIBILITY_ID, "Send Email to Participants Button\nSend email"),
        "bottom_mark_attended": (AppiumBy.ACCESSIBILITY_ID, "Mark/UnMark Attendance Button\nMark Attended"),
        "bottom_more_button": (AppiumBy.ACCESSIBILITY_ID,"More Options Button\nMore"),
        "bulk_sheet_cancel_after_mark_attended": (
            AppiumBy.XPATH,
            '//XCUIElementTypeButton[@name="Cancel"]',
        ),

        "pa_filter_sheet_title_filters": (AppiumBy.ACCESSIBILITY_ID,'Filters',),
        "pa_filter_sheet_reset": (AppiumBy.ACCESSIBILITY_ID,'Reset filters',),
        "pa_filter_section_attendance_status": (AppiumBy.ACCESSIBILITY_ID,'attendanceStatus Filter Button',),
        "pa_filter_radio_all": (AppiumBy.ACCESSIBILITY_ID,'All Checkbox',),
        "pa_filter_radio_attended": (AppiumBy.ACCESSIBILITY_ID,"Attended Checkbox",),
        "pa_filter_radio_no_show": (AppiumBy.ACCESSIBILITY_ID,"No-Show Checkbox",),
        "pa_filter_radio_dropout": (AppiumBy.ACCESSIBILITY_ID,"Drop-out Checkbox",),
        "pa_filter_radio_not_set": (AppiumBy.ACCESSIBILITY_ID,'Not set Checkbox',),
        "pa_filter_show_results": (AppiumBy.ACCESSIBILITY_ID,'Show Filter Results',),
        "qr_scan_button": (AppiumBy.ACCESSIBILITY_ID, "QR Scan Button"),
        "participants_more_options_button": (
            AppiumBy.ACCESSIBILITY_ID,
            "Participants More Options Button",
        ),
        "more_options_menu_select": (AppiumBy.ACCESSIBILITY_ID, "Select"),
        "more_options_menu_scan_qr": (AppiumBy.ACCESSIBILITY_ID, "Scan QR"),
        "more_options_menu_cancel": (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
        #"more_options_menu_search": (AppiumBy.ACCESSIBILITY_ID, "Search"),
        "more_options_mark_all_attended": (
            AppiumBy.ACCESSIBILITY_ID,
            "Mark all attended",
        ),
        "more_options_mark_all_no_show": (
            AppiumBy.ACCESSIBILITY_ID,
            "Mark all no-show",
        ),
        "more_options_mark_all_dropout": (
            AppiumBy.ACCESSIBILITY_ID,
            "Mark all drop-out",
        ),
        "see_past_participants_button": (
            AppiumBy.ACCESSIBILITY_ID,
            "See Past Participants Button",
        ),
    }
    ios = {
        "mark_attendance_search_icon": (AppiumBy.ACCESSIBILITY_ID,'Search Participants Button',),
        "participants_search_field": (AppiumBy.ACCESSIBILITY_ID,"Search Participants Button",),
        "participant_filter": (AppiumBy.ACCESSIBILITY_ID,'Participants Filter Button',),
        "participant_list_scroll": (AppiumBy.XPATH,"(//XCUIElementTypeScrollView)[1]",),
        "participant_name_header": (AppiumBy.ACCESSIBILITY_ID,'Participant name',),
        "attendance_column_header": (AppiumBy.ACCESSIBILITY_ID, "Attendance status"),
        "attendance_status_dropdown": (AppiumBy.ACCESSIBILITY_ID,"Attendance Status Dropdown Expandable Dropdown",),
        "attendance_dropdown_in_participant_row": (
            AppiumBy.XPATH,
            lambda name: (
                "(//XCUIElementTypeButton["
                '(contains(@name,"Attendance Status Dropdown Expandable Dropdown") or '
                'contains(@name,"Attendance Status Dropdown")) and '
                f'ancestor::*[.//*[contains(translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                f'"abcdefghijklmnopqrstuvwxyz"),"{name.lower()}")]]])[1]'
            ),
        ),
        "dropdown_attended": (AppiumBy.ACCESSIBILITY_ID, "Attended"),
        "dropdown_dropout": (AppiumBy.ACCESSIBILITY_ID,"Drop-out"),
        "dropdown_no_show": (AppiumBy.ACCESSIBILITY_ID,"No-Show"),
        "select_all_checkbox": (AppiumBy.ACCESSIBILITY_ID, "Select all"),
        "bottom_send_email": (AppiumBy.ACCESSIBILITY_ID, "Send Email to Participants Button\nSend email"),
        "bottom_mark_attended": (AppiumBy.ACCESSIBILITY_ID, "Mark/UnMark Attendance Button\nMark Attended"),
        "bottom_more_button": (AppiumBy.ACCESSIBILITY_ID,"More Options Button\nMore"),
        "bulk_sheet_cancel_after_mark_attended": (
            AppiumBy.XPATH,
            '//XCUIElementTypeButton[@name="Cancel"]',
        ),

        "pa_filter_sheet_title_filters": (AppiumBy.ACCESSIBILITY_ID,'Filters',),
        "pa_filter_sheet_reset": (AppiumBy.ACCESSIBILITY_ID,'Reset filters',),
        "pa_filter_section_attendance_status": (AppiumBy.ACCESSIBILITY_ID,'attendanceStatus Filter Button',),
        "pa_filter_radio_all": (AppiumBy.ACCESSIBILITY_ID,'All Checkbox',),
        "pa_filter_radio_attended": (AppiumBy.ACCESSIBILITY_ID,"Attended Checkbox",),
        "pa_filter_radio_no_show": (AppiumBy.ACCESSIBILITY_ID,"No-Show Checkbox",),
        "pa_filter_radio_dropout": (AppiumBy.ACCESSIBILITY_ID,"Drop-out Checkbox",),
        "pa_filter_radio_not_set": (AppiumBy.ACCESSIBILITY_ID,'Not set Checkbox',),
        "pa_filter_show_results": (AppiumBy.ACCESSIBILITY_ID,'Show Filter Results',),
        "qr_scan_button": (AppiumBy.ACCESSIBILITY_ID, "QR Scan Button"),
        "participants_more_options_button": (
            AppiumBy.ACCESSIBILITY_ID,
            "Participants More Options Button",
        ),
        "more_options_menu_select": (AppiumBy.ACCESSIBILITY_ID, "Select"),
        "more_options_menu_scan_qr": (AppiumBy.ACCESSIBILITY_ID, "Scan QR"),
        "more_options_menu_cancel": (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
        #"more_options_menu_search": (AppiumBy.ACCESSIBILITY_ID, "Search"),
        "more_options_mark_all_attended": (
            AppiumBy.ACCESSIBILITY_ID,
            "Mark all attended",
        ),
        "more_options_mark_all_no_show": (
            AppiumBy.ACCESSIBILITY_ID,
            "Mark all no-show",
        ),
        "more_options_mark_all_dropout": (
            AppiumBy.ACCESSIBILITY_ID,
            "Mark all drop-out",
        ),
        "see_past_participants_button": (
            AppiumBy.ACCESSIBILITY_ID,
            "See Past Participants Button",
        ),
    }

    @classmethod
    def get_locators(cls, platform: str):
        p = platform.lower()
        if p == "android":
            return cls.android
        if p == "ios":
            return cls.ios
        raise ValueError(f"Invalid platform: {platform}")
