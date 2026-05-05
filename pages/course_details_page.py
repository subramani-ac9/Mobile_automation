import time, logging
from constants.locator.course_details_locator import CourseDetailsLocator
from pages.base_page import BasePage
from utils.time_zone_util import TimezoneFormatter


class CourseDetailsPage(BasePage):
    """
    Page object for the Course Details screen.

    ── XML content-desc structure ────────────────────────────────────────────

    HEADER (always visible, single-value fields):
        content-desc="Art of Living Part 1"          ← course name
        content-desc="In-Person"                     ← mode
        content-desc="Max Capacity : 28"             ← capacity
        content-desc="Happiness Way, San Jose, ..."  ← address (in-person only)
        content-desc="Apr 19, 2026 • 11:16 AM to 11:17 AM • IST"   ← date+time row
        content-desc="Apr 20, 2026 • 11:16 AM to 11:17 AM • IST"
        content-desc="View all (3)"  ← optional; tap to reveal all dates

    BODY (after tapping "Course Details" / scrollable section):
        Multi-value fields use  "<Label>\n<val1>\n<val2>\n..."  e.g.
            content-desc="Teacher\nAuto Test45\nNivedha S"
            content-desc="Organizer\nNivedha S"
            content-desc="Contact Person\nNivedha S"
        Single-value fields:
            content-desc="Status\nActive"
            content-desc="Visibility\nPublic"
            content-desc="Short URL\nhttps://tinyurl.com/23w6z222"
            content-desc="AOL Center\nNew Jersey"

    ── Helper methods ────────────────────────────────────────────────────────
        _parse_field_values(label)  →  list[str]   (all values after the label)
        _get_field_value(label)     →  str          (first value after the label)
    """

    # ── Field label constants ──────────────────────────────────────────────
    _LABEL_STATUS         = "Status"
    _LABEL_VISIBILITY     = "Visibility"
    _LABEL_SHORT_URL      = "Short URL"
    _LABEL_AOL_CENTER     = "AOL Center"
    _LABEL_TEACHER        = "Teacher"
    _LABEL_ORGANIZER      = "Organizer"
    _LABEL_CONTACT_PERSON = "Contact Person"

    def __init__(self, driver, platform: str):
        super().__init__(driver, platform)
        self.locator = CourseDetailsLocator.get_locators(platform)
        self.logger  = logging.getLogger(__name__)

    # ======================================================================
    #  Private helpers
    # ======================================================================

    def _parse_field_values(self, label: str, scroll: bool = True) -> list[str]:
        """
        Locate the view whose content-desc starts with  "<label>\n"  and
        return every value that follows as a list of stripped strings.

        e.g.  "Teacher\nAuto Test45\nNivedha S"
              → ["Auto Test45", "Nivedha S"]

        Locator key  "field_by_label_prefix"  must accept  label + "\\n"
        as a format argument and match on content-desc starts-with.

        Example XPath (Android):
            //*[starts-with(@content-desc, '{0}')]
        """
        loc = self.build_locator(self.locator["field_by_label_prefix"], label + "\n")
        if scroll:
            self.scroll_to_element(self.locator["scroll"], loc)
        raw    = self.get_txt_from_attr(loc).strip()   # full content-desc string
        parts  = raw.split("\n")                        # ["Label", "val1", "val2", ...]
        values = [v.strip() for v in parts[1:] if v.strip()]
        return values

    def _get_field_value(self, label: str, scroll: bool = True) -> str:
        """Return the first (or only) value for a label\\nvalue field."""
        values = self._parse_field_values(label, scroll=scroll)
        return values[0] if values else ""

    # ======================================================================
    #  Header verification
    # ======================================================================

    def is_course_name_displayed(self, event_name: str) -> bool:
        try:
            loc = self.build_locator(self.locator["event_name"], event_name)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception verifying course name '{event_name}': {e}")
            raise Exception(f"Course name '{event_name}' is not present!")

    def is_course_mode_header_displayed(self, mode: str) -> bool:
        """Header shows plain mode string, e.g. content-desc="In-Person"."""
        try:
            loc = self.build_locator(self.locator["event_mode"], mode)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception verifying course mode header '{mode}': {e}")
            raise Exception(f"Mode '{mode}' is not present on the header")

    def is_start_date_header_displayed(self, start_date: str) -> bool:
        """
        Header date rows look like:
            "Apr 19, 2026 • 11:16 AM to 11:17 AM • IST"
        A plain date string ("Apr 19, 2026") is matched as a substring.
        """
        try:
            loc = self.build_locator(self.locator["start_date"], start_date)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception verifying start-date header '{start_date}': {e}")
            raise Exception(f"Start Date '{start_date}' is not present on the header")

    def is_start_time_header_displayed(self, start_time: str) -> bool:
        """
        start_time should be the time portion, e.g. "11:16 AM".
        The locator matches rows whose content-desc contains it.
        """
        try:
            loc = self.build_locator(self.locator["start_time"], start_time)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception verifying start-time header '{start_time}': {e}")
            raise Exception(f"Start Time '{start_time}' is not present on the header")

    def check_course_header(self, ev_name: str, ev_mode: str,
                             st_date: str, st_time: str) -> bool:
        self.logger.info(
            f"Checking course header — name={ev_name}, mode={ev_mode}, "
            f"start_date={st_date}, start_time={st_time}"
        )
        event_name     = self.is_course_name_displayed(ev_name)
        event_mode_hdr = self.is_course_mode_header_displayed(ev_mode)
        start_date_hdr = self.is_start_date_header_displayed(st_date)
        start_time_hdr = self.is_start_time_header_displayed(st_time)
        self.logger.info(
            f"\nCourse Header verification\n"
            f"  CourseName : {event_name}\n"
            f"  CourseMode : {event_mode_hdr}\n"
            f"  StartDate  : {start_date_hdr}\n"
            f"  StartTime  : {start_time_hdr}"
        )
        return event_name and event_mode_hdr and start_date_hdr and start_time_hdr

    # ======================================================================
    #  "View all" date expansion
    # ======================================================================

    def _expand_dates_if_needed(self) -> None:
        """
        If a  "View all (N)"  button is visible in the header section, tap it
        so that all individual date rows are rendered in the DOM before we
        try to read or verify them.

        Locator key  "view_all_dates"  should target the node whose
        content-desc starts with "View all".
        """
        try:
            view_all_loc = self.locator.get("view_all_dates")
            if view_all_loc and self.is_displayed(view_all_loc, timeout=3):
                self.logger.info("'View all' dates button found — tapping to expand all dates")
                self.click_element(view_all_loc)
                time.sleep(1)   # allow DOM to settle after expansion
            else:
                self.logger.info("'View all' dates button not present — all dates already visible")
        except Exception as e:
            # Non-fatal: log and continue if the button is absent
            self.logger.warning(f"Could not tap 'View all' dates button: {e}")

    def get_all_header_dates(self) -> list[str]:
        """
        Collect every date row from the header section.

        Each row has a content-desc like:
            "Apr 19, 2026 • 11:16 AM to 11:17 AM • IST"

        Steps:
          1. Tap "View all (N)" if present so all rows are in the DOM.
          2. Gather every node matched by locator key "header_date_rows".
          3. Return their raw content-desc strings.

        Suggested locator for  "header_date_rows"  (XPath, Android):
            //*[contains(@content-desc, '•')]
        """
        self._expand_dates_if_needed()
        try:
            elements = self.find_elements(self.locator["header_date_rows"])
            rows     = [el.get_attribute("content-desc").strip() for el in elements]
            self.logger.info(f"Header date rows collected: {rows}")
            return rows
        except Exception as e:
            self.logger.error(f"Exception collecting header date rows: {e}")
            raise Exception("Unable to collect header date rows")

    # ======================================================================
    #  Body field navigation
    # ======================================================================

    def click_course_details(self) -> None:
        try:
            self.click_element(self.locator["course_details"])
        except Exception as e:
            self.logger.error(f"Exception clicking 'Course Details': {e}")
            raise Exception("Unable to click 'Course Details' label")

    # ======================================================================
    #  Status
    # ======================================================================

    def get_course_status(self) -> str:
        """Returns e.g. 'Active'."""
        return self._get_field_value(self._LABEL_STATUS)

    def is_course_status_displayed(self, status: str) -> bool:
        try:
            actual = self.get_course_status()
            match  = actual.lower() == status.lower()
            if not match:
                self.logger.info(f"Status mismatch — actual='{actual}', expected='{status}'")
            return match
        except Exception as e:
            self.logger.error(f"Exception verifying course status '{status}': {e}")
            raise Exception(f"Course Status '{status}' is not present")

    # ======================================================================
    #  Visibility
    # ======================================================================

    def get_course_visibility(self) -> str:
        """Returns 'Public' or 'Private'."""
        return self._get_field_value(self._LABEL_VISIBILITY)

    def is_course_visibility_displayed(self, is_private: bool) -> bool:
        expected = "Private" if is_private else "Public"
        try:
            actual = self.get_course_visibility()
            match  = actual.lower() == expected.lower()
            if not match:
                self.logger.info(f"Visibility mismatch — actual='{actual}', expected='{expected}'")
            return match
        except Exception as e:
            self.logger.error(f"Exception verifying visibility '{expected}': {e}")
            raise Exception(f"Course Visibility '{expected}' is not present")

    # ======================================================================
    #  Short URL
    # ======================================================================

    def get_short_url(self) -> str:
        return self._get_field_value(self._LABEL_SHORT_URL)

    def is_short_url_displayed(self) -> bool:
        try:
            url   = self.get_short_url()
            found = url.startswith("http")
            if not found:
                self.logger.info(f"Short URL does not start with 'http': '{url}'")
            return found
        except Exception as e:
            self.logger.error(f"Exception verifying Short URL: {e}")
            raise Exception("Short URL is not present!")

    # ======================================================================
    #  AOL Center
    # ======================================================================

    def get_aol_center(self) -> str:
        """Returns the full AOL center value, e.g. 'New Jersey'."""
        return self._get_field_value(self._LABEL_AOL_CENTER)

    def is_aol_center_displayed(self, center: str) -> bool:
        """
        Matches on the first word of the center name, consistent with the
        original  data['aol_center'].split()[0]  behaviour.
        """
        try:
            actual = self.get_aol_center()
            match  = actual.lower().startswith(center.lower())
            if not match:
                self.logger.info(f"AOL Center mismatch — actual='{actual}', expected prefix='{center}'")
            return match
        except Exception as e:
            self.logger.error(f"Exception verifying AOL Center '{center}': {e}")
            raise Exception(f"AOL Center '{center}' is not present")

    # ======================================================================
    #  Teachers  (multi-value:  "Teacher\nName1\nName2")
    # ======================================================================

    def get_teachers(self) -> list[str]:
        """
        Reads  "Teacher\nAuto Test45\nNivedha S"
        and returns  ["Auto Test45", "Nivedha S"].
        """
        return self._parse_field_values(self._LABEL_TEACHER)

    def is_teachers_displayed(self, expected_teachers: list[str]) -> bool:
        """
        Verifies that every name in expected_teachers is present in the
        Teacher field (order-independent, case-insensitive).
        """
        try:
            actual_teachers = self.get_teachers()
            self.logger.info(f"Teachers — actual={actual_teachers}, expected={expected_teachers}")
            actual_lower = [t.lower() for t in actual_teachers]
            for teacher in expected_teachers:
                if teacher.lower() not in actual_lower:
                    raise Exception(f"Teacher '{teacher}' not found in {actual_teachers}")
            return True
        except Exception as e:
            self.logger.error(f"Exception verifying teachers {expected_teachers}: {e}")
            raise Exception(str(e))

    def is_user_present_in_teachers(self, username: str) -> bool:
        try:
            return any(username.lower() in t.lower() for t in self.get_teachers())
        except Exception:
            return False

    # ======================================================================
    #  Organizers  (multi-value:  "Organizer\nName1\nName2")
    # ======================================================================

    def get_organizers(self) -> list[str]:
        """
        Reads  "Organizer\nNivedha S\nSecond Name"
        and returns  ["Nivedha S", "Second Name"].
        """
        return self._parse_field_values(self._LABEL_ORGANIZER)

    def is_organizer_displayed(self, organizer: str) -> bool:
        try:
            actual_organizers = self.get_organizers()
            self.logger.info(f"Organizers — actual={actual_organizers}, expected='{organizer}'")
            match = any(organizer.lower() == o.lower() for o in actual_organizers)
            if not match:
                self.logger.info(f"Organizer '{organizer}' not found in {actual_organizers}")
            return match
        except Exception as e:
            self.logger.error(f"Exception verifying organizer '{organizer}': {e}")
            raise Exception(f"Organizer '{organizer}' is not present")

    def is_user_present_in_organizers(self, username: str) -> bool:
        self.logger.info("Checking if user is present in organizers")
        try:
            actual = self.get_organizers()
            self.logger.info(f"Organizers: {actual}, looking for: '{username}'")
            return any(username.lower() in o.lower() for o in actual)
        except Exception:
            return False

    # ======================================================================
    #  Contact Persons  (multi-value:  "Contact Person\nName1\nName2")
    # ======================================================================

    def get_contact_persons(self) -> list[str]:
        """
        Reads  "Contact Person\nNivedha S\nSecond Contact"
        and returns  ["Nivedha S", "Second Contact"].
        """
        return self._parse_field_values(self._LABEL_CONTACT_PERSON)

    def is_contact_displayed(self, contact: str) -> bool:
        try:
            actual_contacts = self.get_contact_persons()
            self.logger.info(f"Contacts — actual={actual_contacts}, expected='{contact}'")
            match = any(contact.lower() == c.lower() for c in actual_contacts)
            if not match:
                self.logger.info(f"Contact '{contact}' not found in {actual_contacts}")
            return match
        except Exception as e:
            self.logger.error(f"Exception verifying contact '{contact}': {e}")
            raise Exception(f"Contact '{contact}' is not present")

    # ======================================================================
    #  Course Mode (body section)
    # ======================================================================

    def is_course_mode_displayed(self, mode: str) -> bool:
        try:
            loc = self.build_locator(self.locator["event_mode2"], mode)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception verifying course mode '{mode}': {e}")
            raise Exception(f"Course Mode '{mode}' is not present")

    # ======================================================================
    #  Max Attendees
    # ======================================================================

    def is_max_attendees_displayed(self, value) -> bool:
        try:
            loc = self.build_locator(self.locator["max_attendees"], value)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(f"Exception verifying max attendees '{value}': {e}")
            raise Exception(f"MaxAttendees '{value}' value is not present")

    # ======================================================================
    #  Dates  (header rows — expand "View all" when needed)
    # ======================================================================

    def is_dates_displayed(self, expected_dates: list[str]) -> bool:
        """
        Expands "View all" if present, then checks that every expected date
        string appears as a substring in at least one header date row.

        Header rows look like  "Apr 19, 2026 • 11:16 AM to 11:17 AM • IST",
        so passing "Apr 19, 2026" is sufficient.
        """
        try:
            all_rows = self.get_all_header_dates()
            for date in expected_dates:
                if not any(date in row for row in all_rows):
                    self.logger.info(f"Date '{date}' not found in rows: {all_rows}")
                    raise Exception(f"Date '{date}' is not present in header date rows")
            return True
        except Exception as e:
            self.logger.error(f"Exception verifying dates {expected_dates}: {e}")
            raise Exception(str(e))

    # ======================================================================
    #  Times  (same header rows as dates)
    # ======================================================================

    def is_times_displayed(self, expected_times: list[str]) -> bool:
        """
        Reuses the already-expanded header date rows.
        Each expected_time is matched as a substring, e.g.
            "11:16 AM to 11:17 AM"  in  "Apr 19, 2026 • 11:16 AM to 11:17 AM • IST"
        """
        try:
            all_rows = self.get_all_header_dates()
            for t in expected_times:
                if not any(t in row for row in all_rows):
                    self.logger.info(f"Time '{t}' not found in rows: {all_rows}")
                    raise Exception(f"Time '{t}' is not present in header date rows")
            return True
        except Exception as e:
            self.logger.error(f"Exception verifying times {expected_times}: {e}")
            raise Exception(str(e))

    # ======================================================================
    #  Location
    # ======================================================================

    def is_location_details_displayed(self, street: str, city: str,
                                       zipcode, state: str) -> bool:
        try:
            loc = self.build_locator(self.locator["location"], street, city, state, zipcode)
            self.logger.info(f"Prepared location locator: {loc}")
            self.scroll_to_element(self.locator["scroll"], loc)
            return self.is_displayed(loc)
        except Exception as e:
            self.logger.error(
                f"Exception verifying location — street={street}, city={city}, "
                f"zipcode={zipcode}, state={state}: {e}"
            )
            raise Exception("Location Details not present")

    # ======================================================================
    #  Top-level orchestration
    # ======================================================================

    def verify_course_details(self, data: dict) -> tuple[bool, str]:
        """
        Full end-to-end verification of the Course Details screen.

        Flow
        ----
        1. Check header (course name, mode, first date, first start time).
        2. Expand "View all" if present, then verify all dates & times against
           the converted timezone values.
        3. Tap "Course Details" to open the body section.
        4. Verify body fields: mode, capacity, visibility, teachers (multi),
           organizer (multi), contact (multi), location (in-person only),
           AOL center.

        Returns (True, "") on full pass, or (False, reason) on any failure.
        """
        time_details = self._get_converted_time_details(data)

        try:
            # ── 1. Header ─────────────────────────────────────────────────
            header_ok = self.check_course_header(
                data["product_name"],
                data["event_mode"].capitalize(),
                time_details[0][0],                      # first date string
                time_details[0][1].split(" - ")[0],      # first start time
            )
            if not header_ok:
                return False, "Course Header check failed!"

            # ── 2. Dates & times (View all expansion handled internally) ──
            dates, times = [], []
            dates = data["dates"]
            start_times = data["start_times"]
            end_times = data["end_times"]
            for i in range(int(data["no_of_dates"])):
                dates.append(time_details[i][0])
                times.append(time_details[i][1])
            start_date = self.is_dates_displayed(dates)
            start_time = self.is_times_displayed(times)

            # ── 3. Open body section ──────────────────────────────────────
            self.click_course_details()
            time.sleep(2)

            # ── 4. Body fields ────────────────────────────────────────────
            event_mode2   = self.is_course_mode_displayed(data["event_mode"].title())
            max_attendees = self.is_max_attendees_displayed(int(float(data["max_attendees"])))
            is_private    = self.is_course_visibility_displayed(
                data["is_private"].lower() == "true"
            )

            # Teachers — multi-value field
            teachers_list = [
                data[f"teacher{i}"] for i in range(1, int(data["max_teachers"]) + 1)
            ]
            teachers  = self.is_teachers_displayed(teachers_list)

            # Organizer — multi-value field
            organizer = self.is_organizer_displayed(data["organizer"])

            # Contact person — multi-value field (skip verification if empty)
            contact = (
                True if not data.get("contact_person")
                else self.is_contact_displayed(data["contact_person"])
            )

            # Location — only verified for in-person events
            location = True
            if data["event_mode"].lower() == "in-person":
                location = self.is_location_details_displayed(
                    data["address"],
                    data["city"],
                    int(float(data["zipcode"])),
                    data["state"].split("(")[-1].strip(")"),
                )

            # AOL Center
            center = self.is_aol_center_displayed(data["aol_center"].split()[0])

            details_ok = (
                event_mode2 and max_attendees and is_private
                and teachers and organizer and contact
                and start_date and start_time
                and location and center
            )

            self.logger.info(
                f"\nCourse Body Verification\n"
                f"  courseMode   : {event_mode2}\n"
                f"  maxAttendees : {max_attendees}\n"
                f"  is_private   : {is_private}\n"
                f"  teachers     : {teachers}\n"
                f"  organizer    : {organizer}\n"
                f"  contact      : {contact}\n"
                f"  startDate    : {start_date}\n"
                f"  timeRange    : {start_time}\n"
                f"  {'location' if data['event_mode'].lower() == 'in-person' else 'noLocation'}"
                f"           : {location}\n"
                f"  center       : {center}"
            )

            if not details_ok:
                return False, "Course verification failed due to details mismatch!"
            return True, ""

        except Exception as e:
            self.logger.error(f"Exception raised while verifying course details: {e}")
            return False, f"Course verification failed: {e}"

    # ======================================================================
    #  Private utility
    # ======================================================================

    def _get_converted_time_details(self, data: dict):
        """Convert raw date/time entries in data to the target timezone."""
        try:
            dates, times = [], []
            no_dates = int(data["no_of_dates"])
            for i in range(1, no_dates + 1):
                dates.append(data[f"date{i}"])
                times.append((data[f"start_time{i}"], data[f"end_time{i}"]))
            return TimezoneFormatter.convert_times_details_to_target_timezone(
                dates, times, data["timezone"]
            )
        except Exception as e:
            self.logger.error(f"Exception converting times to target timezone: {e}")
            raise Exception("Unable to convert the given time to target timezone")


