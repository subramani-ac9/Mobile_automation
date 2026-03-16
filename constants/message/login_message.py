class LoginMessage:
    message = {
        "invalid_username" : "User not found. Please create an account.",
        "invalid_password" : "Password is incorrect.",
        "incorrect_username_or_password": "Incorrect username or password.",
        "invalid_credentials": "Invalid credentials. Please try again.",
        "error_occurred": "An error occurred. Please try again.",
        "empty_email_msg": "Please enter your username",
        "empty_pass_msg": "Please enter your password",
        "valid_email_msg": "Please enter a valid email address",
        "valid_pass_msg": "Password must be at least 6 characters",
        "network_error": "Network error. Please check your connection.",
        "server_error": "Server error. Please try again later.",
    }
    
    @classmethod
    def get_message(cls):
        return LoginMessage.message
    
    @classmethod
    def get_error_message(cls, error_type):
        """Get specific error message by type"""
        return cls.message.get(error_type, cls.message["error_occurred"])
    
    @classmethod
    def get_all_error_messages(cls):
        """Get all possible error messages for validation"""
        return list(cls.message.values())
    
    @classmethod
    def validate_error_message(cls, actual_message):
        """Check if actual message matches any expected error message"""
        expected_messages = cls.get_all_error_messages()
        return any(expected in actual_message for expected in expected_messages)