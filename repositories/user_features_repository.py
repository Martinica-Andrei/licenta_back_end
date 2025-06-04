from scipy.sparse import csr_matrix, load_npz, save_npz
from utils import BOOKS_DATA_USER_FEATURES


class UserFeaturesRepository:

    __features = csr_matrix(load_npz(BOOKS_DATA_USER_FEATURES))

    def __init__(self):
        """No attributes."""

    def get_user_features(self) -> csr_matrix:
        """Gets user features."""
        return self.__features

    def set_user_features(self, features: csr_matrix) -> None:
        "Sets and saves user features."
        self.__features = features
        save_npz(BOOKS_DATA_USER_FEATURES, self.__features)

    def get_nr_users(self) -> int:
        """Gets nr of users from features."""
        return self.__features[0]

    def get_nr_features(self) -> int:
        """Gets nr of user features from features."""
        return self.__features[1]

    def get_nr_common_features(self) -> int:
        """Get number of common features from features."""
        #each user has 1 unique feature
        #therefore by subtracting nr user from features results in number of common features
        return self.get_nr_features() - self.get_nr_users()