# import time, logging
# from constants.locator.course_details_locator import CourseDetailsLocator
# from pages.base_page import BasePage
# from utils.time_zone_util import TimezoneFormatter

# class CourseDetailsPage(BasePage):

#     def __init__(self, driver, platform: str):
#         super().__init__(driver, platform)
#         self.locator = CourseDetailsLocator.get_locators(platform)
#         self.logger = logging.getLogger(__name__)
    
#     def is_course_name_displayed(self, event_name):
#         try:
#             loc = self.build_locator(self.locator["event_name"], event_name)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the Course name:: {event_name}, Exception:: {str(e)}')
#             raise Exception(f"Product:: {event_name} is not present!")
    
#     def is_course_mode_header_displayed(self, mode):
#         try:
#             loc = self.build_locator(self.locator["event_mode"], mode)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the Course Mode header:: {mode}, Exception:: {str(e)}')
#             raise Exception(f'Mode ::{mode} is not present on the header')
        
#     def is_start_date_header_displayed(self, start_date):
#         try:
#             loc = self.build_locator(self.locator["start_date"], start_date)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the Course StartDate header:: {start_date}, Exception:: {str(e)}')
#             raise Exception(f'Start Date:: {start_date} is not present on the header')
        
#     def is_start_time_header_displayed(self, start_time):
#         try:
#             loc = self.build_locator(self.locator["start_time"], start_time)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the Course StartTime header:: {start_time}, Exception:: {str(e)}')
#             raise Exception(f'Start Time:: {start_time} is not present on the header')

