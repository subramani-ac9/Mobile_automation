class AddressMessage:

    message = {

        "address_success_msg": "Address saved successfully",
        "3_characterlength_error_msg": "Must be above 3 characters",
        "5_characterlength_error_msg": "Must be above 5 characters",
        "zipcode_error_msg": "Enter a valid 5-digit ZIP code",
        "address_delete_success_msg": "Address deleted successfully",
    }

    @classmethod
    def get_message(cls):
        return AddressMessage.message