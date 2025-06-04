import pandas as pd
from sqlalchemy.orm.scoping import scoped_session
from db_models.category import Category
from repositories.user_features_repository import UserFeaturesRepository
from repositories.user_preprocessing_repository import UserPreprocessingRepository
from repositories.user_repository import UserRepository
from scipy.sparse import csr_matrix, hstack


class UserPreprocessingService:
    def __init__(self, scoped_session: scoped_session):
        self.user_preprocessing_repository = UserPreprocessingRepository()
        self.user_repository = UserRepository(scoped_session)
        self.user_features_repository = UserFeaturesRepository()

    def get_transformed_categories_by_user_id_with_unique_feature(self, id: int) -> csr_matrix:
        """
        Gets transformed liked categories from user with `id` and unique feature.

        Args:
            id (int): User id.

        Returns:
            csr_matrix: Single row transformed categories with unique feature.

        Raises:
            ValueError: User with `id` doesn't exist
        """
        if self.user_repository.find_by_id(id) is None:
            raise ValueError(f"User with id {id} doesn't exist")
        
        categories = self.__get_transformed_categories_by_user_id(id)
        user_feature = self.user_features_repository.get_user_features()[id]
        nr_common_features = self.user_features_repository.get_nr_common_features()
        user_feature_unique = user_feature[0, nr_common_features:]
        return hstack([categories, user_feature_unique ])

    def __get_transformed_categories_by_user_id(self, id: int) -> csr_matrix:
        """
        Gets transformed liked categories from user with `id`.

        Args:
            id (int): User id.

        Returns:
            csr_matrix: Single row transformed categories.
        """
        categories = self.user_repository.find_liked_categories(id)
        return self.__transform_categories(categories)

    def __transform_categories(self, categories: list[Category]) -> csr_matrix:
        """
        Transforms categories to single row csr_matrix.

        Args:
            categories (list[Category]): Single row list containing categories.

        Returns:
            csr_matrix
        """
        categories = pd.Series([[x.name for x in categories]])
        processing = self.user_preprocessing_repository.get_preprocessing()
        return processing.transform(categories)[0]
