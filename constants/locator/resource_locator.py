from appium.webdriver.common.appiumby import AppiumBy


class ResourceLocator:
    android = {
        # authentication page
        "title" : (AppiumBy.ID, "com.samsung.android.biometrics.app.setting:id/title"),
        "subtitle" : (AppiumBy.ID, "com.samsung.android.biometrics.app.setting:id/subtitle"),
        "description" : (AppiumBy.ID, "com.samsung.android.biometrics.app.setting:id/description"),
        "pin_field" : (AppiumBy.ID, "com.samsung.android.biometrics.app.setting:id/lockPassword"),
        "cancel_button" : (AppiumBy.ID, "com.samsung.android.biometrics.app.setting:id/btn_cancel"),
        "continue_button" : (AppiumBy.ID, "com.samsung.android.biometrics.app.setting:id/btn_continue"),
        "error_text" : (AppiumBy.ID, "com.samsung.android.biometrics.app.setting:id/error"),
        "resources_template" : (AppiumBy.ACCESSIBILITY_ID, 'Resources'),

        "resource_product_card": (AppiumBy.ACCESSIBILITY_ID, lambda product: f'{product}'),
        "resource_list": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]'),
        "resource_download_audio": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Download audio"]'),
        "resource_download_video": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Download video"]'),
        "resource_download_document": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Download document"]'),
        "resource_delete_audio": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Delete audio"]'),
        "resource_delete_video": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Delete video"]'),
        "resource_delete_document": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Delete document"]'),
        "resourse_pause_download_audio": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Pause/Cancel Download audio"]'),
        "resourse_pause_download_video": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Pause/Cancel Download video"]'),
        "resourse_pause_download_document": (AppiumBy.XPATH, lambda resource: f'//android.widget.Button[contains(@content-desc,"{resource}")]/android.widget.Button[@content-desc="Pause/Cancel Download document"]'),

        "download_all_button": (AppiumBy.ACCESSIBILITY_ID, 'Download All Button'),
        "close_dialog_button": (AppiumBy.ACCESSIBILITY_ID, 'Close Dialog Button'),
        "confirm_dialog_button": (AppiumBy.ACCESSIBILITY_ID, 'Confirm Dialog Button'),
        "back_button": (AppiumBy.ACCESSIBILITY_ID, 'Back Button'),

        # play page
        "resourse_title"  : (AppiumBy.ACCESSIBILITY_ID, lambda resource: f'{resource}'),
        "rewind_button" : (AppiumBy.ACCESSIBILITY_ID, 'Rewind Button'),
        "forward_button" : (AppiumBy.ACCESSIBILITY_ID, 'Forward Button'),
        "play_button" : (AppiumBy.ACCESSIBILITY_ID, 'Play Button'),
        "progress_bar" : (AppiumBy.XPATH,f'//android.widget.SeekBar[@content-desc="contains(Progress bar)"]'),
        "pause_button" : (AppiumBy.ACCESSIBILITY_ID, 'Pause Button'),
        "volume_up_button" : (AppiumBy.ACCESSIBILITY_ID, 'Volume Up Button'),
        "volume_down_button" : (AppiumBy.ACCESSIBILITY_ID, 'Volume Down Button'),
        "audio_output_button" : (AppiumBy.ACCESSIBILITY_ID, 'Audio Output Button'),
        "cancel_button" : (AppiumBy.ACCESSIBILITY_ID, 'Cancel'),
        "yes_button" : (AppiumBy.ACCESSIBILITY_ID, 'Yes'),
    }

    ios = {
    }

    @classmethod
    def get_locators(cls, platform):
        return cls.ios if platform.lower() == "ios" else cls.android
