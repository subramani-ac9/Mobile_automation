from appium.webdriver.common.appiumby import AppiumBy


class ForgotPasswordLocator:
    android = {
        "forgot_password_screen": (AppiumBy.ID, "forgot_password_screen"),
        "email_field": (AppiumBy.ID, "email"),
        "send_reset_code_button": (AppiumBy.ID, "send_reset_code_btn"),
        "verification_code_field": (AppiumBy.ID, "verification_code"),
        "new_password_field": (AppiumBy.ID, "new_password"),
        "re_enter_password_field": (AppiumBy.ID, "re_enter_password"),
        "submit_button": (AppiumBy.ID, "submit_btn"),
        "back_to_login": (AppiumBy.ID, "back_to_login"),
        "success_message": (AppiumBy.ID, "success_msg"),
        "error_message": (AppiumBy.ID, "error_msg"),
        "invalid_code_error": (AppiumBy.XPATH, "//*[contains(@text, 'Invalid verification code')]"),
        "code_expired_error": (AppiumBy.XPATH, "//*[contains(@text, 'Code expired')]"),
        "email_not_found_error": (AppiumBy.XPATH, "//*[contains(@text, 'Email not found')]"),
    }

    ios = {
        "forgot_password_screen": (AppiumBy.ACCESSIBILITY_ID, "Forgot Password"),
        "email_field": (AppiumBy.ACCESSIBILITY_ID, "Email"),
        "send_reset_code_button": (AppiumBy.ACCESSIBILITY_ID, "Send Reset Code"),
        "verification_code_field": (AppiumBy.ACCESSIBILITY_ID, "Verification Code"),
        "new_password_field": (AppiumBy.ACCESSIBILITY_ID, "New Password"),
        "re_enter_password_field": (AppiumBy.ACCESSIBILITY_ID, "Re-enter your password"),
        "submit_button": (AppiumBy.ACCESSIBILITY_ID, "Submit"),
        "back_to_login": (AppiumBy.ACCESSIBILITY_ID, "Back to Login"),
        "success_message": (AppiumBy.XPATH, "//*[contains(@label, 'Password reset successful')]"),
        "error_message": (AppiumBy.XPATH, "//*[contains(@label, 'Error')]"),
        "invalid_code_error": (AppiumBy.XPATH, "//*[contains(@label, 'Invalid verification code')]"),
        "code_expired_error": (AppiumBy.XPATH, "//*[contains(@label, 'Code expired')]"),
        "email_not_found_error": (AppiumBy.XPATH, "//*[contains(@label, 'Email not found')]"),
        "scroll": (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeScrollView"),
    }

    @classmethod
    def get_locators(cls, platform):
        return cls.ios if platform.lower() == "ios" else cls.android
