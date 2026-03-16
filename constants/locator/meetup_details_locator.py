from appium.webdriver.common.appiumby import AppiumBy

class MeetupDetailsLocator:

    android = {
        "event_name": (AppiumBy.ACCESSIBILITY_ID, lambda name: f'{name}'),
        "event_mode": (AppiumBy.ACCESSIBILITY_ID, lambda mode: f'{mode}'),
        "start_date": (AppiumBy.ACCESSIBILITY_ID, lambda date: f'{date}'),
        "start_time": (AppiumBy.ACCESSIBILITY_ID, lambda time: f'{time}'),
        "meetup_details": (AppiumBy.ACCESSIBILITY_ID, 'Meetup Details'),
        "event_mode2": (AppiumBy.XPATH, lambda EventType:f'//*[contains(@content-desc, "Mode") and contains(@content-desc, "{EventType}")]'),
        "event_status": (AppiumBy.XPATH, lambda status: f'//android.view.View[contains(@content-desc,"{status}")]'),
        "event_visibility": (AppiumBy.XPATH, lambda visibility: f'//android.view.View[contains(@content-desc,"{visibility}")]'),
        "max_attendees": (AppiumBy.XPATH, lambda maxAttendees: f'//*[contains(@content-desc, "Maximum Attendees") and contains(@content-desc, "{maxAttendees}")]'),
        "is_private": (AppiumBy.XPATH, lambda value: f'//*[contains(@content-desc, "Visibility") and contains(@content-desc, "{value}")]'),
        "short_url": (AppiumBy.XPATH, '//*[contains(@content-desc, "Short Url")]'),
        "ith_teacher": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Teacher")]/following-sibling::*)[{ith}]'),
        "ith_organizer": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Organizer")]/following-sibling::*)[{ith}]'),
        "ith_contact": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Contact")]/following-sibling::*)[{ith}]'),
        "start_date": (AppiumBy.ACCESSIBILITY_ID, lambda date: f'{date}'),
        "start_time2": (AppiumBy.XPATH,lambda ith: f"//android.view.View[(contains(@content-desc, 'AM') or contains(@content-desc, 'PM')) and contains(@content-desc, '-')]"),
        "location": (AppiumBy.XPATH,
                     lambda street,city,state,zipcode: f'//*[@content-desc="Location"]/following-sibling::*[contains(@content-desc, "{street}") and contains(@content-desc, "{city}") and contains(@content-desc, "{state}") and contains(@content-desc, "{zipcode}")]'),
        "meeting_url": (AppiumBy.ACCESSIBILITY_ID, lambda url: f'{url}'),
        "scroll": (AppiumBy.XPATH, "//android.widget.ScrollView"),
        "aol_center": (AppiumBy.ACCESSIBILITY_ID, lambda center: f'{center}')
               
    }

    ios = {

    }

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return MeetupDetailsLocator.android
        elif platform.lower() == 'ios':
            return MeetupDetailsLocator.ios
        else:
            raise Exception(f"Invalid platfrom :: {platform}")