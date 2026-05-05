from appium.webdriver.common.appiumby import AppiumBy


class MyEventLocator:

    android = {
        "event_template": (AppiumBy.ACCESSIBILITY_ID, 'Events'),
        "Jai_Gurudev_title": (AppiumBy.ACCESSIBILITY_ID, 'Jai Gurudev!'),
        "program_template": (AppiumBy.ACCESSIBILITY_ID, "Programs"),
        "home_icon": (AppiumBy.ACCESSIBILITY_ID, 'Home Button'),
        'my_events_icon': (AppiumBy.ACCESSIBILITY_ID, 'My Events Button'),
        'resources_icon': (AppiumBy.ACCESSIBILITY_ID, 'Resources Button'),
        'account_icon': (AppiumBy.ACCESSIBILITY_ID, 'Account Button'),
        "create_new_course": (AppiumBy.ACCESSIBILITY_ID, 'Create New Course Button'),
        "create_new_meetup": (AppiumBy.ACCESSIBILITY_ID, 'Create New Meetup Button'),
        "new_event": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'New {value}'.title()),
        "plus_icon": (AppiumBy.ACCESSIBILITY_ID, 'Add Event Button'),
        "advance_filter": (AppiumBy.ACCESSIBILITY_ID, 'Events Filter Button'), 
        "search_button": (AppiumBy.ACCESSIBILITY_ID, 'Events Search Button'), 
        "events_search_close_button": (
            AppiumBy.ACCESSIBILITY_ID,
            "Events Search Close Button",
        ),
        "filter_type": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Type")]'),
        "filter_status": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Status")]'),
        "filter_mode": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Mode")]'),
        "filter_time": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Time")]'),
        "filter_option": (AppiumBy.ACCESSIBILITY_ID, lambda option: f'{option}'),
        "option_ok": (AppiumBy.ACCESSIBILITY_ID, 'OK'),
        "option_cancel": (AppiumBy.ACCESSIBILITY_ID, 'Cancel'),
        'show_result': (AppiumBy.ACCESSIBILITY_ID, 'Show Results'),
        "event_card": (AppiumBy.XPATH, lambda product,mode,date,time: f"//android.view.View[contains(@content-desc, '{product}') and contains(@content-desc, '{mode}') and contains(@content-desc, '{date}') and contains(@content-desc, '{time}')]"),
        "event_card_by_code": (AppiumBy.XPATH, lambda code: f'//android.view.View[contains(@content-desc,"event_card|") and contains(@content-desc,"code={code}")]'),
        # Semantic event list rows: content-desc like event_card|code=...|type=course|mode=...
        "semantic_event_cards": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"event_card|")]'),
        "scroll": (AppiumBy.XPATH, "(((//android.view.View[(contains(@content-desc,'Online') or contains(@content-desc,'In-person')) and (contains(@content-desc,'AM') or contains(@content-desc,'PM'))])[1])/parent::*)[1]"),
    }

  
    ios = {
        "Jai_Gurudev_title": (
            AppiumBy.XPATH,
            '//*[(contains(@name,"Jai") and contains(@name,"Gurudev")) or '
            '(contains(@label,"Jai") and contains(@label,"Gurudev")) or '
            '(contains(@value,"Jai") and contains(@value,"Gurudev"))]',
        ),
        "event_template": (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "Events"`]'),
        "program_template": (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "Programs"`]'),
        "home_icon": (AppiumBy.XPATH, '//XCUIElementTypeImage[@name="Home Button"]'),
        #"live_darshan_icon": (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Live Darshan\nLive Darshan'),
        'my_events_icon': (AppiumBy.ACCESSIBILITY_ID, 'My Events Button'),
        'resources_icon': (AppiumBy.ACCESSIBILITY_ID, 'Resources Button'),
        'account_icon': (AppiumBy.ACCESSIBILITY_ID, 'Account Button'),
        "new_event": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'New {value}'.title()),
        "plus_icon": (AppiumBy.ACCESSIBILITY_ID, 'Add Event Button'),
        "search_button": (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Events Search Button"]'),
        "events_search_close_button": (
            AppiumBy.ACCESSIBILITY_ID,
            "Events Search Close Button",
        ),
        "advance_filter": (AppiumBy.ACCESSIBILITY_ID, 'Events Filter Button'),
        "filter_type": (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Type Filter Button"]'),
        "filter_product_type": (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Product Type Filter Button"]'),
        "filter_mode": (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Mode Filter Button"]'),
        "filter_schedule": (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Schedule Filter Button"]'),
        "filter_status": (AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Status Filter Button"]'),
        'show_result': (AppiumBy.ACCESSIBILITY_ID, 'Show Filter Results'),
        "filter_time": (AppiumBy.XPATH, '//XCUIElementTypeOther[contains(@name,"Time")]'),
        "filter_option": (AppiumBy.ACCESSIBILITY_ID, lambda option: f'{option}'),
        "date_range": (AppiumBy.ACCESSIBILITY_ID, 'Select Date Range'),
        "date_pencil": (AppiumBy.XPATH, '(//XCUIElementTypeOther[contains(@name,"Date")]/following-sibling::XCUIElementTypeButton)[1]'),
        "start_date_box": (AppiumBy.XPATH, "//XCUIElementTypeTextField[contains(@name, 'Start')]"),
        "end_date_box": (AppiumBy.XPATH, "//XCUIElementTypeTextField[contains(@name, 'End')]"),
        "option_ok": (AppiumBy.ACCESSIBILITY_ID, 'OK'),
        "option_cancel": (AppiumBy.ACCESSIBILITY_ID, 'Cancel'),
        "event_card": (AppiumBy.XPATH, lambda product,mode,date,time: f"//XCUIElementTypeOther[contains(@name, '{product}') and contains(@name, '{mode}') and contains(@name, '{date}') and contains(@name, '{time}')]"),
        "scroll": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeScrollView"),
    }

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return MyEventLocator.android
        elif platform.lower() == 'ios':
            return MyEventLocator.ios
        else:
            raise Exception(f"Invalid platfrom :: {platform}")