#     def click_course_details(self):
#         try:
#             self.click_element(self.locator["course_details"])
#         except Exception as e:
#             self.logger.error(f"Exception raised while clicking the 'Course Details' label, Exception:: {str(e)}")
#             raise Exception(f'Unable to click "Course Details" label')
        
#     def is_course_mode_displayed(self, mode):
#         try:
#             loc = self.build_locator(self.locator["event_mode2"], mode)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the Course Mode:: {mode}, Exception:: {str(e)}')
#             raise Exception(f'Course Mode:: {mode} is not present')
        
#     def is_max_attendees_displayed(self, value):
#         try:
#             loc = self.build_locator(self.locator["max_attendees"], value)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the MaxAteendees:: {value}, Exception:: {str(e)}')
#             raise Exception(f'MaxAttendees:: {value} value is not present')
        
#     def is_course_status_displayed(self, status):
#         try:
#             loc = self.build_locator(self.locator["event_status"], status)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the CourseStatus:: {status}, Exception:: {str(e)}')
#             raise Exception(f'Course Status:: {status} is not present')
        
#     def is_course_visibility_displayed(self, value):
#         val = 'Private' if value else 'Public'
#         try:
#             loc = self.build_locator(self.locator["event_visibility"], val)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the CourseVisibility:: {val}, Exception:: {str(e)}')
#             raise Exception(f'Course Visibility:: {val} is not present')
        
