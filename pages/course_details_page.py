import time, logging
from constants.locator.course_details_locator import CourseDetailsLocator
from pages.base_page import BasePage
from utils.time_zone_util import TimezoneFormatter

class CourseDetailsPage(BasePage):

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = CourseDetailsLocator.get_locators(platform)
        self.logger = logging.getLogger(__name__)
    
    def is_course_name_displayed(self, event_name):
        try:
            loc = self.build_locator(self.locator["event_name"], event_name)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Course name:: {event_name}, Exception:: {str(e)}')
            raise Exception(f"Product:: {event_name} is not present!")
    
    def is_course_mode_header_displayed(self, mode):
        try:
            loc = self.build_locator(self.locator["event_mode"], mode)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Course Mode header:: {mode}, Exception:: {str(e)}')
            raise Exception(f'Mode ::{mode} is not present on the header')
        
    def is_start_date_header_displayed(self, start_date):
        try:
            loc = self.build_locator(self.locator["start_date"], start_date)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Course StartDate header:: {start_date}, Exception:: {str(e)}')
            raise Exception(f'Start Date:: {start_date} is not present on the header')
        
    def is_start_time_header_displayed(self, start_time):
        try:
            loc = self.build_locator(self.locator["start_time"], start_time)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Course StartTime header:: {start_time}, Exception:: {str(e)}')
            raise Exception(f'Start Time:: {start_time} is not present on the header')

    def click_course_details(self):
        try:
            self.click_element(self.locator["course_details"])
        except Exception as e:
            self.logger.error(f"Exception raised while clicking the 'Course Details' label, Exception:: {str(e)}")
            raise Exception(f'Unable to click "Course Details" label')
        
    def is_course_mode_displayed(self, mode):
        try:
            loc = self.build_locator(self.locator["event_mode2"], mode)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Course Mode:: {mode}, Exception:: {str(e)}')
            raise Exception(f'Course Mode:: {mode} is not present')
        
    def is_max_attendees_displayed(self, value):
        try:
            loc = self.build_locator(self.locator["max_attendees"], value)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the MaxAteendees:: {value}, Exception:: {str(e)}')
            raise Exception(f'MaxAttendees:: {value} value is not present')
        
    def is_course_status_displayed(self, status):
        try:
            loc = self.build_locator(self.locator["event_status"], status)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the CourseStatus:: {status}, Exception:: {str(e)}')
            raise Exception(f'Course Status:: {status} is not present')
        
    def is_course_visibility_displayed(self, value):
        val = 'Private' if value else 'Public'
        try:
            loc = self.build_locator(self.locator["event_visibility"], val)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the CourseVisibility:: {val}, Exception:: {str(e)}')
            raise Exception(f'Course Visibility:: {val} is not present')
        
    def is_short_url_displayed(self):
        content = "Not Obtained Yet!"
        try:
            content = self.get_txt_from_attr(self.locator["short_url"])
            return content.find('http')
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the ShortURL:: {content}, Exception:: {str(e)}")
            raise Exception(f"Short Url is not present!")
    
    def is_teachers_displayed(self, teacehrs: list[str]):
        try:
            for index, teacher in enumerate(teacehrs):
                loc = self.build_locator(self.locator['ith_teacher'], str(index + 1))
                self.scroll_to_element(self.locator["scroll"], loc)
                content = self.get_txt_from_attr(loc).strip()
                if not content == teacher:
                    self.logger.info(f"Actual:: {content} != {teacher} ::Expected")
                    raise Exception(f"Teacher:: {teacher} is not present")
            return True
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the teachers:: {teacehrs}, Exception:: {str(e)}")
            raise Exception(str(e))


    def is_organizer_displayed(self, organizer):
        try:    
            loc = self.build_locator(self.locator["ith_organizer"], "1")
            self.scroll_to_element(self.locator["scroll"], loc)
            content = self.get_txt_from_attr(loc).strip()
            return content == organizer
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the organizer:: {organizer}, Exception:: {str(e)}")
            raise Exception(f"Organizer:: {organizer} is not present")
        
    def is_contact_displayed(self, contact):
        try:
            loc = self.build_locator(self.locator["ith_contact"], "1")
            self.scroll_to_element(self.locator["scroll"], loc)
            content = self.get_txt_from_attr(loc).strip()
            return content == contact
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the contact:: {contact}, Exception:: {str(e)}")
            raise Exception(f'Contact:: {contact} is not present')
        
    def is_dates_displayed(self, dates):
        try:
            for index, date in enumerate(dates):
                loc = self.build_locator(self.locator['date'], date)
                self.scroll_to_element(self.locator["scroll"], loc)
                content = self.get_txt_from_attr(loc).strip()
                if not content == date:
                    self.logger.info(f"Actual--> {content} != {date} <--Expected")
                    raise Exception(f"Date:: {date} is not present")
            return True
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the dates:: {dates}, Exception:: {str(e)}")
            raise Exception(str(e))
        
    def is_times_displayed(self, times):
        try:
            for index, time in enumerate(times):
                loc = self.build_locator(self.locator['ith_time'], index)
                self.scroll_to_element(self.locator["scroll"], loc)
                content = self.get_txt_from_attr(loc).strip()
                if not content == time:
                    self.logger.info(f"Actual--> {content} != {time} <--Expected")
                    raise Exception(f"Time:: {time} is not present")
            return True
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the times:: {times}, Exception:: {str(e)}")
            raise Exception(str(e))
    
    def is_location_details_displayed(self, street, city, zipcode, state):
        try:
            loc = self.build_locator(self.locator["location"], street, city, state, zipcode)
            self.logger.info(f"Prepared Location locator:: {loc}")
            self.scroll_to_element(self.locator["scroll"], loc)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the LocationDetails:: Street:: {street}, City:: {city}, ZipCode:: {zipcode}, State:: {state}. Exception:: {str(e)}")
            raise Exception(f"Location Details not present")
        
    def is_aol_center_displayed(self, center):
        try:
            loc = self.build_locator(self.locator["aol_center"], center)
            self.scroll_to_element(self.locator["scroll"], loc)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception rasied while verifying the AOLCenter:: {center}, Exception:: {str(e)}")
            raise Exception(f"AOL Center:: {center} is not present")

    def check_course_header(self, ev_name, ev_mode, st_date, st_time):
        self.logger.info(f"Course Header info. : course_name:: {ev_name}, course_mode:: {ev_mode}, start_date:: {st_date}, start_time:: {st_time}")
        event_name = self.is_course_name_displayed(ev_name)
        event_mode1 = self.is_course_mode_header_displayed(ev_mode)
        event_start_date1 = self.is_start_date_header_displayed(st_date)
        event_start_time1 = self.is_start_time_header_displayed(st_time)
        self.logger.info(
            f"\nCourse Header verification,\n"
            f"CourseName       :: {event_name},\n"
            f"CourseMode       :: {event_mode1},\n"
            f"Course StartDate :: {event_start_date1},\n"
            f"Course StartTime :: {event_start_time1} \n"
        )
        return (event_name and event_mode1 and event_start_date1 and event_start_time1)
        
    def verify_course_details(self, data):  # need to check event status, short url
        screen_content = None
        time_details = self.__get_converted_converted_time_details(data)
        try:
            header_check = self.check_course_header(data['product_name'], data['event_mode'].capitalize(), time_details[0][0], time_details[0][1].split(" - ")[0])
            if not header_check: 
                return header_check,f"Course Header check failed!, course_name:: {event_name}, course_mode:: {event_mode1}, event_start_date:: {event_start_date1}, event_start_time:: {event_start_time1}"
            self.click_course_details()
            event_mode2 = self.is_course_mode_displayed(data['event_mode'].title())
            max_attendees = self.is_max_attendees_displayed(int(float(data['max_attendees'])))
            is_private = self.is_course_visibility_displayed(data['is_private'].lower() == 'true')
            time.sleep(10)
            teachers = []
            for i in range(1, int(data["max_teachers"]) + 1):
                teachers.append(data[f'teacher{i}'])
            teachers = self.is_teachers_displayed(teachers)

            organizer = self.is_organizer_displayed(data['organizer'])
            contact = False if data['contact_person'] else True
            contact = self.is_contact_displayed(data['contact_person'])
            dates, times = [], []
            self.logger.info(f"Time Details:: {time_details}")
            for i in range(0, int(data['no_of_dates'])): 
                dates.append(time_details[i][0])
                times.append(time_details[i][1])
            start_date = self.is_dates_displayed(dates)
            start_time = self.is_times_displayed(times)
            location = False if data['event_mode'].lower() == 'in-person' else True
            if data['event_mode'].lower() == 'in-person':
                location = self.is_location_details_displayed(data['address'], data['city'], int(float(data['zipcode'])), data['state'].split('(')[-1].strip(')'))
            center = self.is_aol_center_displayed(data['aol_center'].split()[0])
            details_check = (
                event_mode2 and max_attendees and is_private and teachers and 
                organizer and contact 
                and start_time and start_date and location and center
                )
            self.logger.info(
                f"\Course Body Verification,\n"
                f"courseMode    :: {event_mode2}\n"
                f"maxAttendees :: {max_attendees}\n"
                f"is_private   :: {is_private}\n"
                f"teachers     :: {teachers}\n"
                f"organizer    :: {organizer}\n"
                f"contact      :: {contact}\n"
                f"startDate    :: {start_date}\n"
                f"TimeRange    :: {start_time}\n"
                f"{'Locations' if data['event_mode'].lower() == 'in-person' else 'NoLocation'}  :: {location}\n"
                f"center       :: {center}\n"
            )
            if not details_check:
                return details_check, ("Course verification failed due to details mismatch!")
            return details_check, ""
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the course details, Exception:: {str(e)}')
            return False, f'Course verification failed due to {str(e)}'
        
    def __get_converted_converted_time_details(self, data):
        try:
            dates, times =[], []
            no_dates = int(data['no_of_dates'])
            for i in range(1, no_dates + 1):
                dates.append(data[f'date{i}'])
                times.append((data[f'start_time{i}'], data[f'end_time{i}']))
            timezone = data['timezone']
            return TimezoneFormatter.convert_times_details_to_target_timezone(dates, times, timezone)
        except Exception as e:
            self.logger.error(f"Exception riased while converting the given time to target timezone, Exception:: {str(e)}")
            raise Exception("Unable to convert the given time to target timezone")