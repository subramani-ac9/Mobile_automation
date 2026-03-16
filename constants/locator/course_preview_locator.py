from appium.webdriver.common.appiumby import AppiumBy

class CoursePreviewLocator:
    android = {
        "event_name":(AppiumBy.ACCESSIBILITY_ID,lambda heading: f"{heading}"),
        "event_type": (AppiumBy.ACCESSIBILITY_ID, lambda EventType: f'{EventType}'),
        "event_start_datetime": (AppiumBy.ACCESSIBILITY_ID, lambda start: f'{start}'),
        "course_details": (AppiumBy.ACCESSIBILITY_ID, 'Course details'),
        "event_type2": (AppiumBy.XPATH, lambda EventType:f'//*[contains(@content-desc, "Mode") and contains(@content-desc, "{EventType}")]'),
        "event_status": (AppiumBy.XPATH, lambda status: f'//android.view.View[contains(@content-desc,"{status}")]'),
        "event_visibility": (AppiumBy.XPATH, lambda visibility: f'//android.view.View[contains(@content-desc,"{visibility}")]'),
        "max_attendees": (AppiumBy.XPATH, lambda maxAttendees: f'//*[contains(@content-desc, "Maximum Attendees") and contains(@content-desc, "{maxAttendees}")]'),
        "is_private": (AppiumBy.XPATH, '//*[contains(@content-desc, "Visibility") and contains(@content-desc, "Private")]'),
        "ith_teacher": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Teacher")]/following-sibling::*)[{ith}]'),
        "ith_organizer": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Organizer")]/following-sibling::*)[{ith}]'),
        "ith_contact": (AppiumBy.XPATH, lambda ith: f'(//*[contains(@content-desc,"Contact")]/following-sibling::*)[{ith}]'),
        "location": (AppiumBy.XPATH,
                     lambda street,city,state,zipcode: f'//*[@content-desc="Location"]/following-sibling::*[contains(@content-desc, "{street}") and contains(@content-desc, "{city}") and contains(@content-desc, "{state}") and contains(@content-desc, "{zipcode}")]'),
        "center": (AppiumBy.XPATH, lambda aol: f'//*[contains(@content-desc, "AOL Center")]/following-sibling::*[contains(@content-desc, "{aol}")]'),
        "date_time": (AppiumBy.XPATH, lambda ith: f'(//android.view.View[@content-desc="Dates, Time"]/following-sibling::*)[{ith}]'), # not use,
        "date": (AppiumBy.ACCESSIBILITY_ID, lambda date: f'{date}'),
        "time": (AppiumBy.XPATH,lambda ith: f"(//android.view.View[(contains(@content-desc, 'AM') or contains(@content-desc, 'PM')) and contains(@content-desc, '-')])[{ith}]"),
        "scroll": (AppiumBy.XPATH, "//android.widget.ScrollView"),
    }
    ios = {

    }

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return CoursePreviewLocator.android
        elif platform.lower() == 'ios':
            return CoursePreviewLocator.ios
        else:
            raise Exception(f"Invalid platform :: {platform}")