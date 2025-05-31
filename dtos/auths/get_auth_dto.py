class GetAuthDto:
    def __init__(self, name: str, password: str):
        self.name = name
        self.password = password

    @staticmethod
    def validate(body: dict) -> tuple["GetAuthDto", dict]:
        body = {k.lower(): v for k, v in body.items()}
        if 'name' not in body:
            return None, {"name": "Name is required!"}
        if 'password' not in body:
            return None, {"password": "Password is required!"}
        return GetAuthDto(body['name'], body['password']), None