#     def is_short_url_displayed(self):
#         content = "Not Obtained Yet!"
#         try:
#             content = self.get_txt_from_attr(self.locator["short_url"])
#             return content.find('http')
#         except Exception as e:
#             self.logger.error(f"Exception raised while verifying the ShortURL:: {content}, Exception:: {str(e)}")
#             raise Exception(f"Short Url is not present!")
    
#     def is_teachers_displayed(self, teacehrs: list[str]):
#         try:
#             for index, teacher in enumerate(teacehrs):
#                 loc = self.build_locator(self.locator['ith_teacher'], str(index + 1))
#                 self.scroll_to_element(self.locator["scroll"], loc)
#                 content = self.get_txt_from_attr(loc).strip()
#                 if not content == teacher:
#                     self.logger.info(f"Actual:: {content} != {teacher} ::Expected")
#                     raise Exception(f"Teacher:: {teacher} is not present")
#             return True
#         except Exception as e:
#             self.logger.error(f"Exception raised while verifying the teachers:: {teacehrs}, Exception:: {str(e)}")
#             raise Exception(str(e))


#     def is_organizer_displayed(self, organizer):
#         try:    
#             loc = self.build_locator(self.locator["ith_organizer"], "1")
#             self.scroll_to_element(self.locator["scroll"], loc)
#             content = self.get_txt_from_attr(loc).strip()
#             return content == organizer
#         except Exception as e:
#             self.logger.error(f"Exception raised while verifying the organizer:: {organizer}, Exception:: {str(e)}")
#             raise Exception(f"Organizer:: {organizer} is not present")

