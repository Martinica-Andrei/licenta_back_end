from sqlalchemy.orm.scoping import scoped_session
from db_models.user import User

class UserRepository:
    def __init__(self, scoped_session : scoped_session):
        self.scoped_session = scoped_session

    def find_by_name(self, name : str) -> User:
        user = self.scoped_session.query(User).where(User.name == name).first()
        return user;

    def create(self, model : User) -> User:
        self.scoped_session.add(model)
        self.scoped_session.commit()
        return model