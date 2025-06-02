from sqlalchemy.orm.scoping import scoped_session
from db_models.book import Book
from db_models.book_rating import BookRating
from db_models.user import User
from sqlalchemy.orm import selectinload, with_loader_criteria


class UserRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

    def find_by_name(self, name: str) -> User | None:
        """
        Finds user by name.

        Args:
            name (str): Name of user.

        Returns:
            User | None
        """
        user = self.scoped_session.query(User).where(User.name == name).first()
        return user

    def create(self, model: User) -> User:
        """
        Creates user in db.

        Args:
            model (User): Model to create.

        Returns:
            User: Updated model from db.
        """
        self.scoped_session.add(model)
        self.scoped_session.commit()
        return model

    def find_by_id_with_book_rating(self, id: int) -> User | None:
        """
        Finds user by id with books that he rated.

        Args:
            id (int): User id.

        Returns:
            GetUserDto | None
        """
        model = self.scoped_session.query(User).where(User.id == id).\
            options(selectinload(User.book_ratings).selectinload(BookRating.book)).first()
        return model