#     def is_user_present_in_teachers(self, username: str, max_scan: int = 8) -> bool:
#         try:
#             for index in range(1, max_scan + 1):
#                 loc = self.build_locator(self.locator['teachers'], username)
#                 if not self.is_displayed(loc, timeout=2):
#                     break
#                 content = self.get_txt_from_attr(loc).strip()
#                 if content and username.lower() in content.lower():
#                     return True
#             return False
#         except Exception:
#             return False

#     def is_user_present_in_organizers(self, username: str, max_scan: int = 8) -> bool:
#         print("chevk user is present in organizers")
#         try:
#             for index in range(1, max_scan + 1):
#                 loc = self.build_locator(self.locator['organizers'], username)
#                 if not self.is_displayed(loc, timeout=2):
#                     print("username is not displayed in is_user_present_in_organizers:", loc)
#                     break
#                 content = self.get_txt_from_attr(loc).strip()
#                 print("content in is_user_present_in_organizers:", content)
#                 print("username in is_user_present_in_organizers:", username)
#                 if content and username.lower() in content.lower():
#                     return True
#             return False
#         except Exception:
#             return False
        
#     def is_contact_displayed(self, contact):
#         try:
#             loc = self.build_locator(self.locator["ith_contact"], "1")
#             self.scroll_to_element(self.locator["scroll"], loc)
#             content = self.get_txt_from_attr(loc).strip()
#             return content == contact
#         except Exception as e:
#             self.logger.error(f"Exception raised while verifying the contact:: {contact}, Exception:: {str(e)}")
#             raise Exception(f'Contact:: {contact} is not present')
        
