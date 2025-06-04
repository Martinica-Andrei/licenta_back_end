import pandas as pd
from sqlalchemy.orm.scoping import scoped_session
from db_models.book import Book
from dtos.book_recommenders.by_id_dto import ByIdDto
from dtos.book_recommenders.get_book_dto import GetBookDto
from dtos.book_recommenders.by_content_dto import ByContentDto
from dtos.book_recommenders.training_status_dto import TrainingStatusDto, TrainingStatus
from repositories.book_image_repository import BookImageRepository
from repositories.book_recommender_repository import BookRecommenderRepository
from repositories.book_repository import BookRepository
from repositories.user_repository import UserRepository
from scipy.sparse import csr_matrix

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

    # User must have minimum book ratings to train for personalized recommendations.
    MINIMUM_POSITIVE_RATINGS = 1

    def __init__(self, scoped_session: scoped_session):
        self.book_repository = BookRepository(scoped_session)
        self.user_repository = UserRepository(scoped_session)
        # Also uses:
        # LightfmRepository
        # BookRecommenderRepository

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
        ids = BookRecommenderRepository.find_nearest_neighbors_by_id(
            dto.book_id)
        if ids is None:
            raise BookRecommenderError(
                {'id': f"* Book with id {dto.book_id} doesn't exist"}, 400)
        if dto.user_id is not None:
            models = self.book_repository.find_by_ids_with_categories_authors_rating(
                ids, dto.user_id)
        else:
            models = self.book_repository.find_by_ids_with_categories_authors(
                ids)
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
        ids = BookRecommenderRepository.get_nearest_neighbors_by_content(
            dto.content, dto.categories, dto.authors)
        if dto.user_id is not None:
            models = self.book_repository.find_by_ids_with_categories_authors_rating(
                ids, dto.user_id)
        else:
            models = self.book_repository.find_by_ids_with_categories_authors(
                ids)
        dtos = [self.map_model_to_get_dto(model) for model in models]
        return dtos
    
    def validate_training_status(self, user_id: int) -> TrainingStatusDto:
        """
        Validates training status.

        Args:
            user_id (id): User id.

        Returns:
            TrainingStatusDto.
        """

        positive_book_ratings = self.user_repository.find_liked_books(user_id)
        if len(positive_book_ratings) < self.MINIMUM_POSITIVE_RATINGS:
            message = f"Minimum {self.MINIMUM_POSITIVE_RATINGS} positive ratings are required for recommendations. Like" +\
                      f"{self.MINIMUM_POSITIVE_RATINGS - len(positive_book_ratings)} more books."
            return TrainingStatusDto(TrainingStatus.CANNOT_TRAIN, message)
        book_ids = [x.id for x in positive_book_ratings]
        # with books_model_memory_change_lock.gen_rlock():
        #     if LightfmRepository.is_user_added(user_id) == False:
        #         return {"must_train": True}
        #     y = convert_positive_book_ratings_to_csr(
        #         positive_book_ratings, get_nr_users(), user_id)
        #     user_feature = create_single_user_feature(user_id)
        #     user_features_ = user_features()
        #     user_features_[user_id] = user_feature[0]
        #     precision = compute_user_precision(
        #         model, len(positive_book_ratings), y, item_features=item_features(), user_features=user_features_)
        # if precision < 0.2:
        #     return {"must_train": True}
        # if precision < TARGET_PRECISION:
        #     return {"can_train": True}
        # else:
        #     return {"can_train": False}

    
    def __get_user_categories(self, user_id : int) -> csr_matrix:
        """
        Gets user liked categories as single row csr_matrix with all categories as columns 
        where the user's liked categories have value 1 and others 0.

        Args:
            user_id (int): User id to fetch and transform categories to csr_matrix.

        Returns:
            csr_matrix.
        """
        categories = self.user_repository.find_liked_categories(user_id)
        return BookRecommenderRepository.transform_categories(categories)

    @staticmethod
    def map_model_to_get_dto(model: Book) -> GetBookDto:
        image = BookImageRepository.convert_image_base64(model.image_link)
        rating = model.ratings[0].rating if len(model.ratings) > 0 else None
        categories = [category.name for category in model.categories]
        authors = {author.author.name: author.role for author in model.authors}

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
