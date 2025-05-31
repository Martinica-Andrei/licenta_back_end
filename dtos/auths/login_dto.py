from dtos.convertor import Convertor

class LoginDto:
    def __init__(self, name: str, password: str, remember_me=False):
        self.name = name
        self.password = password
        self.remember_me = remember_me

    @staticmethod
    def convert_from_dict(body: dict) -> tuple["LoginDto", dict]:
        body = {k.lower(): v for k, v in body.items()}
        if 'name' not in body:
            return None, {"name": "Name is required!"}
        if 'password' not in body:
            return None, {"password": "Password is required!"}
        remember_me, invalid_message = Convertor.convert_bool_from_dict(body, "remember_me")
        if remember_me is None:
            return None, invalid_message
        return LoginDto(body['name'], body['password'], remember_me), None
