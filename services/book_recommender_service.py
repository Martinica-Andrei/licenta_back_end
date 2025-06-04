from flask import json
from lightfm import LightFM
import numpy as np
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
from threading import Thread, Event
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

    __MINIMUM_POSITIVE_RATINGS: int = 5
    __BELOW_PRECISION_THRESHOLD: float = 0.2
    __MAX_PRECISION: float = 0.5

    __curent_user_training_id: int = -1
    __current_user_training_progress: int = -1
    __event_training_progress_changed = Event()

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

    def get_recommendations_by_user(self, id: int) -> list[GetBookDto]:
        """
        Gets book recommendations by user with `id`.

        Args:
            id (int). User id.

        Returns:
            list[GetBookDto].
        """
        item_features = self.item_features_repository.get_item_features()
        user_feature = self.user_preprocessing_service.get_transformed_categories_by_user_id_with_unique_feature(
            id)
        book_indices = self.__get_all_book_indices_not_rated(id)
        model = self.lightfm_repository.get_model()
        predictions = model.predict(
            0, book_indices, item_features=item_features, user_features=user_feature)
        indices_sorted = np.argsort(-predictions)
        top_book_indices = book_indices[indices_sorted[:100]]
        predicted_books = self.book_repository.find_by_ids_with_categories_authors_rating(
            top_book_indices, id)
        dtos = [self.map_model_to_get_dto(book) for book in predicted_books]
        return dtos

    def validate_training_status(self, user_id: int) -> TrainingStatusDto:
        """
        Validates training status for user with `user_id`.

        Args:
            user_id (id): User id.

        Returns:
            TrainingStatusDto.
        """
        if BookRecommenderService.__curent_user_training_id != -1:
            if BookRecommenderService.__curent_user_training_id == user_id:
                return TrainingStatusDto(TrainingStatus.CURRENTLY_TRAINING_LOGGED_IN_USER, "")
            else:
                return TrainingStatusDto(TrainingStatus.CURRENTLY_TRAINING_OTHER_USER, "Currently training another user. Please wait a few minutes!")

        positive_book_ratings = self.user_repository.find_liked_books(user_id)
        if len(positive_book_ratings) < BookRecommenderService.__MINIMUM_POSITIVE_RATINGS:
            message = f"Minimum {BookRecommenderService.__MINIMUM_POSITIVE_RATINGS} positive ratings are required for recommendations. Like " +\
                      f"{BookRecommenderService.__MINIMUM_POSITIVE_RATINGS - len(positive_book_ratings)} more books."
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
        if precision < BookRecommenderService.__BELOW_PRECISION_THRESHOLD:
            return TrainingStatusDto(TrainingStatus.MUST_TRAIN, "")
        if precision < BookRecommenderService.__MAX_PRECISION:
            return TrainingStatusDto(TrainingStatus.CAN_TRAIN, "")
        else:
            return TrainingStatusDto(TrainingStatus.ALREADY_TRAINED, "")

    def train_on_single_user(self, user_id: int) -> None:
        """
        Trains the model on a single user by creating a new model and transfering the data.

        Args:
            user_id (int): User id.

        Returns:
            None.
        """

        BookRecommenderService.__curent_user_training_id = user_id

        self.lightfm_service.add_new_users(user_id)
        self.lightfm_service.reset_user_gradients(user_id)

        user_feature = self.user_preprocessing_service.get_transformed_categories_by_user_id_with_unique_feature(
            user_id)
        item_features = self.item_features_repository.get_item_features()

        single_user_model = self.lightfm_repository.new_model_with_single_user(
            user_feature, self.lightfm_repository.get_model())

        positive_book_ratings = self.user_repository.find_liked_books(user_id)
        y = self.item_preprocessing_service.convert_positive_book_ratings_to_csr(
            positive_book_ratings)

        thread_args = (single_user_model,
                        len(positive_book_ratings),
                        y,
                        item_features,
                        user_feature)

        Thread(target=self.__train_on_single_user, args=thread_args).start()

    def get_training_progress(self):
        """
        Awaits and yields training progress when it is changed.
        """
        while BookRecommenderService.__curent_user_training_id != -1:
            BookRecommenderService.__event_training_progress_changed.wait()
            v = {'percentage': BookRecommenderService.__current_user_training_progress}
            yield json.dumps(v) + '\n'
            BookRecommenderService.__event_training_progress_changed.clear()
        BookRecommenderService.__event_training_progress_changed.set()

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

    def __get_all_book_indices_not_rated(self, user_id: int) -> np.ndarray:
        """
        Gets all book indices/ids that are not rated by user.

        Args:
            user_id (int): User id.

        Returns:
            np.ndarray: Single dimensional array.
        """
        book_indices = np.arange(self.item_features_repository.get_nr_items())
        rated_books = self.user_repository.find_rated_books(user_id)
        rated_ids = [book.id for book in rated_books]
        return book_indices[np.isin(book_indices, rated_ids) == False]

    def __train_on_single_user(self, model: LightFM, nr_positive_ratings: int,
                               y: csr_matrix, item_features: csr_matrix, user_feature: csr_matrix):
        """
        Trains on single user.

        Args:
            model (LightFM): LightFM model with features for only 1 user.
            nr_positive_ratings (int): Number of positive ratings.
            y (csr_matrix): Single row csr matrix representing target predictions.
            item_features (csr_matrix): All item features.
            user_feature (csr_matrix): Single row csr_matrix representing features for that user.
        """

        user_feature_ones = csr_matrix(user_feature.data)
        max_percentage = 0

        BookRecommenderService.__current_user_training_progress = max_percentage
        BookRecommenderService.__event_training_progress_changed.set()

        while True:
            model.fit_partial(y, item_features=item_features,
                              user_features=user_feature_ones, epochs=200, num_threads=12)
            precision = self.__compute_user_precision(model, nr_positive_ratings,
                                                      y, item_features, user_feature_ones)
            percentage = round(precision / BookRecommenderService.__BELOW_PRECISION_THRESHOLD, 2)
            percentage = min(1, percentage) # percentage must take values from 0 to 1 only
            if percentage > max_percentage:
                BookRecommenderService.__current_user_training_progress = percentage
                BookRecommenderService.__event_training_progress_changed.set()
            if precision >= BookRecommenderService.__BELOW_PRECISION_THRESHOLD:
                break

        BookRecommenderService.__curent_user_training_id = -1
        BookRecommenderService.__event_training_progress_changed.set()
        # wait for progress to be displayed then continue
        BookRecommenderService.__event_training_progress_changed.wait()
        BookRecommenderService.__current_user_training_progress = -1
        BookRecommenderService.__event_training_progress_changed.clear()

        base_model = self.lightfm_repository.get_model()
        LightfmRepository.transfer_data_from_new_model_to_model(
            model, base_model, user_feature)
        self.nearest_neighbors_service.refit_neighbors()
        self.lightfm_repository.save_model()