from sqlalchemy.orm.scoping import scoped_session
from repositories.book_rating_repository import BookRatingRepository


class BookRatingService:
    def __init__(self, scoped_session: scoped_session):
        self.book_rating_repository = BookRatingRepository(scoped_session)
