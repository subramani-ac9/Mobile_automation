from appium.webdriver.common.appiumby import AppiumBy


class AddressLocator:


    android = {
        "ManageAddress_icon" : (AppiumBy.ACCESSIBILITY_ID, 'Manage Locations Tile Button'),
        "create_address_button" : (AppiumBy.ACCESSIBILITY_ID, 'Create Location Button'),
        "create_button" : (AppiumBy.ACCESSIBILITY_ID, 'Save Button'),
        "state_dropdown" : (AppiumBy.ACCESSIBILITY_ID, 'State Select Dropdown'),
        "state_list" : (AppiumBy.ACCESSIBILITY_ID, lambda state: f'{state}'),
    }

    ios = {**android}

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return AddressLocator.android
        elif platform.lower() == 'ios':
            return AddressLocator.ios
        else:
            raise Exception(f"Invalid platform :: {platform}")