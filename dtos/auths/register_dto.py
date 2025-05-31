import re

class RegisterDto:
    def __init__(self, name: str, password: str):
        self.name = name
        self.password = password

    @staticmethod
    def validate(body: dict) -> tuple["RegisterDto", dict]:
        body = {k.lower(): v for k, v in body.items()}
        if 'name' not in body:
            return None, {"name": "Name is required!"}
        name = body['name']
        if len(name) == 0 or len(name) > 50:
            return None, {"name": "Name must have a length between 1 and 50!"}
        if re.search('\W', name):
            return None, {"name": "Name can only contain alphanumerical characters and underscore!"}
        if 'password' not in body:
            return None,{"password": "Password is required!"}
        password = body['password']
        if len(password) == 0 or len(password) > 30:
            return None, {"password": "Password must have a length between 1 and 30"}
        if re.search(r'\s', password):
            return None, {"password": "Password must not contain spaces!"}
        return RegisterDto(name, password), None
