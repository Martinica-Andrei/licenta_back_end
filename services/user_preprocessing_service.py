import numpy as np
import pandas as pd
from sqlalchemy.orm.scoping import scoped_session
from db_models.category import Category
from repositories.item_features_repository import ItemFeaturesRepository
from repositories.item_preprocessing_repository import ItemPreprocessingRepository
from repositories.user_preprocessing_repository import UserPreprocessingRepository
from repositories.user_repository import UserRepository
from services.lightfm_service import LightfmService
from scipy.sparse import csr_matrix, hstack


class UserPreprocessingService:
    def __init__(self, scoped_session: scoped_session):
        self.user_preprocessing_repository = UserPreprocessingRepository()
        self.user_repository = UserRepository(scoped_session)
    

    def get_transformed_categories_by_user_id(self, id: int) -> csr_matrix:
        """
        Gets transformed liked categories from user with `id`.

        Args:
            id (int): User id.

        Returns:
            csr_matrix: Single row transformed categories.
        """
        categories = self.user_repository.find_liked_categories()
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