#     def is_dates_displayed(self, dates):
#         try:
#             for index, date in enumerate(dates):
#                 loc = self.build_locator(self.locator['date'], date)
#                 self.scroll_to_element(self.locator["scroll"], loc)
#                 content = self.get_txt_from_attr(loc).strip()
#                 if not content == date:
#                     self.logger.info(f"Actual--> {content} != {date} <--Expected")
#                     raise Exception(f"Date:: {date} is not present")
#             return True
#         except Exception as e:
#             self.logger.error(f"Exception raised while verifying the dates:: {dates}, Exception:: {str(e)}")
#             raise Exception(str(e))
        
#     def is_times_displayed(self, times):
#         try:
#             for index, time in enumerate(times):
#                 loc = self.build_locator(self.locator['ith_time'], index)
#                 self.scroll_to_element(self.locator["scroll"], loc)
#                 content = self.get_txt_from_attr(loc).strip()
#                 if not content == time:
#                     self.logger.info(f"Actual--> {content} != {time} <--Expected")
#                     raise Exception(f"Time:: {time} is not present")
#             return True
#         except Exception as e:
#             self.logger.error(f"Exception raised while verifying the times:: {times}, Exception:: {str(e)}")
#             raise Exception(str(e))
    
#     def is_location_details_displayed(self, street, city, zipcode, state):
#         try:
#             loc = self.build_locator(self.locator["location"], street, city, state, zipcode)
#             self.logger.info(f"Prepared Location locator:: {loc}")
#             self.scroll_to_element(self.locator["scroll"], loc)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f"Exception raised while verifying the LocationDetails:: Street:: {street}, City:: {city}, ZipCode:: {zipcode}, State:: {state}. Exception:: {str(e)}")
#             raise Exception(f"Location Details not present")
        
