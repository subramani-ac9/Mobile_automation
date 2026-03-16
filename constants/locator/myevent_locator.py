from appium.webdriver.common.appiumby import AppiumBy


class MyEventLocator:

    android = {

        "event_template": (AppiumBy.XPATH, '//android.view.View[@content-desc="Events"]'),
        "program_template": (AppiumBy.XPATH, '//android.view.View[@content-desc="Programs"]'),
        "quotes_icon": (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Quotes Button"]'),
        'my_events_icon': (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="My Events Button"]'),
        'resources_icon': (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Resources Button"]'),
        'account_icon': (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Account Button"]'),
        "create_new_course": (AppiumBy.ACCESSIBILITY_ID, 'Create New Course Button'),
        "create_new_meetup": (AppiumBy.ACCESSIBILITY_ID, 'Create New Meetup Button'),
        "new_event": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'New {value}'.title()),
        "plus_icon": (AppiumBy.ACCESSIBILITY_ID, 'Add Event Button'),
        "advance_filter": (AppiumBy.ACCESSIBILITY_ID, 'Events Filter Button'), 
        "search_button": (AppiumBy.ACCESSIBILITY_ID, 'Events Search Button'), 
        "filter_type": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Type")]'),
        "filter_status": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Status")]'),
        "filter_mode": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Mode")]'),
        "filter_time": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc,"Time")]'),
        "filter_option": (AppiumBy.ACCESSIBILITY_ID, lambda option: f'{option}'),
        "date_range": (AppiumBy.ACCESSIBILITY_ID, 'Select Date Range'),
        "date_pencil": (AppiumBy.XPATH, '(//android.view.View[contains(@content-desc,"Date")]/following-sibling::android.widget.Button)[1]'),
        "start_date_box": (AppiumBy.XPATH, "//android.widget.EditText[contains(@hint, 'Start')]"),
        "end_date_box": (AppiumBy.XPATH, "//android.widget.EditText[contains(@hint, 'End')]"),
        "option_ok": (AppiumBy.ACCESSIBILITY_ID, 'OK'),
        "option_cancel": (AppiumBy.ACCESSIBILITY_ID, 'Cancel'),
        'show_result': (AppiumBy.ACCESSIBILITY_ID, 'Show Results'),
        "event_card": (AppiumBy.XPATH, lambda product,mode,date,time: f"//android.view.View[contains(@content-desc, '{product}') and contains(@content-desc, '{mode}') and contains(@content-desc, '{date}') and contains(@content-desc, '{time}')]"),
        "scroll": (AppiumBy.XPATH, "(((//android.view.View[(contains(@content-desc,'Online') or contains(@content-desc,'In-person')) and (contains(@content-desc,'AM') or contains(@content-desc,'PM'))])[1])/parent::*)[1]"),
        
    }

    ios = {
        "event_template": (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeOther[`name == "My Events"`]'),
        "live_darshan_icon": (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Live Darshan\nLive Darshan'),
        'my_events_icon': (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_My Events\nMy Events'),
        'resources_icon': (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Resources\nResources'),
        'account_icon': (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Account\nAccount'),
        "new_event": (AppiumBy.ACCESSIBILITY_ID, lambda value: f'New {value}'.title()),
        "plus_icon": (AppiumBy.ACCESSIBILITY_ID, 'create_event_button'),
        "advance_filter": (AppiumBy.ACCESSIBILITY_ID, 'advanced_filter_button'),
        "filter_type": (AppiumBy.XPATH, '//XCUIElementTypeOther[contains(@name,"Type")]'),
        "filter_status": (AppiumBy.XPATH, '//XCUIElementTypeOther[contains(@name,"Status")]'),
        "filter_mode": (AppiumBy.XPATH, '//XCUIElementTypeOther[contains(@name,"Mode")]'),
        "filter_time": (AppiumBy.XPATH, '//XCUIElementTypeOther[contains(@name,"Time")]'),
        "filter_option": (AppiumBy.ACCESSIBILITY_ID, lambda option: f'{option}'),
        "date_range": (AppiumBy.ACCESSIBILITY_ID, 'Select Date Range'),
        "date_pencil": (AppiumBy.XPATH, '(//XCUIElementTypeOther[contains(@name,"Date")]/following-sibling::XCUIElementTypeButton)[1]'),
        "start_date_box": (AppiumBy.XPATH, "//XCUIElementTypeTextField[contains(@name, 'Start')]"),
        "end_date_box": (AppiumBy.XPATH, "//XCUIElementTypeTextField[contains(@name, 'End')]"),
        "option_ok": (AppiumBy.ACCESSIBILITY_ID, 'OK'),
        "option_cancel": (AppiumBy.ACCESSIBILITY_ID, 'Cancel'),
        'show_result': (AppiumBy.ACCESSIBILITY_ID, 'Show Results'),
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