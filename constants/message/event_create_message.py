class EventCreateMessage:
    message = {

        "date_err_msg1": "Out of range.",
        "date_err_msg2": "Start time must be in the future",
        "course_create_success_msg": "Your event creation is in progress.",
        "course_cancel_success_msg": "This event is canceled",
        "course_edit_success_msg": "Your event update is in progress.",
        "max_attendees_zero_msg": "Please enter a valid input",
        "teacher_conflict_msg": 'Teacher schedule conflicts with existing events',
        "product_error_msg": 'Please select a product',
        "max_attendees_exceed_err_msg": lambda val1: f'Max attendees for this event should be less than {val1}',
        "contact_err_msg": 'Please select a contact person',
        "center_err_msg": "Please select a Aol Center",
        "state_err_msg": 'Please select a state',
        "timezone_err_msg": 'Please select a Timezone',
        "past_date_msg": "Start time must be in the future",
        "out_of_range_err_msg": "Out of range.",
        "date_invalid_err_msg": "invalid format",
        "teacher_required_err_msg": "Please select a teacher",
        "invalid_attendee_count_msg": "Please enter a valid attendee count",

        #search messages
        "program_not_found_msg": "No programs found",
        "event_not_found_msg": "No events found",
    }

    @classmethod
    def get_message(cls):
        return EventCreateMessage.message