#     def is_aol_center_displayed(self, center):
#         try:
#             loc = self.build_locator(self.locator["aol_center"], center)
#             self.scroll_to_element(self.locator["scroll"], loc)
#             return self.is_displayed(loc)
#         except Exception as e:
#             self.logger.error(f"Exception rasied while verifying the AOLCenter:: {center}, Exception:: {str(e)}")
#             raise Exception(f"AOL Center:: {center} is not present")

#     def check_course_header(self, ev_name, ev_mode, st_date, st_time):
#         self.logger.info(f"Course Header info. : course_name:: {ev_name}, course_mode:: {ev_mode}, start_date:: {st_date}, start_time:: {st_time}")
#         event_name = self.is_course_name_displayed(ev_name)
#         event_mode1 = self.is_course_mode_header_displayed(ev_mode)
#         event_start_date1 = self.is_start_date_header_displayed(st_date)
#         event_start_time1 = self.is_start_time_header_displayed(st_time)
#         self.logger.info(
#             f"\nCourse Header verification,\n"
#             f"CourseName       :: {event_name},\n"
#             f"CourseMode       :: {event_mode1},\n"
#             f"Course StartDate :: {event_start_date1},\n"
#             f"Course StartTime :: {event_start_time1} \n"
#         )
#         return (event_name and event_mode1 and event_start_date1 and event_start_time1)
        
