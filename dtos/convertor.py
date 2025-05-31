class Convertor:

    @staticmethod
    def convert_bool_from_dict(body: dict, key: str) -> tuple[bool, dict[str, str]]:
        """
        Validates value in `body[key]` and converts to bool if valid. Validation is case insensitive.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            If value is valid, returns tuple[true|false, None].
            Else, returns tuple[None, dict_invalid_message].
        """
        value = str(body[key]).lower()
        if value not in ['true', 'false']:
            return None, {key: f"Invalid value, {key} must be 'true' or 'false'!"}
        value = (value == 'true')
        return value, None