import json
import time
import pandas as pd
import allure
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from appium.webdriver.webdriver import WebDriver
from constants.locator.address_locator import AddressLocator
from constants.locator.course_create_locator import CourseCreateLocator
from constants.tenant_config import TenantConfig, TenantConfiguration
from pages.base_page import BasePage
from pages.course_create_page import CourseCreatePage
from pages.my_events_page import MyEventsPage
from utils.time_zone_util import TimezoneFormatter
from utils.helpers import take_screenshot
from utils.logger_config import LoggerConfig


# Form keys aligned with spreadsheet / handle_address (street is ``address``).
_ADDRESS_FORM_FIELD_KEYS = ("addressName", "address", "city", "zipcode")


class AddressPage(BasePage):
    """
    Page object for Course Creation page.
    
    Uses TenantConfig for all tenant-specific logic to ensure consistency
    and maintainability. All field labels and feature flags are centralized.
    """

    def __init__(self, driver: WebDriver, platform: str):
        super().__init__(driver, platform)
        self.locator = AddressLocator.get_locators(platform)
        from constants.message.address_message import AddressMessage
        self.course_create = CourseCreatePage(driver, platform)
        self.address_message = AddressMessage.get_message()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        
    def click_create_address_button(self):
        self.click_element(self.locator["create_address_button"])

    def scroll_to_state_and_click(self, state_name, max_swipes=10):
        for i in range(max_swipes):
            try:
                element = self.build_locator(self.locator["state_list"], state_name)
                print(f"Element: {element}")
                self.click_element(element,5)
                self.logger.info(f"State '{state_name}' selected")
                return True

            except:
                prev_source = self.driver.page_source

                # 👇 Scroll ONLY inside state list container
                self.driver.swipe(540, 2100, 540, 1500, 800)

                new_source = self.driver.page_source

                # ❌ No more scroll possible
                if prev_source == new_source:
                    raise Exception(f"State '{state_name}' not found after scrolling")

        raise Exception(f"State '{state_name}' not found after {max_swipes} swipes")


    def select_state(self, value):
        try:
            self.click_element(self.locator["state_dropdown"])
            time.sleep(2)

            # 👇 Direct scroll instead of search dependency
            self.scroll_to_state_and_click(value)

        except Exception as e:
            raise Exception(f"Unable to select state as {value}: {str(e)}")

    @staticmethod
    def _sheet_has_value(val: Any) -> bool:
        """True if spreadsheet cell should be applied (skip null / empty / 'null')."""
        if val is None:
            return False
        try:
            if pd.isna(val):
                return False
        except (TypeError, ValueError):
            pass
        s = str(val).strip()
        if not s or s.lower() in ("null", "none", "n/a", "-"):
            return False
        return True

    @staticmethod
    def _cell_to_str(val: Any) -> str:
        """Normalize sheet / numeric cell to comparable string."""
        if val is None:
            return ""
        try:
            if pd.isna(val):
                return ""
        except (TypeError, ValueError):
            pass
        if isinstance(val, float):
            if val.is_integer():
                return str(int(val))
            return str(val).strip()
        return str(val).strip()

    def read_address_form_snapshot(self, tenant: str) -> Dict[str, str]:
        """
        Read current address form into a dict for before/after verification.

        Keys: addressName, address (street), city, zipcode, state (US only when dropdown exists).
        """
        cc = self.course_create
        loc = cc.locator
        t = (tenant or "us").strip().lower()
        config = cc._get_tenant_config(t)
        snap: Dict[str, str] = {}

        def _read(locator_tuple: tuple, timeout: int = 8) -> str:
            raw = self.get_input_value(locator_tuple, timeout=timeout)
            if raw is False or raw is None:
                return ""
            return str(raw).strip()

        try:
            self.scroll_to_element_by_touch(loc["addressName_txt_field"], direction="down", max_swipes=8)
        except Exception:
            pass
        snap["addressName"] = _read(loc["addressName_txt_field"])
        try:
            self.scroll_to_element_by_touch(loc["Streest_Address_txt_field"], direction="down", max_swipes=8)
        except Exception:
            pass
        snap["address"] = _read(loc["Streest_Address_txt_field"])
        city_loc = cc.build_locator(loc["city_txt_field"], config.field_labels.city)
        try:
            self.scroll_to_element_by_touch(city_loc, direction="down", max_swipes=8)
        except Exception:
            pass
        snap["city"] = _read(city_loc)
        zip_loc = cc.build_locator(loc["zipcode_txt_field"], config.field_labels.zipcode)
        try:
            self.scroll_to_element_by_touch(zip_loc, direction="down", max_swipes=8)
        except Exception:
            pass
        snap["zipcode"] = _read(zip_loc)

        snap["state"] = ""
        if t == "us" and self.is_displayed(self.locator["state_dropdown"], timeout=3):
            try:
                el = self.find_element(self.locator["state_dropdown"], timeout=5)
                snap["state"] = (
                    el.get_attribute("content-desc") or el.get_attribute("text") or ""
                ).strip()
                if snap["state"] == "State Select Dropdown":
                    snap["state"] = ""
            except Exception:
                snap["state"] = ""
        return snap

    def apply_address_field_updates_from_row(self, row: dict, tenant: str) -> List[str]:
        """
        Enter only fields present with real values in ``row``; skip null / empty / 'null'.

        Returns list of keys actually applied (order matches handle_address).
        """
        t = (tenant or "us").strip().lower()
        applied: List[str] = []
        if self._sheet_has_value(row.get("addressName")):
            self.course_create.enter_addressName(self._cell_to_str(row["addressName"]))
            applied.append("addressName")
            self.logger.info("Updated addressName from spreadsheet")

        if self._sheet_has_value(row.get("zipcode")):
            self.course_create.enter_zipcode(self._cell_to_str(row["zipcode"]), t)
            applied.append("zipcode")
            self.logger.info("Updated zipcode from spreadsheet")

        if self._sheet_has_value(row.get("state")) and t == "us":
            self.select_state(self._cell_to_str(row["state"]))
            applied.append("state")
            self.logger.info("Updated state from spreadsheet")

        if self._sheet_has_value(row.get("city")):
            self.course_create.enter_city(self._cell_to_str(row["city"]), t)
            applied.append("city")
            self.logger.info("Updated city from spreadsheet")

        if self._sheet_has_value(row.get("address")):
            self.course_create.enter_address(self._cell_to_str(row["address"]))
            applied.append("address")
            self.logger.info("Updated street address from spreadsheet")

        return applied

    def _click_save_address_form(self) -> None:
        if self.is_displayed(self.locator["create_button"]):
            self.course_create.click_element(self.locator["create_button"])
            time.sleep(1.5)

    def _values_equivalent_for_assert(self, key: str, expected: str, actual: str) -> bool:
        e = (expected or "").strip()
        a = (actual or "").strip()
        if key == "zipcode":
            return self._cell_to_str(e) == self._cell_to_str(a)
        if key == "state":
            return e == a or (e and e in a) or (a and a in e)
        return e == a

    def _verify_after_partial_update(
        self,
        before: Dict[str, str],
        after: Dict[str, str],
        row: dict,
        modified_keys: Set[str],
    ) -> Tuple[bool, str]:
        """Ensure modified keys match spreadsheet and all other snapshot fields are unchanged."""
        errors: List[str] = []
        for k in _ADDRESS_FORM_FIELD_KEYS:
            # Selected US state is often not exposed reliably on the dropdown node; only assert when edited.
            if k == "state" and k not in modified_keys:
                continue
            if k in modified_keys:
                exp = self._cell_to_str(row.get(k))
                got = after.get(k, "")
                if not self._values_equivalent_for_assert(k, exp, got):
                    errors.append(f"{k}: expected {exp!r} after save, got {got!r}")
            else:
                b = before.get(k, "")
                a = after.get(k, "")
                if b != a:
                    errors.append(f"{k}: should be unchanged {b!r} -> {a!r}")
        if errors:
            return False, "; ".join(errors)
        return True, ""

    def handle_address(self, data):
        """Fill address form, submit, then validate success or extract validation errors from the page."""
        try:
            print(f"Data: {data}")
            if data.get("addressName"):
                self.course_create.enter_addressName(data.get("addressName"))
                self.logger.info(f"Entered address Name: {data.get('addressName')}")

            if data.get("zipcode"):
                self.course_create.enter_zipcode(data.get("zipcode"), data.get("tenant"))
                self.logger.info(f"Entered zipcode: {data.get('zipcode')}")

            if data.get("state") and data.get("tenant").lower() == "us":
                self.select_state(data.get("state"))
                self.logger.info(f"Entered state: {data.get('state')}")

            if data.get("city"):
                self.course_create.enter_city(data.get("city"), data.get("tenant"))
                self.logger.info(f"Entered city: {data.get('city')}")

            if data.get("address"):
                self.course_create.enter_address(data.get("address"))
                self.logger.info(f"Entered address: {data.get('address')}")

            if self.is_displayed(self.locator["create_button"]):
                self.course_create.click_element(self.locator["create_button"])
                # Allow snackbar / inline validation to appear in page source
                time.sleep(1.5)

            content = self.extract_page_contents()
            success = self._address_save_succeeded(content)
            msg = self._format_outcome_message(success, content)
            if not success:
                self.logger.warning("Address flow did not succeed. %s", msg)
            return success, msg
        except Exception as e:
            return False, f"Address creation failed: {str(e)}"

    def _address_save_succeeded(self, content: List[str]) -> bool:
        """True if success copy appears in any extracted page fragment (substring match)."""
        success = self.address_message.get("address_success_msg") or ""
        if not success:
            return False
        return any(success in line for line in content)

    # Substrings that usually indicate inline validation / errors (not nav chrome)
    _ERROR_TEXT_HINTS = (
        "must ",
        "invalid",
        "error",
        "required",
        "enter a",
        "enter ",
        "please ",
        "cannot ",
        "can't ",
        "failed",
        "try again",
        "character",
        "digit",
        "zip",
        "pin",
        "field",
        "missing",
        "empty",
        "not valid",
        "wrong",
        "incorrect",
    )

    def _format_outcome_message(self, success: bool, content: List[str]) -> str:
        if success:
            success_text = self.address_message["address_success_msg"]
            for line in content:
                if success_text in line:
                    return line.strip()
            return success_text
        primary, preview = self._extract_validation_error(content)
        if preview:
            return f"{primary}\n---\nOther visible text: {preview}"
        return primary

    def _lines_that_look_like_errors(self, content: List[str]) -> List[str]:
        out: List[str] = []
        for line in content:
            s = line.strip()
            if len(s) < 4 or len(s) > 280:
                continue
            low = s.lower()
            if any(h in low for h in self._ERROR_TEXT_HINTS):
                out.append(s)
        # Dedupe preserving order
        seen = set()
        unique = []
        for s in out:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        return unique

    def _summarize_visible_text(self, content: List[str], max_items: int = 45) -> str:
        if not content:
            return "(no text extracted from page source)"
        chunk = content[:max_items]
        return " | ".join(chunk)

    def _extract_validation_error(self, content: List[str]) -> Tuple[str, str]:
        """
        Map on-screen text to known validation messages from AddressMessage (values, not dict keys).
        Always prefers quoting the actual UI string the user would see.

        Returns:
            (primary_message_for_asserts/logs, optional_secondary_excerpt)
        """
        try:
            for key, expected in self.address_message.items():
                if key == "address_success_msg" or not expected:
                    continue
                for line in content:
                    if expected in line:
                        ui = line.strip()
                        return f'UI error (matched "{expected}"): {ui}', ""
                    if len(line) >= 4 and line in expected:
                        ui = line.strip()
                        return f'UI error: {ui}', ""

            error_like = self._lines_that_look_like_errors(content)
            if error_like:
                joined = " | ".join(error_like[:12])
                return f"UI validation / error text: {joined}", ""

            preview = self._summarize_visible_text(content)
            return (
                "No known or heuristic error line found; check page state.",
                preview,
            )
        except Exception as e:
            self.logger.error(
                f"Exception while extracting validation error from page: {e}"
            )
            return f"Unable to read validation state: {e}", ""

    def get_final_error_msg(self, content: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        Backward-compatible helper: returns (primary_error_message, page_excerpt_or_empty).

        If ``content`` is omitted, the current page is scraped again.
        """
        if content is None:
            content = self.extract_page_contents()
        return self._extract_validation_error(content)



    def _swipe_address_list(self, direction: str = "down") -> None:
        """One vertical swipe on the main window to scroll a long address list."""
        size = self.driver.get_window_size()
        width = size["width"]
        height = size["height"]
        center_x = width // 2
        if direction == "down":
            start_y, end_y = int(height * 0.78), int(height * 0.22)
        else:
            start_y, end_y = int(height * 0.22), int(height * 0.78)
        self.drag_and_drop(center_x, start_y, center_x, end_y)

    def _reveal_address_row(self, address: str, max_swipes: int = 25) -> bool:
        """Scroll until the address row is on screen (down then up)."""
        row = self.build_locator(self.locator["address_row"], address)
        if self.is_displayed(row, timeout=4):
            return True
        self.scroll_to_element_by_touch(row, direction="down", max_swipes=max_swipes)
        if self.is_displayed(row, timeout=5):
            return True
        self.scroll_to_element_by_touch(row, direction="up", max_swipes=max_swipes)
        return self.is_displayed(row, timeout=5)

    def is_address_visible(self, address: str, timeout: int = 15, max_swipes: int = 25) -> bool:
        """True if the address row appears in the list; scrolls down then up when many rows exist."""
        row = self.build_locator(self.locator["address_row"], address)
        if not self._reveal_address_row(address, max_swipes=max_swipes):
            return False
        return self.is_displayed(row, timeout=timeout)

    def wait_until_address_not_visible(self, address: str, timeout: int = 15, max_swipes: int = 25) -> bool:
        """True when the row is gone; waits for dismiss then scrolls the list to ensure it is not present."""
        row = self.build_locator(self.locator["address_row"], address)
        if not self.wait_for_element_to_disappear(row, timeout=timeout):
            return False

        def _absent_while_scrolling(direction: str) -> bool:
            prev_src = None
            for _ in range(max_swipes):
                if self.is_displayed(row, timeout=2):
                    return False
                self._swipe_address_list(direction)
                time.sleep(0.2)
                src = self.driver.page_source
                if prev_src is not None and src == prev_src:
                    break
                prev_src = src
            return True

        if not _absent_while_scrolling("down"):
            return False
        if not _absent_while_scrolling("up"):
            return False
        return True

    def click_edit_address_button(self, address: str):
        self.logger.info(f"Clicking edit address button for {address}")
        if not self._reveal_address_row(address):
            raise Exception(f"Address row not found after scrolling: {address}")
        self.click_element(self.build_locator(self.locator["edit_address_button"], address))

    def click_cancel_location_form(self):
        self.logger.info("Clicking cancel on location / address form")
        self.click_element(self.locator["cancel_location_form_button"])

    def update_address(
        self, existing_name: str, data: dict
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Open edit, snapshot form, apply only non-null spreadsheet fields, save, wait 5s,
        re-open by the (possibly new) address name, snapshot again, and verify deltas.

        Returns ``(success, message, meta)`` where ``meta`` on success may include
        ``before``, ``after``, ``modified_keys`` for callers/tests; on failure ``meta`` is None.
        """
        tenant = str(data.get("tenant") or "us").strip().lower()
        before: Dict[str, str] = {}
        after: Dict[str, str] = {}
        modified_keys: Set[str] = set()
        try:
            self.click_edit_address_button(existing_name)
            time.sleep(1)
            before = self.read_address_form_snapshot(tenant)
            self.logger.info("Address form snapshot before update: %s", before)

            applied_fields = self.apply_address_field_updates_from_row(data, tenant)
            modified_keys = set(applied_fields)
            if not modified_keys:
                return (
                    False,
                    "No updatable fields in spreadsheet row (all null/empty or only existingAddressName/tenant).",
                    None,
                )
            self._click_save_address_form()

            content = self.extract_page_contents()
            success = self._address_save_succeeded(content)
            msg = self._format_outcome_message(success, content)
            if not success:
                self.logger.warning("Address update save did not succeed. %s", msg)
                return False, msg, None

            time.sleep(5)

            new_list_name = (
                self._cell_to_str(data["addressName"])
                if self._sheet_has_value(data.get("addressName"))
                else existing_name
            )
            self.click_edit_address_button(new_list_name)
            time.sleep(1)
            after = self.read_address_form_snapshot(tenant)
            self.logger.info("Address form snapshot after update: %s", after)

            ok, ver_msg = self._verify_after_partial_update(before, after, data, modified_keys)
            self.logger.info(f"Verification message: {ver_msg ,ok}")
            if not ok:
                detail = f"Save succeeded but field verification failed: {ver_msg}"
                self.logger.error(detail)
                return False, detail, None

            meta = {
                "before": dict(before),
                "after": dict(after),
                "modified_keys": sorted(modified_keys),
            }
            return True, msg, meta
        except Exception as e:
            self.logger.exception("Address update failed")
            return False, f"Address update failed: {str(e)}", None

    def cancel_address_edit(self, existing_name: str, draft_name: str) -> Tuple[bool, str]:
        """Open edit, change the display name to ``draft_name``, cancel, and discard changes."""
        try:
            self.click_edit_address_button(existing_name)
            time.sleep(1)
            if draft_name:
                self.course_create.enter_addressName(draft_name)
            self.click_cancel_location_form()
            time.sleep(1.5)
            return True, "cancel_ok"
        except Exception as e:
            return False, f"Address cancel flow failed: {str(e)}"

    def click_delete_address_button(self, address):
        self.logger.info(f"Clicking delete address button for {address}")
        if not self._reveal_address_row(address):
            raise Exception(f"Address row not found after scrolling: {address}")
        self.click_element(self.build_locator(self.locator["delete_address_button"], address))

    def click_confirm_delete_button(self):
        self.logger.info("Clicking confirm delete button")
        self.click_element(self.locator["confirm_delete_button"])

    def click_close_dialog_button(self):
        self.logger.info("Clicking close dialog button")
        self.click_element(self.locator["close_dialog_button"])


    def delete_address(self, address):
        try:
            self.logger.info(f"Deleting address: {address}")
            self.click_delete_address_button(address)
            self.click_confirm_delete_button()
            content = self.extract_page_contents()
            success = self._address_delete_succeeded(content)
            msg = self._format_outcome_message(success, content)
            if not success:
                self.logger.warning("Address flow did not succeed. %s", msg)
            return success, msg
        except Exception as e:
            return False, f"Address deletion failed: {str(e)}"

    def _address_delete_succeeded(self, content: List[str]) -> bool:
        """True if success copy appears in any extracted page fragment (substring match)."""
        success = self.address_message.get("address_delete_success_msg") or ""
        if not success:
            return False
        return any(success in line for line in content)