#     def verify_course_details(self, data):  # need to check event status, short url
#         screen_content = None
#         time_details = self.__get_converted_converted_time_details(data)
#         try:
#             header_check = self.check_course_header(data['product_name'], data['event_mode'].capitalize(), time_details[0][0], time_details[0][1].split(" - ")[0])
#             if not header_check: 
#                 return header_check,f"Course Header check failed!, course_name:: {event_name}, course_mode:: {event_mode1}, event_start_date:: {event_start_date1}, event_start_time:: {event_start_time1}"
#             self.click_course_details()
#             event_mode2 = self.is_course_mode_displayed(data['event_mode'].title())
#             max_attendees = self.is_max_attendees_displayed(int(float(data['max_attendees'])))
#             is_private = self.is_course_visibility_displayed(data['is_private'].lower() == 'true')
#             time.sleep(10)
#             teachers = []
#             for i in range(1, int(data["max_teachers"]) + 1):
#                 teachers.append(data[f'teacher{i}'])
#             teachers = self.is_teachers_displayed(teachers)

#             organizer = self.is_organizer_displayed(data['organizer'])
#             contact = False if data['contact_person'] else True
#             contact = self.is_contact_displayed(data['contact_person'])
#             dates, times = [], []
#             self.logger.info(f"Time Details:: {time_details}")
#             for i in range(0, int(data['no_of_dates'])): 
#                 dates.append(time_details[i][0])
#                 times.append(time_details[i][1])
#             start_date = self.is_dates_displayed(dates)
#             start_time = self.is_times_displayed(times)
#             location = False if data['event_mode'].lower() == 'in-person' else True
#             if data['event_mode'].lower() == 'in-person':
#                 location = self.is_location_details_displayed(data['address'], data['city'], int(float(data['zipcode'])), data['state'].split('(')[-1].strip(')'))
#             center = self.is_aol_center_displayed(data['aol_center'].split()[0])
#             details_check = (
#                 event_mode2 and max_attendees and is_private and teachers and 
#                 organizer and contact 
#                 and start_time and start_date and location and center
#                 )
#             self.logger.info(
#                 f"\Course Body Verification,\n"
#                 f"courseMode    :: {event_mode2}\n"
#                 f"maxAttendees :: {max_attendees}\n"
#                 f"is_private   :: {is_private}\n"
#                 f"teachers     :: {teachers}\n"
#                 f"organizer    :: {organizer}\n"
#                 f"contact      :: {contact}\n"
#                 f"startDate    :: {start_date}\n"
#                 f"TimeRange    :: {start_time}\n"
#                 f"{'Locations' if data['event_mode'].lower() == 'in-person' else 'NoLocation'}  :: {location}\n"
#                 f"center       :: {center}\n"
#             )
#             if not details_check:
#                 return details_check, ("Course verification failed due to details mismatch!")
#             return details_check, ""
#         except Exception as e:
#             self.logger.error(f'Exception raised while verifying the course details, Exception:: {str(e)}')
#             return False, f'Course verification failed due to {str(e)}'
        
#     def __get_converted_converted_time_details(self, data):
#         try:
#             dates, times =[], []
#             no_dates = int(data['no_of_dates'])
#             for i in range(1, no_dates + 1):
#                 dates.append(data[f'date{i}'])
#                 times.append((data[f'start_time{i}'], data[f'end_time{i}']))
#             timezone = data['timezone']
#             return TimezoneFormatter.convert_times_details_to_target_timezone(dates, times, timezone)
#         except Exception as e:
#             self.logger.error(f"Exception riased while converting the given time to target timezone, Exception:: {str(e)}")
#             raise Exception("Unable to convert the given time to target timezone")