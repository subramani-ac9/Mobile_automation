from appium.webdriver.common.appiumby import AppiumBy


class QuotesLocator:
    android = {
        "jai_gurudev_title": (
            AppiumBy.ACCESSIBILITY_ID, "Jai Gurudev!"),
        "quote_more_options": (
            AppiumBy.ACCESSIBILITY_ID,
            "Quote More Options Button",
        ),
        "edit_quote_menu": (
            AppiumBy.ACCESSIBILITY_ID,
            'Edit Quote Menu Item\nEdit',
        ),
        "share_quote_menu": (
            AppiumBy.ACCESSIBILITY_ID,
            'Share Quote Menu Item\nShare',
        ),
        "download_quote_menu": (
            AppiumBy.ACCESSIBILITY_ID,
            'Download Quote Menu Item\nDownload',
        ),
        "preparing_quote_share": (
            AppiumBy.ACCESSIBILITY_ID,
            'Preparing quote for sharing...',
        ),
        "downloading_quote": (
            AppiumBy.ACCESSIBILITY_ID,
            'Downloading quote...',
        ),
    }
    ios = {
        "jai_gurudev_title": (
            AppiumBy.ACCESSIBILITY_ID, "Jai Gurudev!"),
        "quote_more_options": (
            AppiumBy.ACCESSIBILITY_ID,
            "Quote More Options Button",
        ),
        "edit_quote_menu": (
            AppiumBy.ACCESSIBILITY_ID,
            'Edit Quote Menu Item\nEdit',
        ),
        "share_quote_menu": (
            AppiumBy.ACCESSIBILITY_ID,
            'Share Quote Menu Item\nShare',
        ),
        "download_quote_menu": (
            AppiumBy.ACCESSIBILITY_ID,
            'Download Quote Menu Item\nDownload',
        ),
        "preparing_quote_share": (
            AppiumBy.ACCESSIBILITY_ID,
            'Preparing quote for sharing...',
        ),
        "downloading_quote": (
            AppiumBy.ACCESSIBILITY_ID,
            'Downloading quote...',
        ),
    }

    @classmethod
    def get_locators(cls, platform: str) -> dict:
        p = (platform or "").lower()
        if p == "android":
            return dict(cls.android)
        if p == "ios":
            return dict(cls.ios)
        raise ValueError(f"Unsupported platform for QuotesLocator: {platform!r}")
