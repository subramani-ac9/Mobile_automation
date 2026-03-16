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


    def find_element(self, value: tuple, timeout: int = 10) -> WebElement:
        try:
            wait = WebDriverWait(self.driver, timeout) if timeout != 10 else self.wait
            return wait.until(
                EC.visibility_of_element_located(value))
        except Exception as e:
            self.logger.error(f"Element {value} not present on the UI. Exception: {e}")
            raise NoSuchElementException(f"Element {value} not present on the UI. Exception: {e}")
    
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
                ele.send_keys(message+ '\n')
            if self.platform == 'android' and is_necessary: self.driver.hide_keyboard()

        except Exception as e:
            self.logger.error(f"element:: {element} is not interactable to send keys!. Exception {e}")
            raise 

    def send_keys_without_enter(self, element: WebElement | tuple, message):
        """Send keys without adding newline character"""
        try:
            if isinstance(element, WebElement):
                element.clear()
                element.send_keys(message)
            else:
                ele = self.find_element(element)
                ele.clear()
                ele.send_keys(message)
        except Exception as e:
            self.logger.error(f"element:: {element} is not interactable to send keys!. Exception {e}")
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

    def scroll_to_element_by_touch(self, target_ele: WebElement | tuple, direction: str = 'down', max_swipes: int = 15):
        """
        Scroll by touch (swipe gesture) until the target element is visible.
        Does not require a scroll container locator.
        direction: 'down' = reveal content below (swipe up), 'up' = reveal content above (swipe down).
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
        for _ in range(max_swipes):
            try:
                if self.is_displayed(target_ele, timeout=2):
                    return
            except Exception:
                pass
            self.drag_and_drop(center_x, start_y, center_x, end_y)
            time.sleep(0.3)
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