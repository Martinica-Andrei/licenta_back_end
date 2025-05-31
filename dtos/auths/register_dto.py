import re

from dtos.convertor import Convertor

class RegisterDto:
    def __init__(self, name: str, password: str, remember_me=False):
        self.name = name
        self.password = password
        self.remember_me = remember_me

    @staticmethod
    def convert_from_dict(body: dict) -> tuple["RegisterDto", dict[str, str]]:
        """
        Converts dict to RegisterDto.

        Args:
            body (dict): Dictionary to be converted.

        Returns:
            If valid returns (RegisterDto, None) otherwise returns (None, dict_invalid_message).
        """
        body = {k.lower(): v for k, v in body.items()}
        if 'name' not in body:
            return None, {"name": "Name is required!"}
        name = body['name']
        if len(name) == 0 or len(name) > 50:
            return None, {"name": "Name must have a length between 1 and 50!"}
        if re.search('\W', name):
            return None, {"name": "Name can only contain alphanumerical characters and underscore!"}
        if 'password' not in body:
            return None, {"password": "Password is required!"}
        password = body['password']
        if len(password) == 0 or len(password) > 30:
            return None, {"password": "Password must have a length between 1 and 30"}
        if re.search(r'\s', password):
            return None, {"password": "Password must not contain spaces!"}
        remember_me, invalid_message = Convertor.convert_bool_from_dict(body, "remember_me")
        if remember_me is None:
            return None, invalid_message
        return RegisterDto(name, password, remember_me), None
