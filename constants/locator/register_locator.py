from appium.webdriver.common.appiumby import AppiumBy


class RegisterLocator:
    android = {
        "register_screen": (AppiumBy.ID, "register_screen"),
        "first_name_field": (AppiumBy.ID, "first_name"),
        "last_name_field": (AppiumBy.ID, "last_name"),
        "email_field": (AppiumBy.ID, "email"),
        "password_field": (AppiumBy.ID, "password"),
        "confirm_password_field": (AppiumBy.ID, "confirm_password"),
        "sign_up_button": (AppiumBy.ID, "sign_up_btn"),
        "back_to_login": (AppiumBy.ID, "back_to_login"),
        "already_have_account": (AppiumBy.ID, "login_link"),
        "success_message": (AppiumBy.ID, "success_msg"),
        "error_message": (AppiumBy.ID, "error_msg"),
        "email_exists_error": (AppiumBy.XPATH, "//*[contains(@text, 'Email already exists')]"),
        "password_mismatch_error": (AppiumBy.XPATH, "//*[contains(@text, 'Passwords do not match')]"),
        "invalid_email_error": (AppiumBy.XPATH, "//*[contains(@text, 'Invalid email format')]"),
        "continue_page": (AppiumBy.ID, "continue_page"),
        "continue_button": (AppiumBy.ID, "continue_btn"),
    }

    ios = {
        "register_screen": (AppiumBy.ACCESSIBILITY_ID, "Sign Up"),
        "first_name_field": (AppiumBy.ACCESSIBILITY_ID, "First Name"),
        "last_name_field": (AppiumBy.ACCESSIBILITY_ID, "Last Name"),
        "email_field": (AppiumBy.ACCESSIBILITY_ID, "Email"),
        "password_field": (AppiumBy.ACCESSIBILITY_ID, "Password"),
        "confirm_password_field": (AppiumBy.ACCESSIBILITY_ID, "Confirm Password"),
        "sign_up_button": (AppiumBy.ACCESSIBILITY_ID, "Sign Up"),
        "back_to_login": (AppiumBy.ACCESSIBILITY_ID, "Back to Login"),
        "already_have_account": (AppiumBy.ACCESSIBILITY_ID, "Already have an account? Sign In"),
        "success_message": (AppiumBy.XPATH, "//*[contains(@label, 'Registration successful')]"),
        "error_message": (AppiumBy.XPATH, "//*[contains(@label, 'Error')]"),
        "email_exists_error": (AppiumBy.XPATH, "//*[contains(@label, 'Email already exists')]"),
        "password_mismatch_error": (AppiumBy.XPATH, "//*[contains(@label, 'Passwords do not match')]"),
        "invalid_email_error": (AppiumBy.XPATH, "//*[contains(@label, 'Invalid email format')]"),
        "continue_page": (AppiumBy.ACCESSIBILITY_ID, "Continue"),
        "continue_button": (AppiumBy.ACCESSIBILITY_ID, "Continue"),
        "scroll": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeScrollView"),
    }

    @classmethod
    def get_locators(cls, platform):
        return cls.ios if platform.lower() == "ios" else cls.android
