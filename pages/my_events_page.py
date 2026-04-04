import logging
import time
import allure
from pages.base_page import BasePage
from constants.flutter_keys import FlutterKeys
from constants.locator.myevent_locator import MyEventLocator
from utils.time_zone_util import TimezoneFormatter
from pages.meetup_details_page import MeetupDetailsPage
from pages.course_details_page import CourseDetailsPage

class MyEventsPage(BasePage):
    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = MyEventLocator.get_locators(platform)
        self.meetup_details_page = MeetupDetailsPage(driver, platform)
        self.course_detils_page = CourseDetailsPage(driver, platform)
    
    @allure.step("Verify dashboard is displayed for tenant: {tenant}")
    def is_dashboard_displayed(self, tenant):
        try:
            # Use longer timeout for dashboard detection after login transition
            self.click_element(self.locator['my_events_icon'])
            if(tenant.lower() == 'us'):
                locator = self.locator['event_template']
            else:
                locator = self.locator['program_template']

            result = self.is_displayed(locator, 40)
            self.logger.debug(f"Dashboard check result: {result} for tenant {tenant}, locator: {locator}")
            return result
        except Exception as e:
            self.logger.error(f"Error checking dashboard display: {e}")
            return False
    
    @allure.step("Verify bottom navigation is displayed")
    def is_bottom_navigation_displayed(self):
        required_icons = {
            "Home": self.locator["home_icon"],
            "Events": self.locator["my_events_icon"],
            "Resources": self.locator["resources_icon"],
            "Account": self.locator["account_icon"]
        }

        for name, locator in required_icons.items():
            try:
                # Use longer timeout for navigation elements after login transition
                if not self.is_displayed(locator):
                    self.logger.warning(f"Missing bottom navigation icon: {name} with locator: {locator}")
                    return False
                else:
                    self.logger.debug(f"Found bottom navigation icon: {name}")
            except Exception as e:
                self.logger.error(f"Error checking {name} navigation icon: {e}")
                return False
        
        self.logger.info("All bottom navigation icons found")
        return True

    # @allure.step("Checking Event Page elements are displayed")
    def check_event_page_elements(self, tenant):

        elements = {
            "Bottom navigation": self.is_bottom_navigation_displayed(),
            "header title": self.is_dashboard_displayed(tenant),
            "Advance filter": self.is_displayed(self.locator['advance_filter']),
            "Search button": self.is_displayed(self.locator['search_button'])
        }

        for element, status in elements.items():
            if status:
                self.logger.info(f"{element} displayed")
            else:
                self.logger.info(f"{element} not displayed")

        return all(elements.values())

    @allure.step("Wait for dashboard to load")
    def wait_for_dashboard_to_load(self, timeout=60, tenant='us'):
        return (self.is_dashboard_displayed(tenant) and
                self.is_bottom_navigation_displayed())
    
    @allure.step("Navigate to Live Darshan")
    def navigate_to_live_darshan(self):
        self.click_element(self.locator['live_darshan_icon'])
        self.wait_for_page_load()
    
    @allure.step("Navigate to Events tab")
    def navigate_to_events(self):
        self.click_element(self.locator['my_events_icon'])
        self.wait_for_page_load()
    
    @allure.step("Navigate to Resources tab")
    def navigate_to_resources(self):
        self.click_element(self.locator['resources_icon'])
        self.wait_for_page_load()
    
    @allure.step("Navigate to Account tab")
    def navigate_to_account(self):
        self.click_element(self.locator['account_icon'])
        self.wait_for_page_load()
    
    def is_events_screen_displayed(self):
        return self.is_displayed(self.locator['event_template'])
    
    def get_events_screen_title(self):
        return self.get_element_text(self.locator['event_template'])
    
    @allure.step("Tap Add Event (+) button")
    def click_add_event_button(self):
        self.click_element(self.locator['plus_icon']) 
        self.wait_for_page_load()

    @allure.step("Select create event type: {event_type}")
    def select_create_event_button(self, event_type):
        if(event_type.lower() == 'course'):
            self.click_element(self.locator['create_new_course'])
        else:
            self.click_element(self.locator['create_new_meetup'])  
        self.wait_for_page_load()
    
    #need to update 
    def is_events_list_displayed(self):
        return self.is_displayed(self.locator['list_view'])

    #need to update 
    def get_events_count(self):
        try:
            event_elements = self.driver_manager.find_elements_by_key("event_item_", 5)
            count = len(event_elements)
            self.logger.info(f"Found {count} events on the page")
            return count
        except Exception:
            return 0
    
    #need to update 
    def get_event_names(self):
        try:
            name_elements = self.driver_manager.find_elements_by_key("event_name_", 10)
            names = [element.text for element in name_elements if element.text]
            self.logger.info(f"Retrieved {len(names)} event names")
            return names
        except Exception as e:
            self.logger.error(f"Failed to get event names: {str(e)}")
            return []
    
    def click_first_event(self):
        try:
            event_elements = self.driver_manager.find_elements_by_key("event_item_", 10)
            if event_elements:
                event_elements[0].click()
                self.logger.info("Clicked on first event")
                self.wait_for_page_load()
                return True
            else:
                self.logger.error("No events found to click")
                return False
        except Exception as e:
            self.logger.error(f"Failed to click first event: {str(e)}")
            return False
    
    def click_event_by_name(self, event_name):
        try:
            event_name_key = FlutterKeys.get_event_name(event_name)
            event_elements = self.driver_manager.find_elements_by_key(event_name_key, 10)
            
            if event_elements:
                event_elements[0].click()
                self.logger.info(f"Clicked on event: {event_name}")
                self.wait_for_page_load()
                return True
            else:
                self.logger.error(f"Event with name '{event_name}' not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to click event by name '{event_name}': {str(e)}")
            return False
    
    def get_event_time(self, event_name):
        try:
            event_time_key = FlutterKeys.get_event_time(event_name)
            return self.get_element_text(event_time_key)
        except Exception as e:
            self.logger.error(f"Failed to get event time for '{event_name}': {str(e)}")
            return ""
    
    def get_event_attendees(self, event_name):
        try:
            event_attendees_key = FlutterKeys.get_event_attendees(event_name)
            return self.get_element_text(event_attendees_key)
        except Exception as e:
            self.logger.error(f"Failed to get event attendees for '{event_name}': {str(e)}")
            return ""
    
    @allure.step("Validate successful login (dashboard and navigation)")
    def validate_successful_login(self, tenant):
        validations = []
        assert self.is_displayed(self.locator['Jai_Gurudev_title'],20), "Jai Gurudev! title should be displayed"
        self.logger.info("Starting login validation checks...")
        
        self.logger.debug("Checking bottom navigation elements...")
        nav_displayed = self.is_bottom_navigation_displayed()
        if nav_displayed:
            validations.append("Bottom navigation is displayed")
            self.logger.info("Bottom navigation is displayed")
        else:
            validations.append("Bottom navigation is not displayed")
            self.logger.warning("No navigation elements found - login failed")


        # -------- Dashboard Check --------
        self.logger.debug("Checking dashboard display...")
        self.click_element(self.locator["my_events_icon"])
        dashboard_displayed = self.is_dashboard_displayed(tenant)

        if dashboard_displayed:
            validations.append("Dashboard is displayed")
            self.logger.info("Dashboard is displayed")
        else:
            validations.append("Dashboard is not displayed")
            self.logger.warning("No dashboard elements found - login failed")
 
        # -------- Final Login Status --------
        if nav_displayed and dashboard_displayed:
            validations.append("Main screen is displayed")
        else:
            validations.append("Main screen is not displayed")

        self.logger.info(f"Login validation completed. Results: {validations}")

        return validations

    
    def is_logged_in(self, tenant='us'):
        return (self.is_dashboard_displayed(tenant) and
                self.is_bottom_navigation_displayed())
    
    def navigate_to_course_tab(self):
        self.navigate_to_resources()
    
    #need to update
    def navigate_to_dashboard_tab(self, tenant='us'):
        if not self.is_dashboard_displayed(tenant):
            pass
    
    #need to update
    def navigate_to_profile_tab(self):
        self.navigate_to_account()
    
    def validate_events_screen(self):
        validations = []    
        if self.is_events_screen_displayed():
            validations.append("Events screen is displayed")
            elements_to_check = [
                (self.event_keys['screen_title'], "Events screen title"),
                (self.event_keys['add_button'], "Add event button"),
                (self.event_keys['list_view'], "Events list view")
            ]
            
            for key, description in elements_to_check:
                if self.is_displayed(key, 5):
                    validations.append(f"{description} is visible")
                else:
                    validations.append(f"{description} is not visible")
        else:
            validations.append("Events screen is not displayed")
        
        return validations
    
    def is_live_darshan_screen_displayed(self):
        return self.is_displayed(FlutterKeys.LIVE_DARSHAN_SCREEN)
    
    def is_resources_screen_displayed(self):
        return self.is_displayed(FlutterKeys.RESOURCES_SCREEN)
    
    def is_account_screen_displayed(self):
        return self.is_displayed(FlutterKeys.ACCOUNT_SCREEN) 
    
    # def convert_the_event_timing_to_system_timezone(self, data):a


    
    def __prepare_event_card_locator(self, data):
        try:
            dates = []
            times = []
            timezone = data['timezone']
            if data['event_type'].lower() == 'course' or data['event_type'].lower() == 'meetup':
                no_dates = 1 if data['event_type'].lower() == 'meetup' else int(data['no_of_dates'])
                for i in range(1, no_dates + 1):
                    dates.append(data[f'date{i}'])
                    times.append((data[f'start_time{i}'], data[f'end_time{i}']))
            else: 
                raise Exception(f"Invalid Event Type:: {data['event_type']}")
            # Extract timezone abbreviation from full timezone string (e.g., "Mountain Time - MST" -> "MST")
            timezone_abbr = data['timezone'].split(' - ')[-1] if ' - ' in data['timezone'] else data['timezone']
            self.logger.debug(f"Original timezone: {data['timezone']}, Extracted abbreviation: {timezone_abbr}")
            converted_details = TimezoneFormatter.convert_times_details_to_target_timezone(dates, times, timezone_abbr)
            event_card_locator = self.build_locator(self.locator["event_card"], data['product_name'], data['event_mode'].capitalize(), converted_details[0][0], converted_details[0][1].split("-")[0].strip())
            return event_card_locator
        except Exception as e:
            self.logger.error(f"Exception raised while preparing the event card, Exception:: {str(e)}")
            raise Exception(f"Unable to parse the event card :{str(e)}")
    
    def pick_event_card(self, data):
        try:
            can = True
            event_card_loc = self.__prepare_event_card_locator(data)
            print(f"Event card locator:: {event_card_loc}")
            self.logger.info(f"Prepared event card:: {event_card_loc}")
            while can:
                cards = self.find_elements(event_card_loc)
                print(f"Cards:: {cards}")
                self.logger.info(f"{len(cards)} event card with same info on the MyEvents page")
                for index, card in enumerate(cards):
                    self.click_element(card)
                    result, msg = self.meetup_details_page.verify_meetup_details(data) if data['event_type'].lower() == 'meetup' else self.course_detils_page.verify_course_details(data)
                    print(f"Result:: {result}")
                    print(f"Message:: {msg}")
                    if result:
                        self.driver.back()
                        return True
                    else: 
                        self.logger.error(f"({index+1}) --> Event card details mismatches. Reason:: {str(msg)}")
                        self.driver.back()

                scroll = self.find_element(self.locator["scroll"])
                can = self.scroll_on_the_element(scroll, percent = 0.9)

                cards = self.find_elements(event_card_loc)
                self.logger.info(f"Found {len(cards)} event card with same info on the MyEvents page")
                for index, card in enumerate(cards):
                    self.click_element(card)
                    result, msg = self.meetup_details_page.verify_meetup_details(data) if data['event_type'].lower() == 'meetup' else self.course_detils_page.verify_course_details(data)
                    if result:
                        self.driver.back()
                        return True
                    else:
                        self.logger.error(f"({index+1}) --> Event card details mismatches. Reason:: {str(msg)}")
                        self.driver.back()
        except Exception as e:
            self.logger.error(f"Failed at Event Card selection, Screen Content:: {self.extract_page_contents()}, {str(e)}")
            return False, f"Failed at Event Card selection due to {str(e)}"
            
    def click_advance_filter_option(self):
        try:
            self.wait_for_element_to_be_clickable(self.locator["advance_filter"])
            self.click_element(self.locator["advance_filter"])
        except Exception as e:
            self.logger.error(f"Exception rasied while clicking the 'Advance Filter' icon, exception:: {str(e)}")
            raise Exception(f"Unable to select advance-filter option")
    
    def click_show_result_button(self):
        try:
            self.click_element(self.locator["show_result"])
        except Exception as e:
            self.logger.error(f"Exception raised while clicking the 'Show Result' button, Exception:: {str(e)}")
            raise Exception(f"Unable to click the show result button")
            
        
    def choose_filter_type(self, types: list[str]):
        self.logger.info(f"Filtering by types: {types}")
        try:
            if types and len(types) > 0:
                self.click_element(self.locator["filter_type"])
                for t in types:
                    loc = self.build_locator(self.locator["filter_option"], t)
                    self.logger.info(f"Prepared filter locator:: Type:: {loc}")
                    self.click_element(loc)
        except Exception as e:
            self.logger.error(f"Exception raised while selecting the 'Type' filter, exception:: {str(e)}")
            raise Exception(f"Unable to choose 'Type' options in the advance-filter")
    
    def choose_filter_mode(self, modes: list[str]):
        self.logger.info(f"Filtering by modes: {modes}")
        try:
            if modes and len(modes) > 0:
                self.click_element(self.locator["filter_mode"])
                for mode in modes:
                    loc = self.build_locator(self.locator["filter_option"], mode)
                    self.logger.info(f"Prepared filter locator:: Mode:: {loc}")
                    self.click_element(loc)
            else:
                self.logger.info("Given ModeFilter list is passed as empty")
        except Exception as e:
            self.logger.error(f"Exception raised while selecting 'Mode' filter, exception:: {str(e)}")
            raise Exception(f"Unable to choose 'Mode' options in the advance-filter")
            
    def choose_filter_status(self, statuses: list[str]):
        self.logger.info(f"Filtering by statuses: {statuses}")
        try:
            if statuses and len(statuses) > 0:
                self.click_element(self.locator["filter_status"])
                for status in statuses:
                    loc = self.build_locator(self.locator["filter_option"], status)
                    self.logger.info(f"Prepared filter locator:: Status:: {loc}")
                    self.click_element(loc)
            else:
                self.logger.info("Given FilterStatus List is passed as empty")
        except Exception as e:
            self.logger.error(f"Exception raised while selecting the 'Status' filter, exception:: {str(e)}")
            raise Exception(f"Unable to choose 'Status' options in the advance-filter")
            
    def choose_filter_time(self, times: list[str], date_range):
        try:
            self.click_element(self.locator["filter_time"])
            if date_range:
                custom = self.build_locator(self.locator['filter_option'], 'Custom')
                self.logger.info(f"Prepared Custom - filter xpath:: {custom}")
                self.click_element(custom)
                self.click_element(self.locator["date_range"])
                self.click_element(self.locator["date_pencil"])
                self.click_element(self.locator["start_date_box"])
                self.send_keys(self.locator["start_date_box"], date_range[0])
                self.click_element(self.locator["end_date_box"])
                self.send_keys(self.locator["end_date_box"], date_range[1])
                self.click_element(self.locator["option_ok"])
            elif times and len(times) > 0:
                for time in times:
                    loc = self.build_locator(self.locator["filter_option"], time)
                    self.click_element(loc)
            else:
                self.logger.info(f"Given TimeFilter List and DateRange list are passed as empty")
        except Exception as e:
            self.logger.error(f"Exception raised while choose 'Time' filter, Exception:: {str(e)}")
            raise Exception(f"Unable to select 'Time' options in the advance-filter")
     
    def choose_advance_filter(self, types=None, modes=None, statuses=None, times=None,  date_range=None):
        self.logger.info(f"Method parameters:: Type:: {types}, Modes:: {modes}, Status:: {statuses}, Times:: {times}, DateRange:: {date_range}")
        try:
            self.click_advance_filter_option()
            self.choose_filter_mode(modes)
            self.choose_filter_type(types)
            self.choose_filter_status(statuses)
            self.choose_filter_time(times, date_range)
            self.click_show_result_button()
            return True, ""
        except Exception as e:
            self.logger.error(f"Exception raised while selecting the advance-filter option:: {str(e)}")
            return False, f'Advance filter selection is failed due to {str(e)}'

    def find_and_click_event_by_name(self, event_name):
        """
        Find and click an event by its name for editing
        """
        try:
            self.logger.info(f"Searching for event: {event_name}")
            event_locator = self.build_locator(self.locator["event_by_name"], event_name)
            
            # Scroll to find the event if not immediately visible
            self.scroll_to_element(self.locator["scroll"], event_locator)
            time.sleep(2)
            
            if self.is_displayed(event_locator):
                element = self.find_element(event_locator)
                element.click()
                self.logger.info(f"Successfully clicked on event: {event_name}")
                return True
            else:
                self.logger.warning(f"Event not found: {event_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error finding event {event_name}: {e}")
            return False

    def search_event(self, search_term):
        """
        Search for an event using search functionality
        """
        try:
            self.logger.info(f"Searching for event with term: {search_term}")
            
            # Check if search functionality is available
            if "search_button" in self.locator:
                self.click_element(self.locator["search_button"])
                time.sleep(1)
                
                if "search_field" in self.locator:
                    self.send_keys(self.locator["search_field"], search_term)
                    time.sleep(2)
                    return True
            
            # If no search functionality, return True to continue with browsing
            self.logger.info("No search functionality available, will browse events")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in search functionality: {e}")
            return False

    def click_first_event_card(self):
        """
        Click on the first available event card
        """
        try:
            self.logger.info("Clicking on first available event card")
            
            # Use a generic locator for first event card
            if "first_event_card" in self.locator:
                first_event_locator = self.locator["first_event_card"]
            else:
                # Fallback to event template
                first_event_locator = self.locator["event_template"]
            
            if self.is_displayed(first_event_locator):
                self.click_element(first_event_locator)
                self.logger.info("Successfully clicked on first event card")
                return True
            else:
                self.logger.warning("No event cards found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error clicking first event card: {e}")
            return False

    def are_events_displayed(self):
        """
        Check if events are displayed in card format
        """
        try:
            return self.is_displayed(self.locator["event_template"])
        except Exception as e:
            self.logger.error(f"Error checking events display: {e}")
            return False

    def get_event_count(self):
        """
        Get the count of displayed events
        """
        try:
            events = self.find_elements(self.locator["event_template"])
            return len(events)
        except Exception as e:
            self.logger.error(f"Error getting event count: {e}")
            return 0

    def _semantic_label_from_card_element(self, el):
        if self.platform.lower() == "ios":
            return el.get_attribute("name") or ""
        return el.get_attribute("content-desc") or ""

    @allure.step("Collect parsed semantic event cards (event_card|...)")
    def get_parsed_semantic_event_cards(self):
        """Return list of dicts from content-desc/name labels starting with event_card|."""
        loc = self.locator.get("semantic_event_cards")
        if not loc:
            return []
        elements = self.find_elements(loc)
        out = []
        for el in elements:
            desc = self._semantic_label_from_card_element(el)
            if desc.startswith("event_card|"):
                out.append(self.parse_event_data(desc))
        return out

    @allure.step("Verify visible event cards match applied filters (semantic labels)")
    def verify_visible_cards_match_applied_filters(
        self,
        filters: dict,
        start_date_str=None,
        end_date_str=None,
        *,
        allow_empty: bool = False,
        reference_date=None,
        username_for_role_validation: str | None = None,
    ):
        from utils.filter_event_card_validation import validate_all_visible_cards

        self.logger.info(
            "verify_visible_cards_match_applied_filters | categories=%s",
            list((filters or {}).keys()),
        )
        if start_date_str or end_date_str:
            self.logger.info(
                "verify_visible_cards_match_applied_filters | custom_dates start=%r end=%r",
                start_date_str,
                end_date_str,
            )
        if username_for_role_validation:
            self.logger.info(
                "verify_visible_cards_match_applied_filters | role_fallback username=%r",
                username_for_role_validation,
            )

        self.logger.debug("Collecting semantic event_card| elements from current screen")
        parsed = self.get_parsed_semantic_event_cards()
        self.logger.info(
            "verify_visible_cards_match_applied_filters | parsed_semantic_cards=%d",
            len(parsed),
        )

        role_fallback = None
        if username_for_role_validation:
            role_fallback = lambda card, allowed: self.verify_role_from_course_details(
                card.get("code", ""), allowed, username_for_role_validation
            )

        validate_all_visible_cards(
            parsed,
            filters or {},
            start_date_str,
            end_date_str,
            allow_empty=allow_empty,
            reference_date=reference_date,
            role_fallback_validator=role_fallback,
            caller_logger=self.logger,
        )

    def open_event_card_by_code(self, event_code: str) -> bool:
        try:
            loc = self.build_locator(self.locator["event_card_by_code"], event_code)
            if not self.is_displayed(loc, timeout=5):
                return False
            self.click_element(loc)
            return True
        except Exception:
            return False

    def verify_role_from_course_details(self, event_code: str, expected_roles: set[str], username: str) -> bool:
        """
        Fallback check for role label ambiguity on card:
        open card -> course details -> assert username under expected role section.
        """
        self.logger.info(
            "role_fallback | event_code=%r expected_roles=%s username=%r",
            event_code,
            sorted(expected_roles),
            username,
        )
        opened = self.open_event_card_by_code(event_code)
        if not opened:
            self.logger.warning("role_fallback | could not open event card for code=%r", event_code)
            return False
        try:
            self.course_detils_page.click_course_details()
            expected = {r.lower() for r in expected_roles}
            if "teacher" in expected and self.course_detils_page.is_user_present_in_teachers(username):
                self.logger.info("role_fallback | matched teacher section for %r", username)
                return True
            if "organizer" in expected and self.course_detils_page.is_user_present_in_organizers(username):
                self.logger.info("role_fallback | matched organizer section for %r", username)
                return True
            self.logger.warning(
                "role_fallback | no teacher/organizer match for %r on event %r",
                username,
                event_code,
            )
            return False
        finally:
            self.driver.back()
            self.driver.back()


            
