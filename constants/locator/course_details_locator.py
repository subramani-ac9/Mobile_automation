from appium.webdriver.common.appiumby import AppiumBy

class CourseDetailsLocator:

    android = {
        
        "event_name": (AppiumBy.ACCESSIBILITY_ID, lambda name: f'{name}'),
        "event_mode": (AppiumBy.ACCESSIBILITY_ID, lambda mode: f'{mode}'),
        "start_date": (AppiumBy.ACCESSIBILITY_ID, lambda date: f'{date}'),
        "start_time": (AppiumBy.ACCESSIBILITY_ID, lambda time: f'{time}'),
        "course_details": (AppiumBy.ACCESSIBILITY_ID, 'Meetup Details Button'), # Course
        "event_mode2": (AppiumBy.XPATH, lambda EventType:f'//*[contains(@content-desc, "Mode") and contains(@content-desc, "{EventType}")]'),
        "event_status": (AppiumBy.XPATH, lambda status: f'//android.view.View[contains(@content-desc,"{status}")]'),
        "event_visibility": (AppiumBy.XPATH, lambda visibility: f'//android.view.View[contains(@content-desc,"{visibility}")]'),
        "max_attendees": (AppiumBy.XPATH, lambda maxAttendees: f'//*[contains(@content-desc, "Maximum Attendees") and contains(@content-desc, "{maxAttendees}")]'),
        "is_private": (AppiumBy.XPATH, lambda value: f'//*[contains(@content-desc, "Visibility") and contains(@content-desc, "{value}")]'),
        "short_url": (AppiumBy.XPATH, '//*[contains(@content-desc, "Short Url")]'),
        "teachers": (AppiumBy.XPATH, lambda username: f'//android.view.View[@content-desc="Teacher"]/following-sibling::android.view.View[contains(@content-desc,"{username}")]'),
        "organizers": (AppiumBy.XPATH, lambda username: f'//android.view.View[@content-desc="Organizer"]/following-sibling::android.view.View[contains(@content-desc,"{username}")]'),
        "ith_teacher": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Teacher")]/following-sibling::*)[{ith}]'),
        "ith_organizer": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Organizer")]/following-sibling::*)[{ith}]'),
        "ith_contact": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Contact")]/following-sibling::*)[{ith}]'),
        "date": (AppiumBy.ACCESSIBILITY_ID, lambda date: f'{date}'),
        "ith_time": (AppiumBy.XPATH,lambda ith: f"//android.view.View[(contains(@content-desc, 'AM') or contains(@content-desc, 'PM')) and contains(@content-desc, '-')]"),
        "location": (AppiumBy.XPATH,
                     lambda street,city,state,zipcode: f'//*[@content-desc="Location"]/following-sibling::*[contains(@content-desc, "{street}") and contains(@content-desc, "{city}") and contains(@content-desc, "{state}") and contains(@content-desc, "{zipcode}")]'),
        "scroll": (AppiumBy.XPATH, "//android.widget.ScrollView"),
        "aol_center": (AppiumBy.ACCESSIBILITY_ID, lambda center: f'{center}'),
        "Event_option_button": (AppiumBy.ACCESSIBILITY_ID, 'Event Options Button'),
        "Cancel_course_button": (AppiumBy.ACCESSIBILITY_ID, 'Cancel Course'),
        "confirm_button": (AppiumBy.ACCESSIBILITY_ID, 'Confirm Dialog Button'),
               
    }

    ios = {

    }

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return CourseDetailsLocator.android
        elif platform.lower() == 'ios':
            return CourseDetailsLocator.ios
        else:
            raise Exception(f"Invalid platfrom :: {platform}")