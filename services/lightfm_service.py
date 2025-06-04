import numpy as np
from sqlalchemy.orm.scoping import scoped_session
from repositories.item_features_repository import ItemFeaturesRepository
from repositories.lightfm_repository import LightfmRepository
from scipy.sparse import csr_matrix


class LightfmService:
    def __init__(self, scoped_session: scoped_session):
        self.lightfm_repository = LightfmRepository()
        self.item_features_repository = ItemFeaturesRepository()

    def get_item_representations(self) -> np.ndarray:
        """Returns the concatenation between bias and embedding for each item from `model`."""
        item_features = self.item_features_repository.get_item_features()
        return self.get_item_representations_by_features(item_features)
    
    def get_item_representations_by_features(self, item_features : csr_matrix) -> np.ndarray:
        """Returns the concatenation between bias and embedding for each item in `item_features` from `model`."""
        model = self.lightfm_repository.get_model()
        bias, components = model.get_item_representations(item_features)
        return self.__concatenate_bias_components(bias, components)

    def find_single_item_representation(self, id: int) -> np.ndarray:
        """
        Finds item_representation by book `id`. 

        Args:
            id (int). Id of the book to get its representation.

        Returns:
            np.ndarray (single dimensional array) | None.
        """
        if id < 0 or id >= self.item_features_repository.get_nr_items():
            return None
        features = self.item_features_repository.get_item_features()
        model = self.lightfm_repository.get_model()
        bias, components = model.get_item_representations(features[id])
        return self.__concatenate_bias_components(bias, components)

    def __concatenate_bias_components(self, bias: np.ndarray, components: np.ndarray) -> np.ndarray:
        """
        Concatenates `bias` with `components` horizontally. `bias` must have same number of columns as `components` number of rows.

        Args:
            bias (np.ndarray): Single dimensional row vector where number of columns equals `components` number of rows.
            components (np.ndarray): Two dimensional array where number of rows equals `bias` number of columns.

        Returns:
            np.ndarray: Two dimensional array containing the concatenation between each bias and component.
        """
        return np.concatenate([bias.reshape(-1, 1), components], axis=1)