from scipy.sparse import csr_matrix, load_npz, save_npz
from utils import BOOKS_DATA_USER_FEATURES
from scipy.sparse import hstack, identity, vstack


class UserFeaturesRepository:

    __features = csr_matrix(load_npz(BOOKS_DATA_USER_FEATURES))

    def __init__(self):
        """No attributes."""

    def get_user_features(self) -> csr_matrix:
        """Gets user features."""
        return UserFeaturesRepository.__features

    def set_user_features(self, features: csr_matrix) -> None:
        "Sets and saves user features."
        UserFeaturesRepository.__features = features
        save_npz(BOOKS_DATA_USER_FEATURES, self.__features)

    def get_nr_users(self) -> int:
        """Gets nr of users from features."""
        return UserFeaturesRepository.__features.shape[0]

    def get_nr_features(self) -> int:
        """Gets nr of user features from features."""
        return UserFeaturesRepository.__features.shape[1]

    def get_nr_common_features(self) -> int:
        """Get number of common features from features."""
        #each user has 1 unique feature
        #therefore by subtracting nr user from features results in number of common features
        return self.get_nr_features() - self.get_nr_users()
    
    def get_nr_user_features_to_add(self, user_id: int) -> None:
        """
        Gets number of user features to add for each new user by computing the distance between `user_id` and (size - 1) from user count in features.

        Args:
            user_id (int): User id.

        Returns:
            None.
        """
        # user_id starts count from 0 while nr_users starts from 1, therefore subtract 1 from nr_users
        nr_features_to_add = user_id - (self.get_nr_users() - 1)
        return nr_features_to_add


    def add_new_user_features(self, nr_users_to_add: int) -> None:
        """
        Creates new unique column for each new user in user_features and adds `nr_users_to_add` rows
        where each user has 1 unique value in the new columns and saves the new user features.

        Args:
            nr_users_to_add (int): Number of users.

        Returns:
            None.
        """
        # expand horizontally current user_features with 0 for each new user
        user_features_hstack = hstack(
            [self.get_user_features(), csr_matrix((self.get_nr_users(), nr_users_to_add))])
        # identity matrix representing each new user unique feature
        new_user_features = identity(nr_users_to_add)
        # prepend 0 repeated by get_nr_user_features so new_user_features has same number of features + new features
        new_user_features = hstack(
            [csr_matrix((nr_users_to_add, self.get_nr_features())), new_user_features])
        # append new user features as rows
        new_user_features = vstack(
            [user_features_hstack, new_user_features])
        # ensure new features are csr_matrix by converting
        new_user_features = csr_matrix(new_user_features)
        self.set_user_features(new_user_features)