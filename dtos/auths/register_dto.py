import re

from dtos.convertor import Convertor

class RegisterDto:
    def __init__(self, name: str, password: str, remember_me=False):
        self.name = name
        self.password = password
        self.remember_me = remember_me

    @staticmethod
    def convert_from_dict(body: dict) -> "RegisterDto":
        """
        Converts dict to RegisterDto.

        Args:
            body (dict): Dictionary to be converted.

        Returns:
            RegisterDto.

        Raises:
            ValidationError: If any validation fails.
        """
        body = {k.lower(): v for k, v in body.items()}
        Convertor.validate_is_required(body, 'name')
        Convertor.validate_str_len_is_in_range(body, 'name', 1, 50)
        Convertor.validate_is_alphanumeric_underscore(body, 'name')
        
        Convertor.validate_is_required(body, 'password')
        Convertor.validate_str_len_is_in_range(body, 'password', 1, 30)
        Convertor.validate_has_no_spaces(body, 'password')

        if 'remember_me' in body:
            remember_me = Convertor.convert_bool_from_dict(body, "remember_me")
        else:
            remember_me = False

        return RegisterDto(body['name'], body['password'], remember_me)
