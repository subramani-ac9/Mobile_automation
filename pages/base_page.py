import time
import re
import logging
from typing import Optional
from appium.webdriver.webdriver import WebDriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from config.config import TestConfig
from utils.logger_config import LoggerConfig


class BasePage:

    def __init__(self, driver: WebDriver, platform: str):
        self.driver = driver
        self.platform = platform
        self.timeout = 10  # Default timeout value
        self.wait = WebDriverWait(self.driver, self.timeout)
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)


    def get_locator(self,locators, key, value=None):
        by, locator = locators[key]

        if callable(locator):
            locator = locator(value)

        return by, locator

    def enter_search_field_value(self,locator, value):
        try:
            self.logger.info(f"Entering product: {value}")

            element = self.find_element(locator)
            element.click()
            self.clear_search_field(element)
            self.driver.execute_script("mobile: type", {"text": value})

            # Trigger search
            self.driver.press_keycode(66)

            self.logger.info(f"Successfully entered value in search field: {value}")

        except Exception as e:
            self.logger.error(f"Failed to enter value in search field {value}: {e}")
            raise Exception(f"Unable to enter value in search field as {value}")

    def get_all_event_cards(self,locator):
        return self.driver.find_elements(*locator)

    def parse_event_data(self, desc: str):
        """
        Example input:
        event_card|type=course|mode=online|status=open

        Output:
        {
            "type": "course",
            "mode": "online",
            "status": "open"
        }
        """
        data = {}
        parts = desc.split("|")

        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                data[key] = value

        return data
    
    def enterEventCode(self, event_code: str, searchButton : tuple = None, search_field: str = None):
        from pages.participant_transfer_page import ParticipantTransferPage
        transfer_page = ParticipantTransferPage(self.driver, self.platform)
        self.logger.info("clicking the serach icon")
        self.click_element(transfer_page.locator["search_button"])
        self.logger.info(f"Entering event code: {event_code}")
        self.click_element(transfer_page.locator["events_search_field"])
        self.enter_search_field_value(transfer_page.locator["events_search_field"], event_code)
        time.sleep(3)


    def click_event_row_containing(self, locator, code: str) -> None:
        loc = self.build_locator(locator, code)
        self.scroll_to_element_by_touch(loc, max_swipes=20)
        self.click_element(loc)

    def is_course_displayed(self,locator, event_code: str):
        self.logger.info(f"Checking if course is displayed on the UI")
        event_elements = self.get_all_event_cards(locator)
        if not event_elements:
            raise Exception("No event cards found")

        for el in event_elements:
            desc = el.get_attribute("content-desc")
            event_data = self.parse_event_data(desc)
            if event_data["code"] == event_code:
                self.logger.info(f"Course with event code {event_code} found on the UI")
                return event_data
        self.logger.error(f"Course with event code {event_code} not found on the UI")
        raise Exception(f"Course with event code {event_code} not found on the UI")

    def find_element(self, value: tuple, timeout: int = 10) -> WebElement:
        try:
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            return wait.until(
                EC.visibility_of_element_located(value))
        except Exception as e:
            self.logger.error(f"Element {value} not present on the UI. Exception: {e}")
            raise NoSuchElementException(f"Element {value} not present on the UI. Exception: {e}")

    def find_element_by_presence(self, value: tuple, timeout: int = 10) -> WebElement:
        """
        Find element by DOM presence only (not necessarily visible).
        Useful for Flutter/Appium where visibility checks can be flaky.
        """
        try:
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            return wait.until(EC.presence_of_element_located(value))
        except Exception as e:
            self.logger.error(
                f"Element {value} not present in DOM. Exception: {e}"
            )
            raise NoSuchElementException(
                f"Element {value} not present in DOM. Exception: {e}"
            )
    
    def find_elements(self, value: tuple, timeout: int = 10):
        try:
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            return wait.until(
                EC.visibility_of_any_elements_located(value))
        except Exception as e:
            return []

    def clear_search_field(self, element):
        element.click()
        # Select all text
        self.driver.press_keycode(29, 4096)  # CTRL + A
        # Delete selected text
        self.driver.press_keycode(67)        # DEL

    def is_displayed(self, value: WebElement | tuple, timeout: int = 10):
        try:
            # Use custom timeout if provided, otherwise use default wait
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            
            if isinstance(value, WebElement):
                return wait.until(
                    EC.visibility_of(value)
                ).is_displayed()
            else:
                return wait.until(
                    EC.visibility_of_element_located(value)
                ).is_displayed()
        except Exception as e:
            self.logger.debug(f"Element {value} not displayed on the UI. Exception: {e}")
            return False

    def wait_for_element_to_disappear(self, value: tuple, timeout: int = 10):
        """Wait for element to disappear from the UI"""
        try:
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            wait.until_not(
                EC.visibility_of_element_located(value)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_element_to_be_clickable(self, value: tuple, timeout: int = 10):
        """Wait for element to be clickable"""
        try:
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            return wait.until(
                EC.element_to_be_clickable(value)
            )
        except TimeoutException:
            return False

    def click_element(self, value: WebElement | tuple, timeout: int = 40) -> None:
        try:
            if isinstance(value, WebElement):
                # if self.is_element_clickable(value):
                value.click()
            else:
                # if self.is_element_clickable(value):
                self.find_element(value, timeout).click()
        except Exception as e:
            self.logger.error(f"Exception arisen when trying to click the element {value}. Exception {e}")
            raise

    def get_text(self, value: WebElement | tuple, timeout: int = 10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((value))
            )
            return element.text
        except Exception as e:
            self.logger.error(f"Unable to get text from locator {value}: {e}")
            raise

    def is_element_clickable(self, value: WebElement | tuple, timeout: int = 10):
        try:
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            return wait.until(
                EC.element_to_be_clickable(value)
            )
        except Exception as e:
            self.logger.warning(f"element:: {value} is not clickable!. Exception {e}")
            return False

    def send_keys(self, element: WebElement | tuple, message, is_necessary=True, timeout: int = 10) -> None:
        try:
            if isinstance(element, WebElement):
                element.clear()
                element.send_keys(message)
            else:
                ele = self.find_element(element, timeout)
                ele.clear()
                ele.send_keys(message)
            if self.platform == 'android' and is_necessary: self.driver.hide_keyboard()

        except Exception as e:
            self.logger.error(f"element:: {element} is not interactable to send keys!. Exception {e}")
            raise 

    def send_keys_without_enter(
        self, element: WebElement | tuple, message, timeout: int = 10
    ):
        """Send keys without adding newline character."""
        try:
            el = (
                element
                if isinstance(element, WebElement)
                else self.find_element(element, timeout)
            )
            try:
                el.clear()
            except Exception as ce:
                # Flutter / iOS often rejects clear(); typing still works.
                self.logger.debug(f"clear() skipped before send_keys: {ce}")
            el.send_keys(message)
            return True
        except Exception as e:
            self.logger.error(
                f"element:: {element} is not interactable to send keys!. Exception {e}"
            )
            return False

    def get_element_text(self, value: WebElement | tuple,timeout: int = 10):
        try:
            if isinstance(value, WebElement):
                return value.text
            else:
                return self.find_element(value, timeout).text
        except Exception as e:
            self.logger.error(f'Could not get the text from the element:: {value}. Exception {e}')
            return False

    def get_input_value(self, element_or_tuple: WebElement | tuple, timeout: int = 10) -> str:
        """Return the current value/text of an input field.

        - Android returns 'text' attribute
        - iOS returns 'value' attribute
        """
        try:
            element = (
                element_or_tuple
                if isinstance(element_or_tuple, WebElement)
                else self.find_element(element_or_tuple, timeout)
            )
            if self.platform == 'android':
                return element.get_attribute('text') or ''
            # Default to iOS/web value attribute
            return element.get_attribute('value') or ''
        except Exception as e:
            self.logger.error(f"Could not read input value from element {element_or_tuple}. Exception {e}")
            return False

    def __android_toggle_wifi(self, enable: bool) -> None:
        state = 'enable' if enable else 'disable'
        self.driver.execute_script('mobile: shell', {
            'command': 'svc',
            'args': ['wifi', state]
        })

    def __android_toggle_data(self, enable: bool) -> None:
        state = 'enable' if enable else 'disable'
        self.driver.execute_script('mobile: shell', {
            'command': 'svc',
            'args': ['data', state]
        })

    def __android_set_airplane_mode(self, enable: bool) -> None:
        # Toggle airplane mode via settings + broadcast (works on emulators; may be blocked on some devices)
        value = '1' if enable else '0'
        self.driver.execute_script('mobile: shell', {
            'command': 'settings',
            'args': ['put', 'global', 'airplane_mode_on', value]
        })
        self.driver.execute_script('mobile: shell', {
            'command': 'am',
            'args': ['broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'true' if enable else 'false']
        })

    def go_offline(self) -> None:
        """Put the device offline. Designed for Android emulator/phones."""
        if self.platform != 'android':
            self.logger.warning('Offline toggling is only implemented for Android')
            return False
        try:
            self.__android_toggle_wifi(False)
            self.__android_toggle_data(False)
        except Exception:
            # Fallback to airplane mode
            try:
                self.__android_set_airplane_mode(True)
            except Exception as e:
                self.logger.error(f"Failed to toggle offline mode: {e}")
                return False
        time.sleep(1)

    def go_online(self) -> None:
        if self.platform != 'android':
            self.logger.warning('Online toggling is only implemented for Android')
        try:
            try:
                self.__android_set_airplane_mode(False)
            except Exception:
                # Ignore if not applicable
                pass
            self.__android_toggle_wifi(True)
            self.__android_toggle_data(True)
        except Exception as e:
            self.logger.error(f"Failed to toggle online mode: {e}")
            return False
        time.sleep(1)
    
    def get_txt_from_attr(self, element: WebElement | tuple, timeout: int = 10):
        try:
            if isinstance(element, WebElement):
                return element.get_attribute('content-desc') if(self.platform == 'android') else element.get_attribute('label')
            else:
                return self.find_element(element, timeout).get_attribute('content-desc') if(self.platform == 'android') else element.get_attribute('label')
        except Exception as e:
            raise Exception(f"Exception raised while trying to get the txt(attr) from the given element::{element}, exception:: {e}")

    def build_locator(self, path: tuple, *value) -> tuple:
        by_strategy, xpath_or_callable = path
        if callable(xpath_or_callable):
            return (by_strategy, xpath_or_callable(*value))
        return path

    def wait_for_page_load(self):
        """Wait for page to load completely"""
        try:
            # Wait for any loading indicators to disappear
            time.sleep(2)
            return True
        except Exception as e:
            self.logger.warning(f"Error waiting for page load: {e}")
            return False

    def scroll_to_element(self, scroll, targetEle, direction='down', ensure=False):
        can = True
        cmd = "mobile: scrollGesture" if self.platform == 'android' else "mobile: scroll"
        ele = None
        try:
            ele = self.wait.until(
                EC.presence_of_element_located(scroll)
            )
        except Exception as e:
            raise Exception(f"Elements {scroll} not present on the UI. Exception: {e}")
        while can:
            try:
                if self.is_displayed(targetEle):
                    if ensure:
                        self.__ensure_the_element_present_on_first_phase(targetEle)
                    return
            except:
                pass

            can = self.driver.execute_script(cmd, {
                # "elementId": self.find_element(scroll).id,
                'elementId': ele.id,
                'direction': direction,
                'percent': 0.5
            })
            try:
                if self.is_displayed(targetEle):
                    if ensure:
                        self.__ensure_the_element_present_on_first_phase(targetEle)
                    return
            except:
                pass
        self.logger.error(f"Exception while scrolling the element:: {targetEle}")
        return False

    def long_click_element(self, value: WebElement | tuple, duration_ms: int = 1500, timeout: int = 15) -> None:
        """Long-press on an element (participant transfer / context menus)."""
        el = value if isinstance(value, WebElement) else self.find_element(value, timeout)
        try:
            self.driver.execute_script(
                "mobile: longClickGesture",
                {"elementId": el.id, "duration": int(duration_ms)},
            )
            return
        except Exception as e:
            self.logger.debug(f"mobile: longClickGesture failed: {e}")
        try:
            self.driver.execute_script(
                "mobile: touchAndHold",
                {"elementId": el.id, "duration": int(duration_ms) / 1000.0},
            )
            return
        except Exception as e2:
            self.logger.debug(f"mobile: touchAndHold failed: {e2}")
        rect = el.rect
        cx = rect["x"] + rect["width"] // 2
        cy = rect["y"] + rect["height"] // 2
        actions = ActionChains(self.driver)
        actions.w3c_actions.pointer_action.move_to_location(cx, cy)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(float(duration_ms) / 1000.0)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.perform()

    def scroll_to_element_by_touch(self, target_ele: WebElement | tuple, direction: str = 'down', max_swipes: int = 15):
        """
        Scroll by touch (swipe gesture) until the target element is visible.
        Does not require a scroll container locator.
        direction: 'down' = reveal content below (swipe up), 'up' = reveal content above (swipe down).

        Stops early in the current direction when ``page_source`` is unchanged after a swipe
        (nothing new scrolled into view).
        """
        size = self.driver.get_window_size()
        width = size['width']
        height = size['height']
        center_x = width // 2
        if direction == 'down':
            start_y = int(height * 0.8)
            end_y = int(height * 0.2)
        else:
            start_y = int(height * 0.2)
            end_y = int(height * 0.8)
        prev_src: Optional[str] = None
        for _ in range(max_swipes):
            try:
                if self.is_displayed(target_ele, timeout=2):
                    return
            except Exception:
                pass
            self.drag_and_drop(center_x, start_y, center_x, end_y)
            time.sleep(0.2)
            src = self.driver.page_source
            if prev_src is not None and src == prev_src:
                self.logger.debug(
                    "scroll_to_element_by_touch: page unchanged after swipe, stopping (direction=%s)",
                    direction,
                )
                break
            prev_src = src
        self.logger.warning(f"Target element not visible after {max_swipes} touch scrolls: {target_ele}")

    def __ensure_the_element_present_on_first_phase(self, targetEle, timeout: int = 10, pause: Optional[float] = 0.1):
        element = self.find_element(targetEle, timeout)
        ele = element.rect
        screen_size = self.driver.get_window_size()
        actions = ActionChains(self.driver)
        start_y = (screen_size['height']//2)+(screen_size['height']//4)
        start_x = ele['x']
        end_y = screen_size['height']//4

        if start_y <= screen_size['height']//2:
            return
        
        # self.drag_and_drop(start_x, start_y, start_x, end_y)

        steps = 10  # Number of small moves to simulate slow drag
        delta_y = (end_y - start_y) // steps

        actions = ActionChains(self.driver)
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.click_and_hold()

        # Perform the slow drag with small moves and pause
        for step in range(1, steps + 1):
            intermediate_y = start_y + (delta_y * step)
            actions.w3c_actions.pointer_action.move_to_location(start_x, intermediate_y)
            actions.w3c_actions.pointer_action.pause(pause)  # Slow down the movement

        actions.w3c_actions.pointer_action.release()
        actions.perform()
    
    def scroll_on_the_element(self, element: WebElement | tuple, direction='down', percent=0.5, timeout: int = 10):
        ele = element
        cmd = "mobile: scrollGesture" if self.platform == 'android' else "mobile: scroll"
        if not isinstance(element, WebElement):
             ele = self.find_element(element, timeout)

        return self.driver.execute_script(cmd, {
            'elementId': ele.id,
            'direction': direction,
            'percent': percent
        })
            
    def drag_and_drop(self, start_x, start_y, end_x, end_y, steps: Optional[int] = 10, pause: Optional[float] = 0.1):
        delta_y = (end_y - start_y) // steps

        actions = ActionChains(self.driver)
        actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
        actions.w3c_actions.pointer_action.click_and_hold()

         # Perform the slow drag with small moves and pause
        for step in range(1, steps + 1):
            intermediate_y = start_y + (delta_y * step)
            actions.w3c_actions.pointer_action.move_to_location(end_x, intermediate_y)
            actions.w3c_actions.pointer_action.pause(pause)  # Slow down the movement

        actions.w3c_actions.pointer_action.release()
        actions.perform()

    
    def extract_page_contents(self):
        try:
            source = self.driver.page_source
            pattern = re.compile(r'(?:text|content-desc|label|name|value)="([^"]+)"')
            matches = pattern.findall(source)

            unique_texts = sorted(set(m.strip() for m in matches if m.strip()))
            return unique_texts

        except Exception as e:
            raise Exception(f"Could not extract text from page source: {e}") from e