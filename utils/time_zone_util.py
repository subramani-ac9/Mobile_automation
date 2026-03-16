import subprocess
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple
from zoneinfo import ZoneInfo
from config.config import TestConfig
import pytz
import logging

class TimezoneFormatter:
    # Mapping of abbreviations to pytz time zone names
    TZ_MAP = {
        "EST": "America/New_York",
        "CST": "America/Chicago",
        "MST": "America/Denver",
        "PST": "America/Los_Angeles",
        "HST": "Pacific/Honolulu",
        "IST": "Asia/Kolkata",
    }

    logger = logging.getLogger(__name__)

    @classmethod
    def _get_timezone(cls, label_with_abbreviation: str):
        try:
            cls.logger.debug(f"Parsing timezone from: {label_with_abbreviation}")
            abbreviation = label_with_abbreviation.split("-")[-1].strip().upper()
            tz_name = cls.TZ_MAP.get(abbreviation)
            if not tz_name:
                cls.logger.error(f"Unsupported timezone abbreviation: {abbreviation}")
                raise ValueError(f"Unsupported timezone abbreviation: {abbreviation}")
            cls.logger.debug(f"Mapped {abbreviation} to {tz_name}")
            return tz_name
        except Exception as e:
            cls.logger.error(f"Invalid timezone input format: {label_with_abbreviation}")
            raise ValueError(f"Invalid input format: {label_with_abbreviation}") from e

    @classmethod
    def get_the_current_date_for_given_timezone(cls, label_with_abbreviation: str) -> str:
        cls.logger.debug(f"Getting current date for timezone: {label_with_abbreviation}")
        timezone = cls._get_timezone(label_with_abbreviation)
        current_datetime = datetime.now(pytz.timezone(timezone))
        formatted_date = current_datetime.strftime("%m/%d/%Y")
        cls.logger.info(f"Current date in {label_with_abbreviation}: {formatted_date}")
        return formatted_date

    @classmethod
    def get_past_date_for_given_timezone(cls, label_with_abbreviation: str, years: int = 0, months: int = 0, days: int = 0) -> str:
        cls.logger.debug(f"Getting past date for timezone: {label_with_abbreviation} (years={years}, months={months}, days={days})")
        timezone = cls._get_timezone(label_with_abbreviation)
        current_datetime = datetime.now(pytz.timezone(timezone))
        past_datetime = current_datetime - relativedelta(years=years, months=months, days=days)
        formatted_date = past_datetime.strftime("%m/%d/%Y")
        cls.logger.info(f"Past date in {label_with_abbreviation}: {formatted_date}")
        return formatted_date

    @classmethod
    def get_the_current_time_for_given_timezone(cls, label_with_abbreviation: str) -> str:
        timezone = cls._get_timezone(label_with_abbreviation)
        current_datetime = datetime.now(pytz.timezone(timezone))
        return current_datetime.strftime("%I:%M %p")

    @classmethod
    def get_the_past_time_for_given_timezone(cls, label_with_abbreviation: str, hours: int=0, minutes: int = 0) -> str:
        timezone = cls._get_timezone(label_with_abbreviation)
        current_datetime = datetime.now(pytz.timezone(timezone))
        pastTime = current_datetime - timedelta(minutes=minutes, hours=hours)
        return pastTime.strftime("%I:%M %p")
    
    @classmethod
    def add_duration_to_time(cls, time_str: str, duration, unit) -> str:
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        if unit == 'minutes':
            new_time = time_obj + timedelta(minutes=duration)
        elif unit == 'hours':
            new_time = time_obj + timedelta(hours=duration)
        else:
            raise ValueError("Unit must be 'minutes' or 'hours'")
        
        return new_time.strftime("%-I:%M %p")


    # 4 xpath
    @classmethod
    def get_pretty_date_for_timezone(cls, label_with_abbreviation: str) -> str:
        tz = cls._get_timezone(label_with_abbreviation)
        tz_now = datetime.now(pytz.timezone(tz))
        local_now = datetime.now()

        is_today = tz_now.date() == local_now.date()

        day_number = tz_now.strftime("%d")  # "15"
        weekday = tz_now.strftime("%A")  # "Tuesday"
        full_date = tz_now.strftime("%B %d, %Y")  # "July 15, 2025"

        result = f"{int(day_number)}, {weekday}, {full_date}"
        if is_today:
            result += ", Today"

        return result

    @classmethod
    def convert_times_details_to_target_timezone(cls,
            date_strings: List[str],
            time_ranges: List[Tuple[str, str]],
            current_timezone: str,
            target_timezone: str = None,

    ) -> List[Tuple[str, str]]:
        result = []
        current_tz = cls._get_timezone(current_timezone)
        target_timezone = cls.get_target_system_timezone(target_timezone)
        target_tz = ZoneInfo(target_timezone)

        print(f"Extracted System Target Timezone:: {target_tz}")
        for date_str, (start_str, end_str) in zip(date_strings, time_ranges):

            start_dt = datetime.strptime(f"{date_str} {start_str}", "%m/%d/%Y %I:%M %p").replace(
                tzinfo=ZoneInfo(current_tz))
            end_dt = datetime.strptime(f"{date_str} {end_str}", "%m/%d/%Y %I:%M %p").replace(
                tzinfo=ZoneInfo(current_tz))

            start_converted = start_dt.astimezone(target_tz)
            end_converted = end_dt.astimezone(target_tz)

            pretty_date = start_converted.strftime("%b %-d, %Y")
            pretty_time = f"{start_converted.strftime('%-I:%M %p')} - {end_converted.strftime('%-I:%M %p')} {start_converted.tzname()}"

            result.append((pretty_date, pretty_time))

        return result

    @classmethod
    def get_target_system_timezone(cls, target_timezone=None):
        cls.logger.debug(f"Getting target system timezone (provided: {target_timezone})")
        if target_timezone:
            cls.logger.debug("Using provided timezone")
            return cls._get_timezone(target_timezone)
        else:
            try:
                platform = TestConfig.MOBILE_PLATFORM.lower()
                cls.logger.debug(f"Detecting system timezone for platform: {platform}")

                if platform == 'ios':
                    cls.logger.debug("Using ideviceinfo to get iOS timezone")
                    try:
                        result = subprocess.check_output(
                            ["ideviceinfo", "-q", "com.apple.mobile.iTunes", "-k", "TimeZone"]
                        ).decode("utf-8").strip()
                        if result:
                            cls.logger.info(f"iOS timezone detected: {result}")
                            return result
                        else:
                            cls.logger.warning("iOS timezone detection returned empty string, using fallback")
                    except Exception as idevice_error:
                        cls.logger.warning(f"ideviceinfo failed: {idevice_error}, using fallback")
                    
                    # Fallback to a default timezone if detection fails
                    cls.logger.info("Using fallback timezone: America/Los_Angeles")
                    return "America/Los_Angeles"
                elif platform == 'android':
                    cls.logger.debug("Using adb to get Android timezone")
                    try:
                        result = subprocess.check_output(
                            ["adb", "shell", "getprop", "persist.sys.timezone"]
                        ).decode("utf-8").strip()
                        if result:
                            cls.logger.info(f"Android timezone detected: {result}")
                            return result
                        else:
                            cls.logger.warning("Android timezone detection returned empty string, using fallback")
                    except Exception as adb_error:
                        cls.logger.warning(f"adb failed: {adb_error}, using fallback")
                    
                    # Fallback to a default timezone if detection fails
                    cls.logger.info("Using fallback timezone: America/Los_Angeles")
                    return "America/Los_Angeles"
                else:
                    cls.logger.error(f"Invalid platform: {TestConfig.MOBILE_PLATFORM}")
                    raise Exception(f"Invalid platform:: {TestConfig.MOBILE_PLATFORM}")
            except Exception as e:
                cls.logger.error(f"Error while fetching the system timezone: {str(e)}")
                cls.logger.info("Using fallback timezone: America/Los_Angeles")
                return "America/Los_Angeles"