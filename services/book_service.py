from sqlalchemy.orm.scoping import scoped_session
from repositories.book_repository import BookRepository


class BookService:
    def __init__(self, scoped_session: scoped_session):
        self.book_repository = BookRepository(scoped_session)
