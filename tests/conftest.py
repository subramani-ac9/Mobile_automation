"""
Pytest hooks: attach failure screenshots to Allure when tests expose item.driver
(set via request.node.driver in test class setup fixtures).
"""

import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """After each phase, on test body failure capture screen while driver is still alive."""
    outcome = yield
    report = outcome.get_result()
    # Store for teardown fixtures that need pass/fail (e.g. disk screenshots)
    setattr(item, f"rep_{report.when}", report)

    if report.when != "call" or not report.failed:
        return

    driver = getattr(item, "driver", None)
    if driver is None:
        logger.debug("No item.driver — skipping Allure failure screenshot for %s", item.nodeid)
        return

    try:
        from utils.helpers import attach_screenshot_to_allure

        safe_name = item.name.replace("[", "_").replace("]", "_")[:80]
        attach_screenshot_to_allure(driver, name=f"Failure screenshot — {safe_name}")
    except Exception as e:
        logger.warning("Could not attach failure screenshot to Allure: %s", e)
