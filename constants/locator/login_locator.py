from appium.webdriver.common.appiumby import AppiumBy


class LoginLocator:
    android = {
        "login_screen":(AppiumBy.XPATH,'//android.view.View[@content-desc="Sign in to continue to your account"]'),
         "email":(AppiumBy.XPATH,"//android.view.View[@content-desc='Username']/following-sibling::android.widget.EditText[1]"),
          "email_display": (
            AppiumBy.XPATH,
            "//android.view.View[@content-desc='Username']/following-sibling::android.view.View"
        ),
        "password":(AppiumBy.XPATH,"//android.view.View[@content-desc='Password']/following-sibling::android.widget.EditText[1]"),
        "continue" : (AppiumBy.XPATH, "//android.widget.Button[contains(@content-desc, 'Continue')]"),         
        "signin": (AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "Log In")]'),
        "forgot_password": (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Forgot Password?"]'),
        "signup": (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Sign Up"]'),
        "error_msg":(AppiumBy.XPATH, lambda msg: f'/;/android.view.View[@content-desc="{msg}"]'),
        "processing_overlay": (AppiumBy.XPATH, '//android.view.View[@content-desc="Processing..."]'),
        "email_validation": (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'email')]"),
        "password_validation": (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'password')]"),
        "screen": (AppiumBy.XPATH, '//android.view.View[@content-desc="Sign in to continue to your account"]'),
        "app_bar": (AppiumBy.XPATH, '//android.view.View[@content-desc="Sign In"]'),
        "forgot_password_button": (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Forgot Password?"]'),
        "create_account_button": (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Create Account"]'),
        "contact_support_button": (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Contact Support Button"]'),
        "Show_password_button": (AppiumBy.ACCESSIBILITY_ID, 'Show/Hide Password'),


        "country_dropdown": (AppiumBy.XPATH, '//android.view.View[contains(@content-desc, "Country")]'),
        "country_field": (AppiumBy.XPATH, '//android.widget.Button[contains(@content-desc, "The Art of Living Foundation") or contains(@content-desc, "Country")]'),
        "tenant_option": (AppiumBy.XPATH, lambda tenant: f'//android.view.View[@content-desc="{tenant}"]'),
        "search_tenant": (AppiumBy.XPATH, '//android.widget.EditText'),
        "tenant_list": (AppiumBy.XPATH, '//android.widget.ScrollView//android.view.View[contains(@content-desc, "Foundation")]'),
        "scroll": (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().scrollable(true)'),
    }

    ios = {
        "login_screen":(AppiumBy.ACCESSIBILITY_ID,'Sign in to continue to your account'),
        "email": (AppiumBy.ACCESSIBILITY_ID, "Email"),
        "password": (AppiumBy.ACCESSIBILITY_ID, "Password"),
        # "signin": (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "Sign In"`]'),
        "signin": (AppiumBy.ACCESSIBILITY_ID, 'Login Button'),
        "forgot_password": (AppiumBy.ACCESSIBILITY_ID, 'Forgot Password?'),
        "signup": (AppiumBy.ACCESSIBILITY_ID, 'Sign Up'),
        "error_msg": (AppiumBy.ACCESSIBILITY_ID, lambda msg: f'{msg}'),
        "processing_overlay": (AppiumBy.ACCESSIBILITY_ID, "Processing..."),
        "email_validation": (AppiumBy.ACCESSIBILITY_ID, "email_validation"),
        "password_validation": (AppiumBy.ACCESSIBILITY_ID, "password_validation"),
        "screen": (AppiumBy.ACCESSIBILITY_ID, 'Sign in to continue to your account'),
        "app_bar": (AppiumBy.XPATH, '//XCUIElementTypeOther[@name="Sign In"]'),
        "forgot_password_button": (AppiumBy.ACCESSIBILITY_ID, 'Forgot Password?'),
        "Show_password_button": (AppiumBy.ACCESSIBILITY_ID, 'Show password'),

        "country_dropdown": (AppiumBy.ACCESSIBILITY_ID, "Country"),
        "country_field": (AppiumBy.ACCESSIBILITY_ID, "Tenant Selector"),
        "tenant_option": (AppiumBy.ACCESSIBILITY_ID, lambda tenant: f'{tenant}'),
        "search_tenant": (AppiumBy.ACCESSIBILITY_ID, "Search"),
        "tenant_list": (AppiumBy.XPATH, '//XCUIElementTypeScrollView//XCUIElementTypeCell')
    }

    @classmethod
    def get_locators(cls, platform):
        if platform.lower() == 'android':
            return LoginLocator.android
        elif platform.lower() == 'ios':
            return LoginLocator.ios
        else:
            raise Exception(f"Invalid platform :: {platform}")