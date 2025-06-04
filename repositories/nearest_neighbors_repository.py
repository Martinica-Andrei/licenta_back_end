import numpy as np
from scipy.sparse import csr_matrix, load_npz, save_npz
from sklearn.neighbors import NearestNeighbors
from utils import BOOKS_DATA_USER_FEATURES


class NearestNeighborsRepository:

    __model = NearestNeighbors(n_neighbors=30, metric='cosine')

    def __init__(self):
        """No attributes."""

    def get_model(self) -> NearestNeighbors:
        return NearestNeighborsRepository.__model
    
    def get_nearest_neighbors_for_single_item(self, item_representation: np.ndarray) -> np.ndarray:
        """
        Gets the indices of the nearest neighbors of a single book using `item_representation`.

        Args:
            item_representation (np.ndarray): A one dimensional array.

        Returns:
            np.ndarray (one dimensional array): A one dimensional array containing the indices of the nearest neighbors of book.
        """
        # kneighbors takes as input an array with 2 dim, one row for each item
        # and also returns a tuple therefore index it by [0]
        indices = NearestNeighborsRepository.__model.kneighbors(
            [item_representation], return_distance=False)[0]
        return indices