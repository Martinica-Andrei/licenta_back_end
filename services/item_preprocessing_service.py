import numpy as np
import pandas as pd
from sqlalchemy.orm.scoping import scoped_session
from repositories.item_features_repository import ItemFeaturesRepository
from repositories.item_preprocessing_repository import ItemPreprocessingRepository
from services.lightfm_service import LightfmService
from scipy.sparse import csr_matrix, hstack


class ItemPreprocessingService:
    def __init__(self, scoped_session: scoped_session):
        self.item_preprocessing_repository = ItemPreprocessingRepository()
        self.item_features_repository = ItemFeaturesRepository()
        self.lightfm_service = LightfmService(scoped_session)

    def transform(self, content: str, categories: list[str], authors: list[str]) -> csr_matrix:
        """
        Transforms content, categories and authors to csr_matrix.
        """
        df = pd.DataFrame({'content': [content], 'categories': [
            categories], 'authors': [authors]})
        preprocessing = self.item_preprocessing_repository.get_preprocessing()
        return preprocessing.transform(df)

    def transform_and_expand(self, content: str, categories: list[str], authors: list[str]) -> csr_matrix:
        """
        Transforms content, categories and authors to csr_matrix and appends 0 until it has the same size as nr item features.
        """
        v = self.transform(content, categories, authors)
        nr_features = self.item_features_repository.get_nr_features()
        nr_zeros_to_add = nr_features -  v.shape[1]
        return hstack([v, csr_matrix((v.shape[0], nr_zeros_to_add))])

    def get_item_representation_by_content(self, content: str, categories: list, authors: list) -> np.ndarray:
        """
        Gets item_representation by `content`, `categories` and `authors`. 

        Args:
            content (str): Book description.
            categories (list): Book categories.
            authors (list): Book authors.

        Returns:
            np.ndarray (single dimensional array).
        """

        transformed = self.transform_and_expand(content, categories, authors)
        return self.lightfm_service.get_item_representations_by_features(transformed)[0]