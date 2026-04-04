import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

logger = logging.getLogger(__name__)

def read_google_sheet(sheet_name: str, worksheet_name: str):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "glad-automation-213257ed4edd.json", scope
        )

        client = gspread.authorize(creds)

        sheet = client.open(sheet_name).worksheet(worksheet_name)

        data = sheet.get_all_records()

        logger.info(f"Read {len(data)} rows from Google Sheet")
        return data

    except Exception as e:
        logger.error(f"Error reading Google Sheet: {e}")
        return []

