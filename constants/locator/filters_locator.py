from appium.webdriver.common.appiumby import AppiumBy


class FiltersLocator:
    # From Appium hierarchy: left category rail = first scrollable ancestor of "Type Filter Button".
    # Outer modal often has another scrollable View — use category-specific xpath so UiScrollable targets the rail.
    ANDROID_CATEGORY_RAIL_SCROLLER_XPATH = (
        '//android.widget.Button[@content-desc="Type Filter Button"]/'
        'ancestor::android.view.View[@scrollable="true"][1]'
    )
    # First scrollable root in the filter dialog (full panel) — fallback when inner list scroll isn’t enough.
    ANDROID_FILTER_DIALOG_SCROLLER_XPATH = '(//android.view.View[@scrollable="true"])[1]'
    # Right-column option rows only (excludes left rail “… Filter Button”).
    ANDROID_OPTIONS_CHECKBOX_XPATH = (
        '//android.widget.Button['
        'contains(@content-desc,"Checkbox") '
        'and not(contains(@content-desc,"Filter Button"))'
        ']'
    )

    android = {
        "header_filter_button" : (AppiumBy.ACCESSIBILITY_ID, 'Events Filter Button'),
        
        # common checkboxes — "All" uses the same content-desc in each open category column
        "filter_type_all_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'All Checkbox'),
        "filter_product_type_all_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'All Checkbox'),
        "filter_mode_all_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'All Checkbox'),
        "filter_schedule_all_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'All Checkbox'),
        "filter_status_all_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'All Checkbox'),
        "filter_role_all_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'All Checkbox'),
        "filter_show_result_button" : (AppiumBy.ACCESSIBILITY_ID, 'Show Filter Results'),
        "filter_reset_button" : (AppiumBy.ACCESSIBILITY_ID, 'Reset Filter Button'),


        # filter based on type
        "filter_type" : (AppiumBy.ACCESSIBILITY_ID, 'Type Filter Button'),
        "filter_type_course_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Course Checkbox'),
        "filter_type_meetup_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Meetup Checkbox'),
        "filter_type_ticketed_event_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Ticketed Event Checkbox'),

        # filter based on product type
        "filter_product_type" : (AppiumBy.ACCESSIBILITY_ID, 'Product Type Filter Button'),
        "filter_product_type_aol_part1_online" : (AppiumBy.ACCESSIBILITY_ID, 'Art of Living Part 1 - Online Checkbox'),
        "filter_product_type_aol_part1_in_person" : (AppiumBy.ACCESSIBILITY_ID, 'Art of Living Part 1 - In Person Checkbox'),
        "filter_product_type_sahaj_samadhi_meditation_in_person" : (AppiumBy.ACCESSIBILITY_ID, 'Sahaj Samadhi Meditation - In Person Checkbox'),
        "filter_product_type_sahaj_samadhi_meditation_online" : (AppiumBy.ACCESSIBILITY_ID, 'Sahaj Samadhi Meditation - Online Checkbox'),
        "filter_product_type_short_sky_meditation_meetup_online" : (AppiumBy.ACCESSIBILITY_ID, 'Short SKY Meditation Meetup - Online Checkbox'),
        "filter_product_type_short_sky_meditation_meetup_in_person" : (AppiumBy.ACCESSIBILITY_ID, 'Short SKY Meditation Meetup - In Person Checkbox'),
        "filter_product_type_sleep_and_anxiety_protocol_in_person" : (AppiumBy.ACCESSIBILITY_ID, 'Sleep and Anxiety Protocol - In Person Checkbox'),
        "filter_product_type_sahaj_samadhi_meditation_meetup_in_person" : (AppiumBy.ACCESSIBILITY_ID, 'Sahaj Samadhi Meditation Meetup - In Person Checkbox'),
        "filter_product_type_long_sky_meetup_in_person" : (AppiumBy.ACCESSIBILITY_ID, 'Long SKY Meetup - In Person Checkbox'),

        #filter based on mode
        "filter_mode" : (AppiumBy.ACCESSIBILITY_ID, 'Mode Filter Button'),
        "filter_mode_in_person_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'In-person Checkbox'),
        "filter_mode_online_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Online Checkbox'),

        #filter based on schedule
        "filter_schedule" : (AppiumBy.ACCESSIBILITY_ID, 'Schedule Filter Button'),
        "filter_schedule_upcoming_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Upcoming Checkbox'),
        "filter_schedule_past_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Past Checkbox'),
        "filter_schedule_custom_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Custom Checkbox'),
        # custom schedule
        "filter_schedule_sort_order_toggle" : (AppiumBy.ACCESSIBILITY_ID, 'Sort Order Toggle'),
        "filter_schedule_date_range_picker" : (AppiumBy.ACCESSIBILITY_ID, 'Date Range Picker'),
        "range_start_date" : (AppiumBy.ACCESSIBILITY_ID,lambda date: f'{date}'), # eg: (19, Thursday, March 19, 2026, Today) -> Today dates , (20, Thursday, March 19, 2026) -> normal dates)
        "range_end_date" : (AppiumBy.ACCESSIBILITY_ID,lambda date: f'{date}'), 
        "Save_button" : (AppiumBy.ACCESSIBILITY_ID, 'Save'),
        "Cancel_button" : (AppiumBy.ACCESSIBILITY_ID, 'Close'),

        #filter based on status
        "filter_status" : (AppiumBy.ACCESSIBILITY_ID, 'Status Filter Button'),
        "filter_status_open_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Open Checkbox'),
        "filter_status_closed_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Closed Checkbox'),
        "filter_status_declined_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Declined Checkbox'),
        "filter_status_active_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Active Checkbox'),
        "filter_status_inactive_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Inactive Checkbox'),
        "filter_status_cancelled_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Cancelled Checkbox'),
        "filter_status_expense_submitted_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Expense Submitted Checkbox'),
        "filter_status_expense_declined_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Expense Declined Checkbox'),
        "filter_status_pending_activation_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Pending Activation Checkbox'),


        # filter based on role (UI: "My Role Filter Button" in Appium Inspector)
        "filter_role" : (AppiumBy.ACCESSIBILITY_ID, 'My Role Filter Button'),
        "filter_role_teacher_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Teacher Checkbox'),
        "filter_role_organizer_checkBox" : (AppiumBy.ACCESSIBILITY_ID, 'Organizer Checkbox'),
    }


    ios = {**android}


    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return FiltersLocator.android
        elif platform.lower() == 'ios':
            return FiltersLocator.ios
        else:
            raise Exception(f"Invalid platform :: {platform}")