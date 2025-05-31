from sqlalchemy.orm.scoping import scoped_session
from db_models.author import Author
import sqlalchemy as sa


class AuthorRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

    def find_by_name_containing(self, name: str, offset: int, limit: int) -> list[Author]:
        """
        Finds all authors that have `name`.

        Args:
            name (str): Name of authors.
            offset (int): Starting row for fetching.
            limit (int): Number of authors to fetch.

        Returns:
            list[Author]: List of authors.
        """
        authors = self.scoped_session.query(Author).\
            filter(Author.name.like(f'%{name}%')).\
            order_by(sa.func.char_length(Author.name)).\
            limit(limit).offset(offset).all()
        return authors
