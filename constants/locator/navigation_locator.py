from appium.webdriver.common.appiumby import AppiumBy


class NavigationLocator:
    android = {
        "account": (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Account"]'),
        "my_events": (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="My Events"]'),
        "resources": (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Resources"]'),
        "live_darshan": (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Live Darshan"]'),
    }

    ios = {
        "live_darshan": (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Live Darshan\nLive Darshan'),
        "my_events": (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_My Events\nMy Events'),
        "resources": (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Resources\nResources'),
        "account": (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Account\nAccount'),
    }

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return NavigationLocator.android
        elif platform.lower() == 'ios':
            return NavigationLocator.ios
        else:
            raise Exception(f"Invalid platfrom :: {platform}")
