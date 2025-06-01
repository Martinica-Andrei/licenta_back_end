import hashlib
from sqlalchemy.orm.scoping import scoped_session
from repositories.user_repository import UserRepository
from dtos.users.get_user_dto import GetUserDto
from db_models.user import User

class UserService:
    def __init__(self, scoped_session: scoped_session):
        self.user_repository = UserRepository(scoped_session)

    def find_by_name(self, name: str) -> GetUserDto | None:
        """
        Finds user by name.
  
        Args:
            name (str): Name of user.
  
        Returns:
            GetUserDto | None
        """
        model = self.user_repository.find_by_name(name)
        if model is not None:
            return self.map_to_dto(model)
        return None

    @staticmethod
    def map_to_dto(model: User) -> GetUserDto:
        return GetUserDto(model.name, model.password)

    @staticmethod
    def map_to_model_from_get(dto: GetUserDto):
        return User(name=dto.name, password=dto.password)
