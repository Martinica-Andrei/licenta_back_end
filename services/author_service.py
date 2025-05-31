import hashlib
from sqlalchemy.orm.scoping import scoped_session
from db_models.author import Author
from dtos.authors.get_author_dto import GetAuthorDto
from repositories.author_repository import AuthorRepository

class AuthorService:
    def __init__(self, scoped_session: scoped_session):
        self.author_repository = AuthorRepository(scoped_session)

    def find_by_name_containing(self, name: str, offset: int, limit: int) -> list[GetAuthorDto]:
        """
        Finds all authors that have `name`.

        Args:
            name (str): Name of authors.
            offset (int): Starting row for fetching.
            limit (int): Number of authors to fetch.

        Returns:
            list[GetAuthorDto]: List of authors.
        """
        models = self.author_repository.find_by_name_containing(name, offset, limit)
        dtos = [self.map_to_dto(model) for model in models]
        return dtos

    @staticmethod
    def map_to_dto(model: Author) -> GetAuthorDto:
        return GetAuthorDto(model.id, model.name)