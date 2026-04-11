import csv
import os
import datetime
import logging
import time
logger = logging.getLogger(__name__)


def attach_screenshot_to_allure(driver, name="screenshot"):
    """Take screenshot and attach to current Allure report (e.g. on failure)."""
    try:
        import allure
        png = driver.get_screenshot_as_png()
        if png:
            allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        logger.debug(f"Allure screenshot attach failed: {e}")


def take_screenshot(driver, filename):
    """Take screenshot and save to reports directory"""
    try:
        logger.info(f"Taking screenshot: {filename}")
        # Create reports directory if it doesn't exist
        reports_dir = "reports/screenshots"
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{reports_dir}/{filename}_{timestamp}.png"

        driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Failed to take screenshot: {str(e)}")
        return None


def read_csv_as_dict(file_name: str):
    logger.info(f"Reading CSV file: {file_name}")
    try:
        import csv
        with open(file_name, mode='r', newline='', encoding='utf-8') as file:
            data = list(csv.DictReader(file))
            logger.info(f"Successfully read {len(data)} rows from {file_name}")
            return data
    except Exception as e:
        logger.error(f"Failed to read CSV file {file_name}: {e}")
        return []

def write_csv_from_dicts(file_name: str, data: list[dict]):
    logger.info(f"Writing {len(data)} rows to CSV file: {file_name}")
    try:
        import csv
        if not data:
            raise ValueError("Data list is empty.")
        
        fieldnames = list(data[0].keys())

        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            logger.info(f"Successfully wrote {len(data)} rows to {file_name}")
    except Exception as e:
        logger.error(f"Failed to write CSV file {file_name}: {e}")
        raise

def read_input_data(file_name: str):
    """Read CSV file and return as pandas DataFrame"""
    logger.info(f"Reading input data from: {file_name}")
    try:
        import pandas as pd
        df = pd.read_csv(file_name)
        logger.info(f"Successfully read {len(df)} rows from {file_name}")
        return df
    except Exception as e:
        logger.error(f"Failed to read input data from {file_name}: {e}")
        return None

def write_output_data(file_name: str, data):
    """Write pandas DataFrame to CSV file"""
    logger.info(f"Writing output data to: {file_name}")
    try:
        data.to_csv(file_name, index=False)
        logger.info(f"Successfully wrote output to: {file_name}")
    except Exception as e:
        logger.error(f"Failed to write output data to {file_name}: {e}")
        raise

# webview helper functions

def switch_to_webview(driver, timeout=10):
    """
    Switch from NATIVE_APP to WebView context.
    Call this BEFORE interacting with any WebView element.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        contexts = driver.contexts
        wv = next((c for c in contexts if "WEBVIEW" in c), None)
        if wv:
            driver.switch_to.context(wv)
            print(f"✅ Switched to WebView: {wv}")
            return
        time.sleep(1)
    raise Exception(
        f"❌ WebView context not found after {timeout}s. "
        f"Available contexts: {driver.contexts}"
    )


def switch_to_native(driver):
    """
    Switch back to NATIVE_APP context.
    Call this BEFORE interacting with any native element.
    """
    driver.switch_to.context("NATIVE_APP")
    print("✅ Switched back to NATIVE_APP")


def get_current_context(driver):
    """Debug helper — print current context."""
    ctx = driver.current_context
    print(f"Current context: {ctx}")
    return ctx


def print_all_contexts(driver):
    """Debug helper — print all available contexts."""
    contexts = driver.contexts
    print(f"All contexts: {contexts}")
    return contexts