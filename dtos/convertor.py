from dtos.helper_methods import HelperMethods


class Convertor:

    @staticmethod
    def convert_bool_from_dict(body: dict, key: str) -> tuple[bool, dict[str, str]]:
        """
        Validates value in `body[key]` and converts to bool if valid. Conversion is case insensitive.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            If value is valid, returns `tuple[true|false, None]`.
            Else, returns `tuple[None, dict_invalid_message]`.
        """
        value = str(body[key]).lower()
        if value not in ['true', 'false']:
            return None, {key: f"* Invalid value, {key} must be 'true' or 'false'!"}
        value = (value == 'true')
        return value, None
    
    @staticmethod
    def convert_int_from_dict(body: dict, key: str) -> tuple[int, dict[str, str]]:
        """
        Converts `body[key]` to int.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            If value can be converted into an integer, returns `tuple[int(body[key]), None]`.
            Else, returns `tuple[None, dict_invalid_message]`.
        """
        try:
            return int(body[key]), None
        except ValueError:
            cap_key = HelperMethods.capitalize_first_letter(key)
            return None, {key: f"* {cap_key} must be an integer!"}
        
    @staticmethod
    def validate_int_is_in_range(body: dict, key: str, min_inclusive, max_inclusive) -> dict[str, str] | bool:
        """
        Checks if `int(body[key])` is in `min_inclusive` - `max_inclusive` range.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            If value is in range returns `True`, otherwise returns dict with error message.
        """
        v = int(body[key])
        if v >= min_inclusive and v <= max_inclusive:
            return True
        else:
            cap_key = HelperMethods.capitalize_first_letter(key)
            return {key: f"* {cap_key} must have value between {min_inclusive} and {max_inclusive}!"}
        
    @staticmethod
    def validate_str_len_is_in_range(body: dict, key: str, min_inclusive, max_inclusive) -> dict[str, str] | bool:
        """
        Checks if `str(body[key])` is in `min_inclusive` - `max_inclusive` length range.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            If length of string is in range returns `True`, otherwise returns dict with error message.
        """
        length = len(str(body[key]))
        if length >= min_inclusive and length <= max_inclusive:
            return True
        else:
            cap_key = HelperMethods.capitalize_first_letter(key)
            return {key: f"* {cap_key} must have length between {min_inclusive} and {max_inclusive}!"}
    
    @staticmethod
    def validate_is_required(body: dict, key: str) -> dict[str, str] | bool:
        """
        Checks if `key` is in `body`.

        Args:
            body (dict): Dictionary that might contain `key`.
            key (str): Key to check if it is in dictionary

        Returns:
            If valid, returns `True`, otherwise returns a dictionary with a message.
        """
        if key in dict:
            return True
        else:
            cap_key = HelperMethods.capitalize_first_letter(key)
            return {key: f"* {cap_key} is required!"}