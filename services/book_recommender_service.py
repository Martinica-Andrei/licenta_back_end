from sqlalchemy.orm.scoping import scoped_session
from db_models.book import Book
from dtos.book_recommenders.by_id_dto import ByIdDto
from dtos.book_recommenders.get_book_dto import GetBookDto
from dtos.book_recommenders.by_content_dto import ByContentDto
from repositories.book_image_repository import BookImageRepository
from repositories.book_recommender_repository import BookRecommenderRepository
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

    def get_recommendations_by_id(self, dto: ByIdDto) -> list[GetBookDto]:
        """
        Gets book recommendations by id.

        Args:
            dto (ByIdDto).

        Returns:
            list[GetBookDto].

        Raises:
            BookRecommenderError: If `dto.book_id` doesn't exist.
        """
        ids = BookRecommenderRepository.find_nearest_neighbors_by_id(dto.book_id)
        if ids is None:
            raise BookRecommenderError({'id' : f"* Book with id {dto.book_id} doesn't exist"}, 400)
        if dto.user_id is not None:
            models = self.book_repository.find_by_ids_with_categories_authors_rating(ids, dto.user_id)
        else:
            models = self.book_repository.find_by_ids_with_categories_authors(ids)
        dtos = [self.map_model_to_get_dto(model) for model in models]
        return dtos
    
    def get_recommendations_by_content(self, dto: ByContentDto) -> list[GetBookDto]:
        """
        Gets book recommendations by content.

        Args:
            dto (ByContentDto).

        Returns:
            list[GetBookDto].
        """
        ids = BookRecommenderRepository.get_nearest_neighbors_by_content(dto.content, dto.categories, dto.authors)
        if dto.user_id is not None:
            models = self.book_repository.find_by_ids_with_categories_authors_rating(ids, dto.user_id)
        else:
            models = self.book_repository.find_by_ids_with_categories_authors(ids)
        dtos = [self.map_model_to_get_dto(model) for model in models]
        return dtos
    
    @staticmethod
    def map_model_to_get_dto(model : Book) -> GetBookDto:
        image = BookImageRepository.convert_image_base64(model.image_link)
        rating = model.ratings[0].rating if len(model.ratings) > 0 else None
        categories = [category.name for category in model.categories]
        authors = {author.author.name : author.role for author in model.authors}

        return GetBookDto(model.id,
                          model.title,
                          model.description,
                          model.link,
                          image,
                          model.nr_likes,
                          model.nr_dislikes,
                          categories,
                          authors,
                          rating
                          )