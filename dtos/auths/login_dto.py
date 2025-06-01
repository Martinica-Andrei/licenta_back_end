from dtos.convertor import Convertor

class LoginDto:
    def __init__(self, name: str, password: str, remember_me=False):
        self.name = name
        self.password = password
        self.remember_me = remember_me

    @staticmethod
    def convert_from_dict(body: dict) -> "LoginDto":
        """
        Converts dict to LoginDto.

        Args:
            body (dict): Dictionary to be converted.

        Returns:
            LoginDto.

        Raises:
            ValidationError: If any validation fails.
        """
        body = {k.lower(): v for k, v in body.items()}
        Convertor.validate_is_required(body, 'name')
        Convertor.validate_is_required(body, 'password')
        if 'remember_me' in body:
            remember_me = Convertor.convert_bool_from_dict(body, "remember_me")
        else:
            remember_me = False
        return LoginDto(body['name'], body['password'], remember_me)
