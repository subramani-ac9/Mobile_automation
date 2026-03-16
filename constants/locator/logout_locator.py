from appium.webdriver.common.appiumby import AppiumBy


class LogoutLocator:

    android = {
        "logout": (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Logout Tile Button"]'),
        'account_icon': (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Account Button"]'),
        'confirm_logout': (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Confirm Dialog Button"]'),
        'cancel_logout': (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Close Dialog Button"]'),
    }
    ios = {
        "logout": (AppiumBy.ACCESSIBILITY_ID, 'Logout'),    
        'account_icon': (AppiumBy.ACCESSIBILITY_ID, 'bottom_nav_Account\nAccount'),
        'confirm_logout': (AppiumBy.ACCESSIBILITY_ID, 'Logout'),
    }
    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return LogoutLocator.android
        elif platform.lower() == 'ios':
            return LogoutLocator.ios
        else:
            raise Exception(f"Invalid platfrom :: {platform}")