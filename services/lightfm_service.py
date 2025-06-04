import numpy as np
from sqlalchemy.orm.scoping import scoped_session
from repositories.item_features_repository import ItemFeaturesRepository
from repositories.lightfm_repository import LightfmRepository
from scipy.sparse import csr_matrix
from repositories.user_features_repository import UserFeaturesRepository


class LightfmService:
    def __init__(self, scoped_session: scoped_session):
        self.lightfm_repository = LightfmRepository()
        self.item_features_repository = ItemFeaturesRepository()
        self.user_features_repository = UserFeaturesRepository()

    def get_item_representations(self) -> np.ndarray:
        """Returns the concatenation between bias and embedding for each item from `model`."""
        item_features = self.item_features_repository.get_item_features()
        return self.get_item_representations_by_features(item_features)

    def get_item_representations_by_features(self, item_features: csr_matrix) -> np.ndarray:
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
        return self.__concatenate_bias_components(bias, components)[0]

    def is_user_added(self, user_id: int) -> bool:
        """
        Check user embeddings and user features to see if `user_id` is added.

        Args:
            user_id (int): User id.

        Returns:
            bool.
        """
        return (self.user_features_repository.get_nr_user_features_to_add(user_id) <= 0) and\
            (self.__get_nr_user_embeddings_to_add(user_id) <= 0)

    def add_user_embeddings_if_feature_mismatch(self) -> None:
        """
        Adds embeddings to users to match the number of features
        """
        # this method exists because in rare cases, embeddings from add_new_users will be discarded
        # because they are not saved immediately.
        nr_embeddings_to_add = self.__get_user_embedding_feature_size_mismatch()
        if nr_embeddings_to_add > 0:
            self.lightfm_repository.add_new_user_embeddings(nr_embeddings_to_add)

    def add_new_users(self, user_id: int) -> None:
        """
        Checks if user_id is added, if not add new user features and user embeddings, gradients, momentum.

        Args:
            user_id (int): Computes distance between current_features/embeddings and user id.

        Returns:
            None.

        """
        # warning, in some cases user features will be added while embeddings won't be added
        nr_user_features_to_add = self.user_features_repository.get_nr_user_features_to_add(
            user_id)
        if nr_user_features_to_add > 0:
            self.user_features_repository.add_new_user_features(
                nr_user_features_to_add)

        nr_user_embeddings_to_add = self.__get_nr_user_embeddings_to_add(
            user_id)
        if nr_user_embeddings_to_add > 0:
            self.lightfm_repository.add_new_user_embeddings(
                nr_user_embeddings_to_add)

    def reset_user_gradients(self, user_id: int) -> None:
        """Resets bias and embedding gradients to 0 for `user_id`."""
        nr_common_features = self.user_features_repository.get_nr_common_features()
        model = self.lightfm_repository.get_model()
        model.user_embedding_gradients[nr_common_features +
                                       user_id] = np.ones(model.no_components)
        model.user_bias_gradients[nr_common_features + user_id] = 1

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

    def __get_nr_user_embeddings_to_add(self, user_id: int) -> None:
        """
        Gets number of user embeddings to add for each new user by computing the distance between `user_id` and (unique embeddings - 1) from model.

        Args:
            user_id (int): User id.

        Returns:
            None.
        """
        # user_embeddings also has common embeddings, therefore remove them
        unique_embeddings_len = self.__get_number_of_unique_embeddings()
        # user id starts count from 0 while unique_embeddings_len starts from 1, therefore subtract 1 from embeddings
        nr_embeddings_to_add = user_id - (unique_embeddings_len - 1)
        return nr_embeddings_to_add

    def __get_number_of_unique_embeddings(self) -> int:
        """Get number of embeddings that are associated with unique features."""
        model = self.lightfm_repository.get_model()
        return model.user_embeddings.shape[0] - \
            self.user_features_repository.get_nr_common_features()

    def __get_user_embedding_feature_size_mismatch(self) -> int:
        """
        Gets how many more features there are than embeddings.

        Returns:
            bool.
        """
        nr_features = self.user_features_repository.get_nr_features()
        nr_embeddings = self.lightfm_repository.get_model(
        ).user_embeddings.shape[0]
        return nr_features - nr_embeddings
