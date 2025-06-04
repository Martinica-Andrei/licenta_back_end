import numpy as np
from sqlalchemy.orm.scoping import scoped_session
from repositories.nearest_neighbors_repository import NearestNeighborsRepository
from services.item_preprocessing_service import ItemPreprocessingService
from services.lightfm_service import LightfmService


class NearestNeighborsService:
    def __init__(self, scoped_session: scoped_session):
        self.nearest_neighbors_repository = NearestNeighborsRepository()
        self.lightfm_service = LightfmService(scoped_session)
        self.item_preprocessing_service = ItemPreprocessingService(
            scoped_session)

    def find_nearest_neighbors_by_id(self, id: int) -> np.ndarray | None:
        """
        Finds nearest neighbors indices of book by `id`.

        Args:
            id (int). Id of the book to get its nearest neighbors indices.

        Returns:
            np.ndarray (one dimensional array): A one dimensional array containing the indices of the nearest neighbors of book.
            or
            None: If id doesn't exist.

        """
        item_representation = LightfmService.find_single_item_representation(
            id)
        if item_representation is None:
            return None
        indices = self.nearest_neighbors_repository.get_nearest_neighbors_for_single_item(
            item_representation)
        return indices

    def get_nearest_neighbors_by_content(self, content: str, categories: list, authors: list) -> np.ndarray:
        """
        Gets nearest neighbors indices using `content`, `categories`, and `authors`.

        Args:
            content (str): Book description.
            categories (list): Book categories.
            authors (list): Book authors.

        Returns:
            np.ndarray (one dimensional array): A one dimensional array containing the indices of the nearest neighbors using content.

        """
        item_representation = self.item_preprocessing_service.get_item_representation_by_content(
            content, categories, authors)
        indices = self.nearest_neighbors_repository.get_nearest_neighbors_for_single_item(
            item_representation)
        return indices
