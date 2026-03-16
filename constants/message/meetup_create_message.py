class MeetupCreateMsg:

    message = {

        "date_err_msg1": "Out of range.",
        "date_err_msg2": "Start time must be in the future",
        "time_err_msg": 'Start time and end time must be on the same day',
        "meetup_create_success_msg": "Your event creation is in progress.",
        "max_attendees_zero_msg": "Please enter a valid input",
        "teacher_conflict_msg": 'Teacher schedule conflicts with existing events',
        "product_error_msg": 'Please select a product',
        "max_attendees_exceed_err_msg": lambda val1: f'Max attendees for this event should be less than {val1}',
        "contact_err_msg": 'Please select a contact person',
        "center_err_msg": "Please select a Aol Center",
        "state_err_msg": 'Please select a state',
        "timezone_err_msg": 'Please select a Timezone',
        "common_err": "Please enter a valid input",
        "url_err_msg": "Please enter a valid meeting url",
        "min_char_err_msg":lambda val: f"Must be above {val} characters",
        "min_char_zipcode_err": lambda val: f"Must be {val} digits"
    }

    @classmethod
    def get_meetup_create_message(cls):
        return MeetupCreateMsg.message