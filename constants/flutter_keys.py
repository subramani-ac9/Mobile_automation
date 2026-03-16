"""
Flutter Widget Keys Constants

This file contains all the Flutter widget keys used across the application.
Centralizing keys here makes it easier to maintain and update when the app changes.
"""

class FlutterKeys:
    """Centralized Flutter widget keys for the application"""
    
    # ============================================================================
    # ONBOARDING SCREEN KEYS
    # ============================================================================
    ONBOARDING_SCREEN = "onboarding_screen"
    ONBOARDING_LOADING_INDICATOR = "onboarding_loading_indicator"
    ONBOARDING_APP_LOGO = "onboarding_app_logo"
    ONBOARDING_WELCOME_MESSAGE = "onboarding_welcome_message"
    ONBOARDING_HOME_ICON = "onboarding_home_icon"
    ONBOARDING_TRANSFORM_LIVES = "onboarding_transform_lives"
    ONBOARDING_DESCRIPTION = "onboarding_description"
    ONBOARDING_CONTINUE_BUTTON = "onboarding_continue_button"
    
    # ============================================================================
    # LOGIN SCREEN KEYS
    # ============================================================================
    LOGIN_SCREEN = "login_screen"
    LOGIN_APP_BAR = "login_app_bar"
    LOGIN_SAFE_AREA = "login_safe_area"
    LOGIN_WEB_VIEW_HANDLER = "login_web_view_handler"
    LOGIN_LOADING_INDICATOR = "login_loading_indicator"
    LOGIN_ERROR_SECTION = "login_error_section"
    LOGIN_ERROR_ICON = "login_error_icon"
    LOGIN_ERROR_MESSAGE = "login_error_message"
    LOGIN_RETRY_BUTTON = "login_retry_button"
    LOGIN_PROCESSING_OVERLAY = "login_processing_overlay"
    LOGIN_FORM_CONTAINER = "login_form_container"
    LOGIN_APP_LOGO = "login_app_logo"
    LOGIN_FORM_TITLE = "login_form_title"
    LOGIN_AUTH_FORM = "login_auth_form"
    LOGIN_COUNTRY_SELECTOR = "login_country_selector"
    LOGIN_FORGOT_PASSWORD_BUTTON = "login_forgot_password_button"
    LOGIN_REGISTER_BUTTON = "login_register_button"
    LOGIN_LINK_BUTTON = "login_link_button"
    
    # Login form input fields (need to be added to Flutter app)
    LOGIN_EMAIL_INPUT = "login_email_input"
    LOGIN_PASSWORD_INPUT = "login_password_input"
    LOGIN_SUBMIT_BUTTON = "login_submit_button"
    
    # ============================================================================
    # FORGOT PASSWORD SCREEN KEYS
    # ============================================================================
    FORGOT_PASSWORD_APP_BAR = "forgot_password_app_bar"
    FORGOT_PASSWORD_BODY = "forgot_password_body"
    FORGOT_PASSWORD_SAFE_AREA = "forgot_password_safe_area"
    FORGOT_PASSWORD_CENTER = "forgot_password_center"
    FORGOT_PASSWORD_SINGLE_CHILD_SCROLL_VIEW = "forgot_password_single_child_scroll_view"
    FORGOT_PASSWORD_COLUMN = "forgot_password_column"
    FORGOT_PASSWORD_LOGO = "forgot_password_logo"
    FORGOT_PASSWORD_TITLE = "forgot_password_title"
    FORGOT_PASSWORD_DESCRIPTION = "forgot_password_description"
    FORGOT_PASSWORD_AUTH_FORM = "forgot_password_auth_form"
    FORGOT_PASSWORD_PREVIOUS_BUTTON = "forgot_password_previous_button"
    FORGOT_PASSWORD_REMEMBER_PASSWORD_TEXT = "forgot_password_remember_password_text"
    FORGOT_PASSWORD_BACK_TO_LOGIN_BUTTON = "forgot_password_back_to_login_button"
    FORGOT_PASSWORD_LOADING_OVERLAY = "forgot_password_loading_overlay"
    
    # Forgot password form fields (need to be added to Flutter app)
    FORGOT_PASSWORD_EMAIL_INPUT = "forgot_password_email_input"
    FORGOT_PASSWORD_SUBMIT_BUTTON = "forgot_password_submit_button"
    FORGOT_PASSWORD_SUCCESS_MESSAGE = "forgot_password_success_message"
    
    # ============================================================================
    # REGISTRATION SCREEN KEYS
    # ============================================================================
    REGISTRATION_SCAFFOLD = "registration_scaffold"
    REGISTRATION_APP_BAR = "registration_app_bar"
    REGISTRATION_SAFE_AREA = "registration_safe_area"
    REGISTRATION_CENTER = "registration_center"
    REGISTRATION_COLUMN = "registration_column"
    REGISTRATION_LOGO = "registration_logo"
    REGISTRATION_TITLE = "registration_title"
    REGISTRATION_DESCRIPTION = "registration_description"
    REGISTRATION_AUTH_FORM = "registration_auth_form"
    REGISTRATION_ADDITIONAL_CONTENT = "registration_additional_content"
    REGISTRATION_PREVIOUS_BUTTON = "registration_previous_button"
    REGISTRATION_SKIP_BUTTON = "registration_skip_button"
    REGISTRATION_SIGN_IN_BUTTON = "registration_sign_in_button"
    
    # ============================================================================
    # MAIN SCREEN / DASHBOARD KEYS
    # ============================================================================
    MAIN_SCREEN = "main_screen"
    MAIN_SCREEN_CONTENT = "main_screen_content"
    MAIN_BOTTOM_NAVIGATION = "main_bottom_navigation"
    
    # ============================================================================
    # BOTTOM NAVIGATION KEYS
    # ============================================================================
    BOTTOM_NAVIGATION_CONTAINER = "bottom_navigation_container"
    NAV_LIVE_DARSHAN = "nav_live_darshan"
    NAV_EVENTS = "nav_events"
    NAV_RESOURCES = "nav_resources"
    NAV_ACCOUNT = "nav_account"
    
    # ============================================================================
    # EVENTS SCREEN KEYS
    # ============================================================================
    EVENTS_SCREEN = "events_screen"
    EVENTS_CONTENT = "events_content"
    EVENTS_APP_BAR = "events_app_bar"
    EVENTS_SCREEN_TITLE = "events_screen_title"
    EVENTS_ADD_BUTTON = "events_add_button"
    EVENTS_TAB_BAR = "events_tab_bar"
    EVENTS_REFRESH_INDICATOR = "events_refresh_indicator"
    EVENTS_LIST_VIEW = "events_list_view"
    
    # Event items (dynamic keys with patterns)
    EVENTS_SECTION_TITLE_PATTERN = "events_section_title_$title"
    EVENT_ITEM_PATTERN = "event_item_${event.id}"
    EVENT_NAME_PATTERN = "event_name_$name"
    EVENT_TIME_PATTERN = "event_time_$name"
    EVENT_ATTENDEES_PATTERN = "event_attendees_$name"
    
    # ============================================================================
    # RESOURCES SCREEN KEYS (for course listing)
    # ============================================================================
    RESOURCES_SCREEN = "resources_screen"
    RESOURCES_CONTENT = "resources_content"
    RESOURCES_APP_BAR = "resources_app_bar"
    RESOURCES_SCREEN_TITLE = "resources_screen_title"
    RESOURCES_TAB_BAR = "resources_tab_bar"
    RESOURCES_LIST_VIEW = "resources_list_view"
    
    # ============================================================================
    # COURSE LISTING KEYS (need to be added to Flutter app)
    # ============================================================================
    COURSE_LIST = "course_list"
    COURSE_ITEM = "course_item"
    COURSE_TITLE = "course_title"
    COURSE_DESCRIPTION = "course_description"
    COURSE_IMAGE = "course_image"
    COURSE_LOADING = "course_loading"
    COURSE_EMPTY_STATE = "course_empty_state"
    COURSE_DETAIL_BACK_BUTTON = "course_detail_back_button"
    COURSE_DETAIL_TITLE = "course_detail_title"
    COURSE_DETAIL_CONTENT = "course_detail_content"
    
    # ============================================================================
    # ACCOUNT SCREEN KEYS (need to be added to Flutter app)
    # ============================================================================
    ACCOUNT_SCREEN = "account_screen"
    ACCOUNT_CONTENT = "account_content"
    ACCOUNT_APP_BAR = "account_app_bar"
    ACCOUNT_SCREEN_TITLE = "account_screen_title"
    ACCOUNT_USER_INFO = "account_user_info"
    ACCOUNT_LOGOUT_BUTTON = "account_logout_button"
    ACCOUNT_SETTINGS_BUTTON = "account_settings_button"
    
    # ============================================================================
    # LIVE DARSHAN SCREEN KEYS (need to be added to Flutter app)
    # ============================================================================
    LIVE_DARSHAN_SCREEN = "live_darshan_screen"
    LIVE_DARSHAN_CONTENT = "live_darshan_content"
    LIVE_DARSHAN_APP_BAR = "live_darshan_app_bar"
    LIVE_DARSHAN_SCREEN_TITLE = "live_darshan_screen_title"
    LIVE_DARSHAN_VIDEO_PLAYER = "live_darshan_video_player"
    LIVE_DARSHAN_PLAY_BUTTON = "live_darshan_play_button"
    LIVE_DARSHAN_PAUSE_BUTTON = "live_darshan_pause_button"
    
    # ============================================================================
    # COMMON UI ELEMENTS
    # ============================================================================
    LOADING_INDICATOR = "loading_indicator"
    ERROR_MESSAGE = "error_message"
    SUCCESS_MESSAGE = "success_message"
    RETRY_BUTTON = "retry_button"
    BACK_BUTTON = "back_button"
    CLOSE_BUTTON = "close_button"
    CONFIRM_BUTTON = "confirm_button"
    CANCEL_BUTTON = "cancel_button"
    
    # ============================================================================
    # UTILITY METHODS FOR DYNAMIC KEYS
    # ============================================================================
    
    @staticmethod
    def get_events_section_title(title):
        """Get events section title key with dynamic title"""
        return f"events_section_title_{title}"
    
    @staticmethod
    def get_event_item(event_id):
        """Get event item key with dynamic event ID"""
        return f"event_item_{event_id}"
    
    @staticmethod
    def get_event_name(name):
        """Get event name key with dynamic name"""
        return f"event_name_{name}"
    
    @staticmethod
    def get_event_time(name):
        """Get event time key with dynamic name"""
        return f"event_time_{name}"
    
    @staticmethod
    def get_event_attendees(name):
        """Get event attendees key with dynamic name"""
        return f"event_attendees_{name}"
    
    # ============================================================================
    # KEY GROUPS FOR EASY ACCESS
    # ============================================================================
    
    @classmethod
    def get_login_keys(cls):
        """Get all login-related keys"""
        return {
            'screen': cls.LOGIN_SCREEN,
            'app_bar': cls.LOGIN_APP_BAR,
            'auth_form': cls.LOGIN_AUTH_FORM,
            'email_input': cls.LOGIN_EMAIL_INPUT,
            'password_input': cls.LOGIN_PASSWORD_INPUT,
            'submit_button': cls.LOGIN_SUBMIT_BUTTON,
            'forgot_password_button': cls.LOGIN_FORGOT_PASSWORD_BUTTON,
            'error_message': cls.LOGIN_ERROR_MESSAGE,
            'loading_indicator': cls.LOGIN_LOADING_INDICATOR,
            'processing_overlay': cls.LOGIN_PROCESSING_OVERLAY
        }
    
    @classmethod
    def get_forgot_password_keys(cls):
        """Get all forgot password-related keys"""
        return {
            'app_bar': cls.FORGOT_PASSWORD_APP_BAR,
            'auth_form': cls.FORGOT_PASSWORD_AUTH_FORM,
            'email_input': cls.FORGOT_PASSWORD_EMAIL_INPUT,
            'submit_button': cls.FORGOT_PASSWORD_SUBMIT_BUTTON,
            'success_message': cls.FORGOT_PASSWORD_SUCCESS_MESSAGE,
            'back_button': cls.FORGOT_PASSWORD_BACK_TO_LOGIN_BUTTON,
            'loading_overlay': cls.FORGOT_PASSWORD_LOADING_OVERLAY
        }
    
    @classmethod
    def get_navigation_keys(cls):
        """Get all navigation-related keys"""
        return {
            'bottom_navigation': cls.MAIN_BOTTOM_NAVIGATION,
            'live_darshan': cls.NAV_LIVE_DARSHAN,
            'events': cls.NAV_EVENTS,
            'resources': cls.NAV_RESOURCES,
            'account': cls.NAV_ACCOUNT
        }
    
    @classmethod
    def get_course_keys(cls):
        """Get all course-related keys"""
        return {
            'list': cls.COURSE_LIST,
            'item': cls.COURSE_ITEM,
            'title': cls.COURSE_TITLE,
            'description': cls.COURSE_DESCRIPTION,
            'image': cls.COURSE_IMAGE,
            'loading': cls.COURSE_LOADING,
            'empty_state': cls.COURSE_EMPTY_STATE,
            'detail_back_button': cls.COURSE_DETAIL_BACK_BUTTON,
            'detail_title': cls.COURSE_DETAIL_TITLE
        }
    
    @classmethod
    def get_event_keys(cls):
        """Get all event-related keys"""
        return {
            'screen': cls.EVENTS_SCREEN,
            'list_view': cls.EVENTS_LIST_VIEW,
            'add_button': cls.EVENTS_ADD_BUTTON,
            'screen_title': cls.EVENTS_SCREEN_TITLE,
            'refresh_indicator': cls.EVENTS_REFRESH_INDICATOR
        } 