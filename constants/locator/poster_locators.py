from appium.webdriver.common.appiumby import AppiumBy


class PosterLocators:
    android = {
        "edit_event_button": (AppiumBy.ACCESSIBILITY_ID, "Edit Event Button"),
        "date_time_section_label": (AppiumBy.ACCESSIBILITY_ID, "Date & Time *"),
        "event_date_field_1": (AppiumBy.ACCESSIBILITY_ID, "Event Date Field 1"),
        "event_time_field_1": (AppiumBy.ACCESSIBILITY_ID, "Event Time Field 1"),
        # Optional; when empty, PosterCreationPage uses course_detail_scroll for edit form
        "event_edit_scroll": (AppiumBy.ACCESSIBILITY_ID, ""),
        "course_posters_entry": (AppiumBy.ACCESSIBILITY_ID, "Create Poster Button"),
        "poster_fab_plus": (AppiumBy.XPATH, '//android.view.View[@content-desc="Register here: "]/following-sibling::android.widget.Button'),
        "template_39": (AppiumBy.ACCESSIBILITY_ID, "Template 39"),
        "poster_preview_date": (AppiumBy.ACCESSIBILITY_ID, ""),
        "poster_preview_time": (AppiumBy.ACCESSIBILITY_ID, ""),
        "poster_qr_code": (AppiumBy.ACCESSIBILITY_ID, ""),
        "poster_url_text": (
            AppiumBy.XPATH,
            "//*[contains(@content-desc,'https') or contains(@text,'https')]",
        ),
        "register_here_text": (AppiumBy.ACCESSIBILITY_ID, "Register here:"),
        "poster_saved_tile": (AppiumBy.ACCESSIBILITY_ID, "Course posters"),
        "toolbar_back_button": (AppiumBy.ACCESSIBILITY_ID, "Back Button"),
        "share_poster_option": (AppiumBy.ACCESSIBILITY_ID, "Share Poster"),
        "download_poster_option": (AppiumBy.ACCESSIBILITY_ID, "Download Poster"),
        "delete_poster_option": (AppiumBy.ACCESSIBILITY_ID, "Delete poster"),
        "cancel_button": (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
        "delete_poster_confirm_button": (AppiumBy.ACCESSIBILITY_ID, "Confirm Dialog Button"),
        "no_posters_yet_label": (
            AppiumBy.ACCESSIBILITY_ID,
            "No posters yet",
        ),
        "preparing_poster_sharing_message": (AppiumBy.ACCESSIBILITY_ID, ""),
        "course_posters_overflow_menu": (AppiumBy.XPATH, '//android.view.View[@content-desc="Course posters"]/following-sibling::android.widget.Button'),
    
        "course_posters_close_share_options": (AppiumBy.ACCESSIBILITY_ID, "Course posters"),
        "Events_search_close_button": (AppiumBy.ACCESSIBILITY_ID, 'Events Search Close Button'),
        "link_element": (AppiumBy.XPATH,"//*[contains(@content-desc,'Register here')]/following-sibling::*[contains(@content-desc,'http')]"),
        "share_message_element": (AppiumBy.XPATH, "//*[contains(@text,'Registration Link')]"),
    }

    ios = {
        "edit_event_button": (AppiumBy.ACCESSIBILITY_ID, "Edit Event Button"),
        "date_time_section_label": (AppiumBy.ACCESSIBILITY_ID, "Date & Time *"),
        "event_date_field_1": (AppiumBy.ACCESSIBILITY_ID, "Event Date Field 1"),
        "event_time_field_1": (AppiumBy.ACCESSIBILITY_ID, "Event Time Field 1"),
        "event_edit_scroll": (AppiumBy.ACCESSIBILITY_ID, ""),
        "course_posters_entry": (AppiumBy.ACCESSIBILITY_ID, "Create Poster Button"),
        "poster_fab_plus": (
            AppiumBy.XPATH,
            '//XCUIElementTypeApplication[@name="QA - AOL Teacher App"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeButton',
        ),
        "template_39": (AppiumBy.ACCESSIBILITY_ID, "Template 39"),
        "poster_preview_date": (AppiumBy.ACCESSIBILITY_ID, ""),
        "poster_preview_time": (AppiumBy.ACCESSIBILITY_ID, ""),
        "add_teacher_icon": (AppiumBy.ACCESSIBILITY_ID, "Teachers Add Teacher"),
        "add_contact_icon": (AppiumBy.ACCESSIBILITY_ID, "Add Contact Add Contact"),
        "save_poster_button": (AppiumBy.ACCESSIBILITY_ID, "Save Poster"),
        "poster_qr_code": (
            AppiumBy.XPATH,
            '//XCUIElementTypeOther[@name="Glad Portal"]/XCUIElementTypeOther[2]/XCUIElementTypeImage[2]',
        ),
        "poster_url_text": (
            AppiumBy.IOS_PREDICATE,
            'label CONTAINS "https" OR name CONTAINS "https" OR value CONTAINS "https"',
        ),
        "register_here_text": (AppiumBy.ACCESSIBILITY_ID, "Register here:"),
        "poster_saved_tile": (AppiumBy.ACCESSIBILITY_ID, "Course posters"),
        "toolbar_back_button": (AppiumBy.ACCESSIBILITY_ID, "Back Button"),
        "course_posters_overflow_menu": (AppiumBy.XPATH, '//XCUIElementTypeApplication[@name="QA - AOL Teacher App"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeOther[2]/XCUIElementTypeButton[2]'),
        "share_poster_option": (AppiumBy.ACCESSIBILITY_ID, "Share Poster"),
        "download_poster_option": (AppiumBy.ACCESSIBILITY_ID, "Download Poster"),
        "delete_poster_option": (AppiumBy.ACCESSIBILITY_ID, "Delete poster"),
        "cancel_button": (AppiumBy.ACCESSIBILITY_ID, "Cancel"),
        "delete_poster_confirm_button": (AppiumBy.ACCESSIBILITY_ID, "Confirm Dialog Button"),
        "no_posters_yet_label": (
            AppiumBy.ACCESSIBILITY_ID,
            "No posters yet",
        ),
        "preparing_poster_sharing_message": (AppiumBy.ACCESSIBILITY_ID, ""),
        "course_posters_close_share_options": (
            AppiumBy.XPATH,
            '//XCUIElementTypeCollectionView[@name="activityCollectionView"]/XCUIElementTypeOther[1]/XCUIElementTypeOther',
        ),
        "Events_search_close_button": (AppiumBy.ACCESSIBILITY_ID, 'Events Search Close Button'),
        "link_element": (
            AppiumBy.IOS_PREDICATE,
            'label CONTAINS "https" OR name CONTAINS "https" OR value CONTAINS "https"',
        ),
        "share_message_element": (
            AppiumBy.IOS_PREDICATE,
            'label CONTAINS "Registration Link" OR name CONTAINS "Registration Link"',
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
