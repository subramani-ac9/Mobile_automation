from appium.webdriver.common.appiumby import AppiumBy


class OnBoardLocator:
    android ={
        "continue_button":(AppiumBy.ACCESSIBILITY_ID, 'Continue Button')
    }
    ios = {
        "continue_button": (AppiumBy.ACCESSIBILITY_ID, 'Continue Button')
    }
    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return OnBoardLocator.android
        elif platform.lower() == 'ios':
            return OnBoardLocator.ios
        else:
            raise Exception(f"Invalid platfrom :: {platform}")