import hashlib
from sqlalchemy.orm.scoping import scoped_session
from repositories.user_repository import UserRepository
from dtos.auths.register_dto import RegisterDto
from dtos.auths.login_dto import LoginDto
from db_models.user import User
from flask_login import login_user
from flask_wtf.csrf import generate_csrf

class AuthError(Exception):
    def __init__(self, message: dict, code=400):
        super().__init__()
        self.message = message
        self.code = code

    def to_tuple(self) -> tuple:
        """
        Returns (`message`, `code`)
        """
        return (self.message, self.code)


class AuthService:
    def __init__(self, scoped_session: scoped_session):
        self.user_repository = UserRepository(scoped_session)

    def register(self, dto: RegisterDto) -> LoginDto:
        """
        Creates the user.
  
        Args:
            dto (CreateAuthDto): User to create.
  
        Returns:
            GetAuthDto: Updated user values after creation.

        Raises:
            AuthError: If `dto.name` already exists in the repository.
        """
        if self.user_repository.find_by_name(dto.name) is not None:
            raise AuthError(
                {"name": f'Name "{dto.name}" is already taken!'}, 400)
        model = self.map_register_dto_to_model(dto)
        model.password = self.hash_password(model.password)
        model = self.user_repository.create(model)
        login_dto = self.map_model_to_login_dto(model)
        login_dto.password = dto.password
        login_dto.remember_me = dto.remember_me
        return login_dto

    def login_user(self, dto: LoginDto) -> dict:
        """
        Logins the user.
  
        Args:
            dto (GetAuthDto): User to login.
  
        Returns:
            dict: Dictionary storing a single key named `'csrf_token`'.

        Raises:
            AuthError: If user with `dto.name` doesn't exist.
            AuthError: If hashed `dto.password` doesn't match with the user repository password.
        """
        model = self.user_repository.find_by_name(dto.name)
        if model is None:
            raise AuthError({"name": 'User doesn\'t exist!'}, 400)
        if model.password != self.hash_password(dto.password):
            raise AuthError({"password": "Incorrect password!"}, 400)
        login_user(model, remember=dto.remember_me)
        return {'csrf_token': generate_csrf()}

    @staticmethod
    def map_model_to_login_dto(model: User) -> LoginDto:
        return LoginDto(model.name, model.password, False)

    @staticmethod
    def map_register_dto_to_model(dto: RegisterDto):
        return User(name=dto.name, password=dto.password)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes `password` using sha256 and returns the hex as 64 bytes.
  
        Args:
            password (str): Password to hash.
  
        Returns:
            str: Hashed password as 64 byte hex.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
