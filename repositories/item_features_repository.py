from scipy.sparse import csr_matrix, load_npz, save_npz
from utils import BOOKS_DATA_ITEM_FEATURES


class ItemFeaturesRepository:

    __features = csr_matrix(load_npz(BOOKS_DATA_ITEM_FEATURES))

    def __init__(self):
        """No attributes."""

    def get_item_features(self) -> csr_matrix:
        "Gets item_features."
        return self.__features

    def set_item_features(self, features) -> None:
        "Sets and saves item features."
        __item_features = features
        save_npz(BOOKS_DATA_ITEM_FEATURES, __item_features)

    def get_nr_items(self) -> int:
        """Gets nr of items from features."""
        return self.__features.shape[0]

    def get_nr_features(self) -> int:
        """Gets nr of item features from features."""
        return self.__features.shape[1]

    def get_nr_common_features(self) -> int:
        """Get number of common features from features."""
        #each item has 1 unique feature
        #therefore by subtracting nr items from features results in number of common features
        return self.get_nr_features() - self.get_nr_items()