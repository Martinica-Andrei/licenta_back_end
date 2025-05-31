import hashlib
from sqlalchemy.orm.scoping import scoped_session
from repositories.user_repository import UserRepository
from dtos.auths.create_auth_dto import CreateAuthDto
from dtos.auths.get_auth_dto import GetAuthDto
from db_models.user import User
from flask_login import login_user, logout_user
from flask_wtf.csrf import generate_csrf

from services.user_service import UserService


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

    def get_user_by_name(self, name: str) -> GetAuthDto:
        """
        Gets user by name.
  
        Args:
            name (str): Name of user.
  
        Returns:
            GetAuthDto
        """
        model = self.user_repository.get_user_by_name(name)
        if model is not None:
            return self.map_to_dto(model)
        return None

    def create_user(self, dto: CreateAuthDto) -> GetAuthDto:
        """
        Creates the user.
  
        Args:
            dto (CreateAuthDto): User to create.
  
        Returns:
            GetAuthDto: Updated user values after creation.

        Raises:
            AuthError: If `dto.name` already exists in the repository.
        """
        if self.get_user_by_name(dto.name) is not None:
            raise AuthError(
                {"name": f'Name "{dto.name}" is already taken!'}, 400)
        model = self.map_to_model_from_create(dto)
        model.password = self.hash_password(model.password)
        model = self.user_repository.create_user(model)
        return self.map_to_dto(model)

    def login_user(self, dto: GetAuthDto) -> dict:
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
        existing_model = self.get_user_by_name(dto.name)
        if existing_model is None:
            raise AuthError({"name": 'User doesn\'t exist!'}, 400)
        if existing_model.password != self.hash_password(dto.password):
            raise AuthError({"password": "Incorrect password!"}, 400)
        model = self.map_to_model_from_get(dto)
        login_user(model)
        return {'csrf_token': generate_csrf()}

    @staticmethod
    def map_to_dto(model: User) -> GetAuthDto:
        return GetAuthDto(model.name, model.password)

    @staticmethod
    def map_to_model_from_create(dto: CreateAuthDto):
        return User(name=dto.name, password=dto.password)

    @staticmethod
    def map_to_model_from_get(dto: GetAuthDto):
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
