from sqlalchemy.orm.scoping import scoped_session
from db_models.book import Book
from dtos.books.get_book_id_title_dto import GetBookIdTitleDto
from dtos.books.search_book_dto import SearchBookDto
from repositories.book_repository import BookRepository


class BookService:
    def __init__(self, scoped_session: scoped_session):
        self.book_repository = BookRepository(scoped_session)

    def find_by_title_containing(self, dto: SearchBookDto) -> list[GetBookIdTitleDto]:
        """
        Finds all books that have `title`.

        Args:
            dto (SearchBookDto): 

        Returns:
            list[Book]: List of books that have `title`.
        """
        models = self.book_repository.find_by_title_containing(
            dto.title, dto.count)
        dtos = [self.map_model_to_id_title_dto(model) for model in models]
        return dtos

    @staticmethod
    def map_model_to_id_title_dto(model: Book) -> GetBookIdTitleDto:
        return GetBookIdTitleDto(model.id, model.title)
