import time, logging
from constants.locator.meetup_details_locator import MeetupDetailsLocator
from pages.base_page import BasePage
from utils.time_zone_util import TimezoneFormatter

class MeetupDetailsPage(BasePage):

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = MeetupDetailsLocator.get_locators(platform)
        self.logger = logging.getLogger(__name__)

    def is_event_name_displayed(self, event_name):
        try:
            loc = self.build_locator(self.locator["event_name"], event_name)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Event name:: {event_name}, Exception:: {str(e)}')
            raise Exception(f"Product:: {event_name} is not present!")
    
    def is_event_mode_header_displayed(self, mode):
        try:
            loc = self.build_locator(self.locator["event_mode"], mode)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Event Mode header:: {mode}, Exception:: {str(e)}')
            raise Exception(f'Mode ::{mode} is not present on the header')
        
    def is_start_date_header_displayed(self, start_date):
        try:
            loc = self.build_locator(self.locator["start_date"], start_date)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Event StartDate header:: {start_date}, Exception:: {str(e)}')
            raise Exception(f'Start Date:: {start_date} is not present on the header')
        
    def is_start_time_header_displayed(self, start_time):
        try:
            loc = self.build_locator(self.locator["start_time"], start_time)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Event StartTime header:: {start_time}, Exception:: {str(e)}')
            raise Exception(f'Start Time:: {start_time} is not present on the header')

    def click_meetup_details(self):
        try:
            self.click_element(self.locator["meetup_details"])
        except Exception as e:
            self.logger.error(f"Exception raised while clicking the 'Meetup Details' label, Exception:: {str(e)}")
            raise Exception(f'Unable to click "Meetup Details" label')
        
    def is_event_mode_displayed(self, mode):
        try:
            loc = self.build_locator(self.locator["event_mode2"], mode)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the Event Mode:: {mode}, Exception:: {str(e)}')
            raise Exception(f'Meetup Mode:: {mode} is not present')
        
    def is_max_attendees_displayed(self, value):
        try:
            loc = self.build_locator(self.locator["max_attendees"], value)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the MaxAteendees:: {value}, Exception:: {str(e)}')
            raise Exception(f'MaxAttendees:: {value} value is not present')
        
    def is_meetup_status_displayed(self, status):
        try:
            loc = self.build_locator(self.locator["event_status"], status)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the MeetupStatus:: {status}, Exception:: {str(e)}')
            raise Exception(f'Meetup Status:: {status} is not present')
        
    def is_meetup_visibility_displayed(self, value):
        try:
            val = 'Private' if value else 'Public'
            loc = self.build_locator(self.locator["event_visibility"], val)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the MeetupVisibility:: {val}, Exception:: {str(e)}')
            raise Exception(f'Meetup Visibility:: {value} is not present')
        
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
                content = self.get_txt_from_attr(loc)
                if not content == teacher:
                    self.logger.info(f"Actual:: {content} != {teacher} ::Expected")
                    raise Exception(f"Teacher:: {teacher} is not present")
            return content == teacher
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
        
    def is_start_date_displayed(self, start_date):
        try:
            loc = self.build_locator(self.locator["start_date"], start_date)
            self.scroll_to_element(self.locator["scroll"], loc)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the StartDate:: {start_date}, Exception:: {str(e)}")
            raise Exception(f"Start Date:: {start_date} is not displayed")
        
    def is_start_time_displayed(self, start_time):
        try:
            loc = self.build_locator(self.locator["start_time"], start_time)
            self.scroll_to_element(self.locator["scroll"], loc)
            content = self.get_txt_from_attr(loc).strip()
            return content == start_time
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the contact:: {contact}, Exception:: {str(e)}")
            raise Exception(f"Start Time:: {start_time} is present")
    
    def is_location_details_displayed(self, street, city, zipcode, state):
        try:
            loc = self.build_locator(self.locator["location"], street, city, state, zipcode)
            self.logger.info(f"Prepared Location locator:: {loc}")
            self.scroll_to_element(self.locator["scroll"], loc)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception raised while verifying the LocationDetails:: Street:: {street}, City:: {city}, ZipCode:: {zipcode}, State:: {state}. Exception:: {str(e)}")
            raise Exception(f"Location Details not present")

    def is_meeting_url_displayed(self, url):
        try:
            loc = self.build_locator(self.locator["meeting_url"], url)
            self.logger.info(f"locator, :: {loc}")
            self.scroll_to_element(self.locator["scroll"], loc )
            return self.is_displayed(loc)
        except Exception as e:   
            self.logger.error(f"Exception rasied while verifying the MeetingURL:: {url}, Exception:: {str(e)}")
            raise Exception(f"Meeting Url:: {url} is not present")

        
    def is_aol_center_displayed(self, center):
        try:
            loc = self.build_locator(self.locator["aol_center"], center)
            self.scroll_to_element(self.locator["scroll"], loc)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception rasied while verifying the AOLCenter:: {center}, Exception:: {str(e)}")
            raise Exception(f"AOL Center:: {center} is not present")

    def check_event_header(self, ev_name, ev_mode, st_date, st_time):
        self.logger.info(f"Meetup Header info. : meetup_name:: {ev_name}, c_mode:: {ev_mode}, start_date:: {st_date}, start_time:: {st_time}")
        event_name = self.is_event_name_displayed(ev_name)
        event_mode1 = self.is_event_mode_header_displayed(ev_mode)
        event_start_date1 = self.is_start_date_header_displayed(st_date)
        event_start_time1 = self.is_start_time_header_displayed(st_time)
        self.logger.info(
            f"\nMeetup Header verification,\n"
            f"EventName       :: {event_name},\n"
            f"EventMode       :: {event_mode1},\n"
            f"Event StartDate :: {event_start_date1},\n"
            f"Event StartTime :: {event_start_time1} \n"
        )
        return (event_name and event_mode1 and event_start_date1 and event_start_time1)
        
    def verify_meetup_details(self, data):  # need to check event status, short url
        
        screen_content = None
        time_details = self.__get_converted_converted_time_details(data)
        try:
            header_check = self.check_event_header(data['product_name'], data['event_mode'].capitalize(), time_details[0][0], time_details[0][1].split(" - ")[0])
            if not header_check: 
                return header_check,f"Meetup Header check failed!"
            self.click_meetup_details()
            event_mode2 = self.is_event_mode_displayed(data['event_mode'].title())
            max_attendees = self.is_max_attendees_displayed(int(float(data['max_attendees'])))
            is_private = self.is_meetup_visibility_displayed(bool(data['is_private']))
            time.sleep(5)
            teachers = []
            for i in range(1, int(data["max_teachers"]) + 1):
                teachers.append(data[f'teacher{i}'])
            teachers = self.is_teachers_displayed(teachers)

            organizer = self.is_organizer_displayed(data['organizer'])
            contact = False if data['contact_person'] else True
            if data['contact_person']:   
                contact = self.is_contact_displayed(data['contact_person'])
            start_date = self.is_start_date_displayed(time_details[0][0])
            start_time = self.is_start_time_displayed(time_details[0][1])
            locOrUrl = False
            if data['event_mode'].lower() == 'in-person':
                locOrUrl = self.is_location_details_displayed(data['address'], data['city'], int(float(data['zipcode'])), data['state'].split('(')[-1].strip(')'))
            elif data['event_mode'].lower() == 'online':
                self.logger.info(f"Meeting URL:: {data['meeting_url']}")
                locOrUrl = self.is_meeting_url_displayed(data['meeting_url'])
            center = self.is_aol_center_displayed(data['aol_center'].split()[0])

            details_check = (
                event_mode2 and max_attendees and is_private and teachers and 
                organizer and contact 
                and start_time and start_date and locOrUrl and center
                )
            self.logger.info(
                f"\nEvent Body Verification,\n"
                f"eventMode    :: {event_mode2}\n"
                f"maxAttendees :: {max_attendees}\n"
                f"is_private   :: {is_private}\n"
                f"teachers     :: {teachers}\n"
                f"organizer    :: {organizer}\n"
                f"contact      :: {contact}\n"
                f"startDate    :: {start_date}\n"
                f"TimeRange    :: {start_time}\n"
                f"{'Locations' if data['event_mode'].lower() == 'in-person' else 'meeting_url'}  :: {locOrUrl}\n"
                f"center       :: {center}\n"
            )
            if not details_check:
                return details_check, ("Meetup verification failed due to details mismatch!")
            return details_check, ""
        except Exception as e:
            self.logger.error(f'Exception raised while verifying the meetup details, Exception:: {str(e)}')
            return False, f'Meetup verification failed due to {str(e)}'
        
    def __get_converted_converted_time_details(self, data):
        try:
            timezone = data['timezone']
            dates = [data['date1']]
            times = [(data['start_time1'], data['end_time1'])]
            return TimezoneFormatter.convert_times_details_to_target_timezone(dates, times, timezone)
        except Exception as e:
            self.logger.error(f"Exception riased while converting the given time to target timezone, Exception:: {str(e)}")
            raise Exception("Unable to convert the given time to target timezone")
        


         

        
                    
            
