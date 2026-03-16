import os
from dotenv import load_dotenv

load_dotenv()

class TestConfig:    
    # Appium Server Configuration
    APPIUM_HOST = os.getenv('APPIUM_HOST', 'localhost')
    APPIUM_PORT = os.getenv('APPIUM_PORT', 4723)
    
    # Platform Selection
    MOBILE_PLATFORM = os.getenv('MOBILE_PLATFORM', 'android').lower()
    
    # Android Configuration
    ANDROID_PLATFORM_NAME = os.getenv('ANDROID_PLATFORM_NAME', 'Android')
    ANDROID_DEVICE_NAME = os.getenv('ANDROID_DEVICE_NAME', 'emulator-5554')
    ANDROID_PLATFORM_VERSION = os.getenv('ANDROID_PLATFORM_VERSION', '')
    ANDROID_APP_PACKAGE = os.getenv('ANDROID_APP_PACKAGE', 'com.aoljourney.teacher.app.dev')
    ANDROID_APP_ACTIVITY = os.getenv('ANDROID_APP_ACTIVITY', 'com.aoljourney.teacher.app.MainActivity')
    ANDROID_APP_PATH = os.getenv('ANDROID_APP_PATH', '')
    
    # iOS Configuration
    IOS_PLATFORM_NAME = os.getenv('IOS_PLATFORM_NAME', 'iOS')
    IOS_DEVICE_NAME = os.getenv('IOS_DEVICE_NAME', "Nivedha's iPhone")  # Real device
    IOS_PLATFORM_VERSION = os.getenv('IOS_PLATFORM_VERSION', '18.6.2')
    IOS_BUNDLE_ID = os.getenv('IOS_BUNDLE_ID', 'com.aoljourney.teacher.app.dev')
    IOS_UDID = os.getenv('IOS_UDID', '00008110-001E29A21EFBA01E')  # Real device UDID
    IOS_XCODE_ORG_ID = os.getenv('IOS_XCODE_ORG_ID', '')
    IOS_XCODE_SIGNING_ID = os.getenv('IOS_XCODE_SIGNING_ID', 'iPhone Developer')
    IOS_APP_PATH = os.getenv('IOS_APP_PATH', '')
    
    # Timeouts
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', 10))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', 20))
    DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', 30))
    ELEMENT_TIMEOUT = int(os.getenv('ELEMENT_TIMEOUT', 10))
    
    # Test Data
    TEST_EMAIL = os.getenv('TEST_EMAIL', 'KR2227')
    TEST_PASSWORD = os.getenv('TEST_PASSWORD', 'Admin@ac9')

    # TEST_EMAIL = os.getenv('TEST_EMAIL', 'gohul1@abovecloud9.ai')
    # TEST_PASSWORD = os.getenv('TEST_PASSWORD', 'Admin@123')
    
    # Tenant/Country Configuration
    DEFAULT_TENANT = os.getenv('DEFAULT_TENANT', '[DND] The Art of Living Foundation (US)')

    FORGOT_PASSWORD_EMAIL = os.getenv('FORGOT_PASSWORD_EMAIL', 'forgot@example.com')
    TEST_MEETUP_ONLINE_PRODUCT = os.getenv('TEST_MEETUP_ONLINE_PRODUCT', 'Short SKY Meditation Meetup')
    TEST_MEETUP_INPERSON_PRODUCT = os.getenv('TEST_MEETUP_INPERSON_PRODUCT', 'Short SKY Meditation Meetup')
    
    # Localization Test Data - Converted versions of nivedhas@abovecloud9.ai
    TEST_EMAIL_CYRILLIC = os.getenv('TEST_EMAIL_CYRILLIC', 'нивeдхас@abovecloud9.ai')     # Cyrillic transliteration
    TEST_EMAIL_CHINESE = os.getenv('TEST_EMAIL_CHINESE', '倪维德哈斯@abovecloud9.ai')        # Chinese phonetic transliteration
    TEST_EMAIL_JAPANESE = os.getenv('TEST_EMAIL_JAPANESE', 'ニヴェドハス@abovecloud9.ai')   # Japanese katakana transliteration
    TEST_EMAIL_ARABIC = os.getenv('TEST_EMAIL_ARABIC', 'نيفيدهاس@abovecloud9.ai')         # Arabic transliteration
    
    # Rapid Login Test Configuration
    RAPID_LOGIN_USER_COUNT = int(os.getenv('RAPID_LOGIN_USER_COUNT', 5))                   # Number of users to test
    RAPID_LOGIN_EMAIL_PATTERN = os.getenv('RAPID_LOGIN_EMAIL_PATTERN', 'autotest+{i}@abovecloud9.ai')  # Email pattern with {i} placeholder
    RAPID_LOGIN_PASSWORD_PATTERN = os.getenv('RAPID_LOGIN_PASSWORD_PATTERN', 'Admin{i}@123')  # Password pattern with {i} placeholder
    RAPID_LOGIN_TIMEOUT = int(os.getenv('RAPID_LOGIN_TIMEOUT', 300))                       # Timeout in seconds (increased for mobile)
    
    # Invalid Password Test Configuration
    INVALID_PASSWORD_USER_COUNT = int(os.getenv('INVALID_PASSWORD_USER_COUNT', 5))         # Number of invalid password attempts
    INVALID_PASSWORD_PATTERN = os.getenv('INVALID_PASSWORD_PATTERN', 'Invalid{i}@Wrong')   # Invalid password pattern
    
    @classmethod
    def get_appium_capabilities(cls):
        if cls.MOBILE_PLATFORM == 'ios':
            capabilities = {
                'platformName': cls.IOS_PLATFORM_NAME,
                'deviceName': cls.IOS_DEVICE_NAME,
                'platformVersion': cls.IOS_PLATFORM_VERSION,
                'automationName': 'XCUITest',
                'bundleId': cls.IOS_BUNDLE_ID,
                'noReset': False,
                'newCommandTimeout': 3600,
                'autoGrantPermissions': True,
                'autoAcceptAlerts': True,
                # Debug/stability options
                'showXcodeLog': True,
                'wdaLaunchTimeout': 120000,
                'wdaConnectionTimeout': 120000,
                # Additional capabilities to handle XCTestCaseImplementation error
                'useNewWDA': True,
                'wdaStartupRetries': 3,
                'wdaStartupRetryInterval': 10000,
                'useSimpleBuildTest': True,
                'skipLogCapture': False,
                'shouldUseSingletonTestManager': False,
                'shouldTerminateApp': True,
                'forceAppLaunch': True,
                # iOS 18+ compatibility
                'iosInstallPause': 8000,
                'iosDeviceReadyTimeout': 30000,
                'iosSimulatorStartupTimeout': 120000
            }
            
            if cls.IOS_UDID:
                capabilities['udid'] = cls.IOS_UDID
            if cls.IOS_XCODE_ORG_ID:
                capabilities['xcodeOrgId'] = cls.IOS_XCODE_ORG_ID
            if cls.IOS_XCODE_SIGNING_ID:
                capabilities['xcodeSigningId'] = cls.IOS_XCODE_SIGNING_ID
            if cls.IOS_APP_PATH:
                capabilities['app'] = cls.IOS_APP_PATH
                
        else:  
            capabilities = {
                'platformName': cls.ANDROID_PLATFORM_NAME,
                'deviceName': cls.ANDROID_DEVICE_NAME,
                'platformVersion': cls.ANDROID_PLATFORM_VERSION,
                'automationName': 'UiAutomator2',
                'appPackage': cls.ANDROID_APP_PACKAGE,
                'appActivity': cls.ANDROID_APP_ACTIVITY,
                'noReset': False,
                'newCommandTimeout': 3600,
                'autoGrantPermissions': True
            }
            
            if cls.ANDROID_APP_PATH:
                capabilities['app'] = cls.ANDROID_APP_PATH
                
        return capabilities 