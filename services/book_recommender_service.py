from lightfm import LightFM
from sqlalchemy.orm.scoping import scoped_session
from custom_precision_at_k import custom_precision_at_k
from db_models.book import Book
from dtos.book_recommenders.by_id_dto import ByIdDto
from dtos.book_recommenders.get_book_dto import GetBookDto
from dtos.book_recommenders.by_content_dto import ByContentDto
from dtos.book_recommenders.training_status_dto import TrainingStatus, TrainingStatusDto
from repositories.book_image_repository import BookImageRepository
from repositories.book_repository import BookRepository
from repositories.item_features_repository import ItemFeaturesRepository
from repositories.lightfm_repository import LightfmRepository
from repositories.user_repository import UserRepository
from scipy.sparse import csr_matrix

from services.item_preprocessing_service import ItemPreprocessingService
from services.lightfm_service import LightfmService
from services.nearest_neighbors_service import NearestNeighborsService
from services.user_preprocessing_service import UserPreprocessingService


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

    MINIMUM_POSITIVE_RATINGS = 1
    BELOW_PRECISION_THRESHOLD = 0.2
    TARGET_PRECISION = 0.5

    def __init__(self, scoped_session: scoped_session):
        self.book_repository = BookRepository(scoped_session)
        self.user_repository = UserRepository(scoped_session)
        self.lightfm_repository = LightfmRepository()
        self.item_features_repository = ItemFeaturesRepository()

        self.lightfm_service = LightfmService(scoped_session)
        self.item_preprocessing_service = ItemPreprocessingService(
            scoped_session)
        self.user_preprocessing_service = UserPreprocessingService(
            scoped_session)
        self.nearest_neighbors_service = NearestNeighborsService(
            scoped_session)

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
        ids = self.nearest_neighbors_service.find_nearest_neighbors_by_id(
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
        ids = self.nearest_neighbors_service.get_nearest_neighbors_by_content(
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
        Validates training status for user with `user_id`.

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
        if self.lightfm_service.is_user_added(user_id) == False:
            return TrainingStatusDto(TrainingStatus.MUST_TRAIN, "")
        
        self.lightfm_service.add_user_embeddings_if_feature_mismatch()

        y = self.item_preprocessing_service.convert_positive_book_ratings_to_csr(
            positive_book_ratings)
        user_feature = self.user_preprocessing_service.get_transformed_categories_by_user_id_with_unique_feature(
            user_id)
        model = self.lightfm_repository.get_model()
        item_features = self.item_features_repository.get_item_features()
        precision = self.__compute_user_precision(
            model, len(positive_book_ratings), y, item_features=item_features, user_features=user_feature)
        if precision < self.BELOW_PRECISION_THRESHOLD:
            return TrainingStatusDto(TrainingStatus.MUST_TRAIN, "")
        if precision < self.TARGET_PRECISION:
            return TrainingStatusDto(TrainingStatus.CAN_TRAIN, "")
        else:
            return TrainingStatusDto(TrainingStatus.ALREADY_TRAINED, "")

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

    def __compute_user_precision(self, model: LightFM, nr_positive_ratings: int, 
                                 y: csr_matrix, item_features: csr_matrix, user_features: csr_matrix):
        """
        Computes custom_precision_at_k for top `nr_positive_ratings`.
        """
        # k = nr_positive_ratings because precision is computed for all items here
        return custom_precision_at_k(model, y, item_features=item_features, user_features=user_features,
                                     k=nr_positive_ratings, num_threads=12).mean()
