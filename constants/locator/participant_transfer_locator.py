from appium.webdriver.common.appiumby import AppiumBy


class ParticipantTransferLocator:
    android = {
        "events_search_field": (AppiumBy.XPATH, "//android.widget.EditText",),
        "event_row_contains": (
            AppiumBy.XPATH,
            lambda code: (
                f'//android.view.View[contains(@content-desc,"{code}")] | '
                f'//android.widget.Button[contains(@content-desc,"{code}")]'
            ),
        ),
        "course_detail_scroll": (AppiumBy.XPATH, "//android.widget.ScrollView"),
        "participants_section": (
            AppiumBy.ACCESSIBILITY_ID,
            'Mark/UnMark Attendance Button',
        ),
        "participant_by_name": (AppiumBy.XPATH, lambda val: f'//android.view.View[contains(@content-desc, "{val}")]'),
       "transfer_button": (AppiumBy.ACCESSIBILITY_ID, "Transfer Button\nTransfer"),
        "notes_button": (AppiumBy.ACCESSIBILITY_ID, "Notes Button\nNotes"),
        "confirm_button": (AppiumBy.ACCESSIBILITY_ID, "Confirm Dialog Button"),
        "transfer_reason_field": (
            AppiumBy.XPATH,
            "//android.widget.EditText",
        ),
        "transfer_top_right": (
            AppiumBy.ACCESSIBILITY_ID,
            'Transfer',
        ),

        "filter_teachers_option": (AppiumBy.ACCESSIBILITY_ID,"teacher Filter Button",),
        "teacher_filter_any_one_event": (AppiumBy.ACCESSIBILITY_ID,"Any One Event Teacher Checkbox",),
        "show_results_bottom": (AppiumBy.ACCESSIBILITY_ID, "Show Filter Results",),
        "transfer_top_right_2": (AppiumBy.ACCESSIBILITY_ID, "Transfer Button"),
        "transfer_top_right_2": (
            AppiumBy.XPATH,
            '//android.widget.Button[contains(@content-desc,"Transfer Button")]',
        ),
        "eligible_programs_filter": (AppiumBy.ACCESSIBILITY_ID, "Events Filter Button",),
        "eligible_event_row": (
            AppiumBy.XPATH,
            '//android.view.View[contains(@content-desc,"E-")]',
        ),
        "transfer_initiated_message": (
            AppiumBy.XPATH,
            '//*[contains(@content-desc,"Transfer Initiated")]',
        ),
        "dialog_ok_button": (AppiumBy.ACCESSIBILITY_ID, "OK"),
        "nav_back": (
            AppiumBy.XPATH,
            '//android.widget.ImageButton[@content-desc="Back"]',
        ),
    }

    ios = {
        "search_button": (AppiumBy.ACCESSIBILITY_ID, "Events Search Button",),
        "events_search_field": (
            AppiumBy.XPATH,
            "(//XCUIElementTypeSearchField | //XCUIElementTypeTextField)[1]",
        ),
        "event_row_contains": (
            AppiumBy.IOS_PREDICATE,
            lambda code: (
                f'label CONTAINS[c] "{code}" OR name CONTAINS[c] "{code}" OR '
                f'value CONTAINS[c] "{code}"'
            ),
        ),
        "course_detail_scroll": (
            AppiumBy.IOS_CLASS_CHAIN,
            "**/XCUIElementTypeScrollView",
        ),
        "participants_section": (
            AppiumBy.ACCESSIBILITY_ID,
            "Mark/UnMark Attendance Button",
        ),
        "participant_by_name": (
            AppiumBy.IOS_PREDICATE,
            lambda name: (
                f'label CONTAINS[c] "{name}" OR name CONTAINS[c] "{name}"'
            ),
        ),
        "transfer_button": (AppiumBy.ACCESSIBILITY_ID, "Transfer Button\nTransfer"),
        "notes_button": (AppiumBy.ACCESSIBILITY_ID, "Notes Button\nNotes"),
        "confirm_button": (AppiumBy.ACCESSIBILITY_ID, "Confirm Dialog Button"),
        "transfer_reason_field": (
            AppiumBy.XPATH,
            '//XCUIElementTypeTextField[@name="Mention the reason for the transfer"]',
        ),
        "transfer_top_right": (AppiumBy.ACCESSIBILITY_ID, "Transfer"),
        "eligible_programs_filter": (AppiumBy.ACCESSIBILITY_ID, "Events Filter Button",),
        "filter_teachers_option": (AppiumBy.ACCESSIBILITY_ID,"teacher Filter Button",),
        "teacher_filter_any_one_event": (AppiumBy.ACCESSIBILITY_ID,"Any One Event Teacher Checkbox",),
        "show_results_bottom": (AppiumBy.ACCESSIBILITY_ID, "Show Filter Results",),
        "transfer_top_right_2": (AppiumBy.ACCESSIBILITY_ID, "Transfer Button"),
        "eligible_event_row": (
            AppiumBy.IOS_PREDICATE,
            'label CONTAINS "E-" OR name CONTAINS "E-"',
        ),
        "transfer_initiated_message": (
            AppiumBy.IOS_PREDICATE,
            'label CONTAINS[c] "Transfer Initiated" OR name CONTAINS[c] "Transfer Initiated"',
        ),
        "dialog_ok_button": (AppiumBy.ACCESSIBILITY_ID, "OK"),
        # First toolbar back
        "nav_back_first_click": (
            AppiumBy.IOS_CLASS_CHAIN,
            "**/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/"
            "XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[2]/"
            "XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/"
            "XCUIElementTypeOther[2]/XCUIElementTypeButton",
        ),
        "nav_back_first_click_xpath": (
            AppiumBy.XPATH,
            '//XCUIElementTypeApplication[@name="QA - AOL Teacher App"]/'
            "XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/"
            "XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[2]/"
            "XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/"
            "XCUIElementTypeOther[2]/XCUIElementTypeButton",
        ),
        # Second toolbar back
        "nav_back": (AppiumBy.ACCESSIBILITY_ID, "Back Button"),
        "nav_back_second_click_xpath": (
            AppiumBy.XPATH,
            '//XCUIElementTypeButton[@name="Back Button"]',
        ),
    }

    @staticmethod
    def teacher_filter_row_labels(platform: str) -> list[str]:
        """Fallback strings if filter_teachers_option locator does not match the build."""
        p = platform.lower()
        if p == "ios":
            return [
                "Teachers Filter Button",
                "Teacher Filter Button",
                "Teachers",
                "Teacher",
            ]
        return ["Teachers", "Teacher", "Teachers Filter Button"]

    @classmethod
    def get_locators(cls, platform: str):
        p = platform.lower()
        if p == "android":
            return cls.android
        if p == "ios":
            return cls.ios
        raise Exception(f"Invalid platform :: {platform}")
