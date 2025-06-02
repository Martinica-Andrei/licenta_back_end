from sqlalchemy.orm.scoping import scoped_session
from db_models.book_rating import BookRating
from dtos.book_ratings.post_book_rating_dto import PostBookRatingDto
from repositories.book_rating_repository import BookRatingRepository
from repositories.book_repository import BookRepository


class BookRecommenderError(Exception):
    def __init__(self, message: dict, code=400):
        super().__init__()
        self.message = message
        self.code = code

    def to_tuple(self) -> tuple:
        """
        Returns (`message`, `code`).
        """
        return (self.message, self.code)


class BookRecommenderService:
    def __init__(self, scoped_session: scoped_session):
        self.book_repository = BookRepository(scoped_session)

    