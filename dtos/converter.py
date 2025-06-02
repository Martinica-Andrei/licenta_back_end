from dtos.helper_methods import HelperMethods
import re


class ValidationError(Exception):
    def __init__(self, message: dict, code=400):
        super().__init__()
        self.message = message
        self.code = code

    def to_tuple(self) -> tuple:
        """
        Returns (`message`, `code`).
        """
        return (self.message, self.code)


class Converter:

    @staticmethod
    def convert_bool_from_dict(body: dict, key: str) -> bool:
        """
        Validates value in `body[key]` and converts to bool if valid. Conversion is case insensitive.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            bool: The converted value as a boolean.

        Raises:
            ValidationError: If conversion fails.
        """
        value = str(body[key]).lower()
        if value not in ['true', 'false']:
            raise ValidationError(
                {key: f"* Invalid value, {key} must be 'true' or 'false'!"}, 400)
        value = (value == 'true')
        return value

    @staticmethod
    def convert_int_from_dict(body: dict, key: str) -> int:
        """
        Converts `body[key]` to int.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            int: The converted value as an integer.

        Raises:
            ValidationError: If conversion fails.
        """
        try:
            return int(body[key])
        except ValueError:
            cap_key = HelperMethods.capitalize_first_letter(key)
            raise ValidationError(
                {key: f"* {cap_key} must be an integer!"}, 400)

    @staticmethod
    def validate_int_is_in_range(body: dict, key: str, min_inclusive, max_inclusive) -> None:
        """
        Checks if `int(body[key])` is in `min_inclusive` - `max_inclusive` range.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            None.

        Raises:
            ValidationError: If value is not an integer.
            ValidationError: If integer is not in `min_inclusive` - `max_inclusive` range.
        """
        v = Converter.convert_int_from_dict(body, key)
        if v < min_inclusive or v > max_inclusive:
            cap_key = HelperMethods.capitalize_first_letter(key)
            raise ValidationError(
                {key: f"* {cap_key} must have value between {min_inclusive} and {max_inclusive}!"}, 400)

    @staticmethod
    def validate_str_len_is_in_range(body: dict, key: str, min_inclusive, max_inclusive) -> None:
        """
        Checks if `str(body[key])` is in `min_inclusive` - `max_inclusive` length range.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            None.

        Raises:
            ValidationError: If length of value is not in `min_inclusive` - `max_inclusive` length range.
        """
        length = len(str(body[key]))
        if length < min_inclusive or length > max_inclusive:
            cap_key = HelperMethods.capitalize_first_letter(key)
            raise ValidationError(
                {key: f"* {cap_key} must have length between {min_inclusive} and {max_inclusive}!"}, 400)

    @staticmethod
    def validate_is_required(body: dict, key: str) -> None:
        """
        Checks if `key` is in `body`.

        Args:
            body (dict): Dictionary that might contain `key`.
            key (str): Key to check if it is in dictionary.

        Returns:
            None.

        Raises:
            ValidationError: If `key` is not in `body`.
        """
        if key not in body:
            cap_key = HelperMethods.capitalize_first_letter(key)
            raise ValidationError({key: f"* {cap_key} is required!"}, 400)

    @staticmethod
    def validate_is_alphanumeric_underscore(body: dict, key: str) -> None:
        """
        Checks if `body[key]` only contains letters from a-zA-Z, digits 0-9 and underscore _.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            None.

        Raises:
            ValidationError: If value has `\W` regex letter.
        """
        if re.search('\W', body[key]):
            cap_key = HelperMethods.capitalize_first_letter(key)
            raise ValidationError(
                {key: f"{cap_key} can only contain alphanumerical characters and underscore!"}, 400)

    @staticmethod
    def validate_has_no_spaces(body: dict, key: str) -> None:
        """
        Checks if `body[key]` doesn't contain spaces.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            None.

        Raises:
            ValidationError: If value contains spaces, `\s` regex letter.
        """

        if re.search('\s', body[key]):
            cap_key = HelperMethods.capitalize_first_letter(key)
            raise ValidationError(
                {key: f"{cap_key} must not contain spaces!"}, 400)

    @staticmethod
    def validate_has_value_in_list(body: dict, key: str, values: set) -> None:
        """
        Checks if `body[key]` is in `values`.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.
            values (set): Set that checks if it contains `body[key]`.

        Returns:
            None.

        Raises:
            ValidationError: If `body[key]` not in `values`.
        """
        if body[key] not in values:
            cap_key = HelperMethods.capitalize_first_letter(key)
            values_str = ', '.join(values)
            raise ValidationError(
                {key: f"{cap_key} must be {values_str}!"}, 400)

    @staticmethod
    def validate_is_list(body: dict, key: str) -> None:
        """
        Checks if `body[key]` is list.

        Args:
            body (dict): Dictionary that contains `key`.
            key (str): Key to access value in `body`.

        Returns:
            None.

        Raises:
            ValidationError: If `body[key]` is not list.
        """
        if type(body[key]) is not list:
            cap_key = HelperMethods.capitalize_first_letter(key)
            raise ValidationError(
                {key: f"{cap_key} must be a list!"}, 400)