import json
import os
import time
import pytest
import allure

from utils.driver_manager import DriverManager
from config.config import TestConfig
from utils.googleSheet_helper import read_google_sheet
from utils.helpers import read_csv_as_dict, take_screenshot
from pages.login_page import LoginPage
from pages.onboard_page import OnBoardPage
from pages.my_events_page import MyEventsPage
from pages.filters_page import FiltersPage
from utils.navigator import Navigator
from utils.logger_config import LoggerConfig


def _load_filter_rows():
    # rows = read_csv_as_dict("data/filter_run1.csv")
    rows = read_google_sheet(os.getenv("GOOGLE_SHEET_NAME"), "Filter")
    print(f"Filter data: {rows}")
    return [r for r in rows if r.get("Testcase_ID", "").strip()]


FILTER_ROWS = _load_filter_rows()


def _row_id(row):
    return row.get("Testcase_ID", "unknown")


def _rows_prefix(prefix: str):
    return [r for r in FILTER_ROWS if r.get("Testcase_ID", "").startswith(prefix)]



LEGACY_FILTER_ROWS = [r for r in FILTER_ROWS if r["Testcase_ID"].startswith("Filter_04")]


class TestFilter:
    @pytest.fixture(autouse=True)
    def setup(self, request):
        test_method_name = request.node.name
        self.logger = LoggerConfig.setup_test_logger(self.__class__.__name__, test_method_name)

        test_id = None
        for marker in request.node.iter_markers("id"):
            if marker.args:
                test_id = marker.args[0]
                break

        start_time = time.time()
        LoggerConfig.log_test_start(self.logger, test_method_name, test_id)

        try:
            self.driver_manager = DriverManager()
            self.driver = self.driver_manager.start_driver()
            self.login_page = LoginPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.onboard_page = OnBoardPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.my_events_page = MyEventsPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.filters_page = FiltersPage(self.driver, TestConfig.MOBILE_PLATFORM)
            self.nav = Navigator(self.driver, TestConfig.MOBILE_PLATFORM)

            request.node.driver = self.driver
            self.logger.info("Test setup completed successfully")
            yield

        except Exception as e:
            self.logger.error(f"Test setup failed: {str(e)}")
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            status = "COMPLETED"

            rep_call = getattr(request.node, "rep_call", None)
            if rep_call is not None and rep_call.failed:
                take_screenshot(self.driver, f"test_failed_{self.__class__.__name__}")
                status = "FAILED"

            LoggerConfig.log_test_end(self.logger, test_method_name, duration, status)

            if hasattr(self, "driver_manager"):
                self.driver_manager.quit_driver()
                self.logger.info("Driver cleanup completed")

    def _parse_filters_row(self, row):
        raw = row.get("Filters")
        if not raw or not str(raw).strip():
            self.logger.warning(
                "Row %s has no Filters column; using empty filter dict",
                row.get("Testcase_ID", "?"),
            )
            return {}
        try:
            parsed = json.loads(raw)
            self.logger.debug(
                "Row %s: parsed Filters JSON with keys %s",
                row.get("Testcase_ID", "?"),
                list(parsed.keys()) if isinstance(parsed, dict) else type(parsed).__name__,
            )
            return parsed
        except json.JSONDecodeError as e:
            self.logger.error(
                "Row %s: invalid Filters JSON (%s): %s",
                row.get("Testcase_ID", "?"),
                e,
                raw[:200] + ("…" if len(str(raw)) > 200 else ""),
            )
            return {}

    def _run_filter_scenario(self, row):
        tc = row.get("Testcase_ID", "")
        scenario = row.get("Scenario", "")
        self.logger.info("=" * 72)
        self.logger.info("Filter scenario | testcase_id=%s", tc)
        self.logger.info("Filter scenario | description=%s", scenario)

        filters = self._parse_filters_row(row)
        self.logger.info(
            "Filter scenario | filter_categories=%s",
            list(filters.keys()) if filters else [],
        )
        if filters:
            self.logger.debug("Filter scenario | full_filter_dict=%s", filters)
        sd, ed = row.get("start_date"), row.get("end_date")
        if sd or ed:
            self.logger.info("Filter scenario | custom_schedule start_date=%r end_date=%r", sd, ed)

        with allure.step(f"[{tc}] Navigate to My Events"):
            self.logger.info("Step 1/4: Navigate to My Events (login if needed)")
            status = self.nav.navigate_to_my_events_page(
                "nivedhas@abovecloud9.ai", TestConfig.TEST_PASSWORD, "us"
            )
            self.logger.info("Step 1/4: Completed — navigate status=%r", status)

        with allure.step(f"[{tc}] Apply filters"):
            self.logger.info("Step 2/4: Open filters and apply combination from CSV")
            self.filters_page.apply_filter_combination(filters, sd, ed)
            self.logger.info("Step 2/4: Completed — filter UI applied")

        self.logger.info("Step 3/4: Wait for filtered event list to stabilize (4s)")
        time.sleep(4)
        self.logger.info("Step 3/4: Completed")

        with allure.step(f"[{tc}] Validate event_card semantic labels"):
            self.logger.info("Step 4/4: Validate visible cards against applied filters")
            self.my_events_page.verify_visible_cards_match_applied_filters(
                filters,
                sd,
                ed,
                username_for_role_validation="nivash m",
            )
            self.logger.info("Step 4/4: Completed — all visible cards match constraints")

        self.logger.info("Filter scenario | testcase_id=%s finished successfully", tc)
        self.logger.info("=" * 72)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", LEGACY_FILTER_ROWS, ids=_row_id)
    def test_filter_legacy_event_cards(self, row):
        """Filter_01–04: legacy combinations (product type, schedule, role, status, mode)."""
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_S1_type_"), ids=_row_id)
    def test_filter_single_category_type_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_S1_product_type_"), ids=_row_id)
    def test_filter_single_category_product_type_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_S1_mode_"), ids=_row_id)
    def test_filter_single_category_mode_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_S1_schedule_"), ids=_row_id)
    def test_filter_single_category_schedule_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_S1_status_06"), ids=_row_id)
    def test_filter_single_category_status_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_S1_role_"), ids=_row_id)
    def test_filter_single_category_role_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_MS_"), ids=_row_id)
    def test_filter_multi_select_single_category_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_C2_"), ids=_row_id)
    def test_filter_two_categories_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_C3_"), ids=_row_id)
    def test_filter_three_categories_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_C4_"), ids=_row_id)
    def test_filter_four_categories_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_C5_"), ids=_row_id)
    def test_filter_five_categories_event_cards(self, row):
        self._run_filter_scenario(row)

    @pytest.mark.data_driven
    @pytest.mark.filter
    @pytest.mark.parametrize("row", _rows_prefix("Filter_C6_"), ids=_row_id)
    def test_filter_six_categories_event_cards(self, row):
        self._run_filter_scenario(row)
