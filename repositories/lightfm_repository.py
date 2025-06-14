import joblib
from utils import BOOKS_DATA_MODEL
import numpy as np
from scipy.sparse import hstack, csr_matrix, identity, vstack
from lightfm import LightFM


class LightfmRepository:

    __model : LightFM = joblib.load(BOOKS_DATA_MODEL)

    def __init__(self):
        """No attributes."""

    def get_model(self) -> LightFM:
        """Gets the lightFM model."""
        return LightfmRepository.__model
    
    def save_model(self) -> None:
        """Saves model."""
        joblib.dump(LightfmRepository.__model, BOOKS_DATA_MODEL)

    def add_new_user_embeddings(self, nr_users_to_add: int) -> None:
        """
        Adds new user embedding, biases, gradients and momentum for each new user feature. Code imitates _initialize method from
        https://github.com/lyst/lightfm/blob/master/lightfm/lightfm.py

        Args:
            nr_users_to_add (int): Number of users.

        Returns:
            None.
        """
        # for faster writing
        model = LightfmRepository.__model

        random_state = model.random_state
        nr_components = model.no_components

        #  everything is initialized using https://github.com/lyst/lightfm/blob/master/lightfm/lightfm.py
        # _initialize method as reference
        new_user_embeddings = (random_state.rand(
            nr_users_to_add, nr_components) - 0.5) / nr_components

        new_user_embedding_gradients = np.zeros_like(new_user_embeddings)
        # momentum is used for adadelta
        new_user_embedding_momentum = np.zeros_like(new_user_embeddings)

        new_user_biases = np.zeros(nr_users_to_add)

        new_user_bias_gradients = np.zeros_like(new_user_biases)
        new_user_bias_momentum = np.zeros_like(new_user_biases)

        # adagrad divides by the sum of root of squared gradients represented by gradients variable here
        # therefore it is set to 1
        # _initialize in https://github.com/lyst/lightfm/blob/master/lightfm/lightfm.py does the same thing
        if model.learning_schedule == "adagrad":
            new_user_embedding_gradients += 1
            new_user_bias_gradients += 1

        # add new embeddings as new rows to model
        model.user_embeddings = np.concatenate(
            [model.user_embeddings, new_user_embeddings], axis=0, dtype=np.float32)
        model.user_embedding_gradients = np.concatenate(
            [model.user_embedding_gradients, new_user_embedding_gradients], axis=0, dtype=np.float32)
        model.user_embedding_momentum = np.concatenate(
            [model.user_embedding_momentum, new_user_embedding_momentum], axis=0, dtype=np.float32)

        # add new biases as new columns to model (biases are row vectors)
        model.user_biases = np.concatenate(
            [model.user_biases, new_user_biases], axis=0, dtype=np.float32)
        model.user_bias_gradients = np.concatenate(
            [model.user_bias_gradients, new_user_bias_gradients], axis=0, dtype=np.float32)
        model.user_bias_momentum = np.concatenate(
            [model.user_bias_momentum, new_user_bias_momentum], axis=0, dtype=np.float32)

    @staticmethod
    def new_model_with_single_user(user_feature: csr_matrix, model: LightFM) -> LightFM:
        """
        Creates and returns a new lightFM model with embeddings from features of a single user and all item embeddings.

        Args:
            user_feature (csr_matrix): csr_matrix of single row containing features for this user.

        Returns:
            LightFM.
        """
        # get indices of features
        feature_indices = user_feature.nonzero()[1]
        new_model = LightFM()

        # copy params to new model
        new_model.set_params(**model.get_params())

        # copy all item biases, embeddings
        new_model.item_biases = model.item_biases.copy()
        new_model.item_embeddings = model.item_embeddings.copy()

        # copy all item, embedding gradients, momentum
        new_model.item_bias_gradients = model.item_bias_gradients.copy()
        new_model.item_embedding_gradients = model.item_embedding_gradients.copy()
        new_model.item_bias_momentum = model.item_bias_momentum.copy()
        new_model.item_embedding_momentum = model.item_embedding_momentum.copy()

        new_model.user_biases = model.user_biases[feature_indices].copy()
        new_model.user_embeddings = model.user_embeddings[feature_indices].copy(
        )

        new_model.user_bias_gradients = model.user_bias_gradients[feature_indices].copy(
        )
        new_model.user_embedding_gradients = model.user_embedding_gradients[feature_indices].copy(
        )
        new_model.user_bias_momentum = model.user_bias_momentum[feature_indices].copy(
        )
        new_model.user_embedding_momentum = model.user_embedding_momentum[feature_indices].copy(
        )

        return new_model

    @staticmethod
    def transfer_data_from_new_model_to_model(new_model: LightFM, model: LightFM, user_feature: csr_matrix) -> None:
        """
        Copies all `user_feature` embeddings, gradients, momentum from `new_model` to `model`. Also copies trained item embeddings, gradients, momentum.

        Args:
            new_model (LightFM): Model trained on only one user feature from `user_feature`.
            model (LightFM): Model with all user features.
            user_feature (csr_matrix): csr_matrix of single row containing features for this user.

        Returns:
            None.
        """
        feature_indices = user_feature.nonzero()[1]
        # new_model has the same size for item features, therefore copy all because they have been updated
        model.item_biases = new_model.item_biases.copy()
        model.item_embeddings = new_model.item_embeddings.copy()

        model.item_bias_gradients = new_model.item_bias_gradients.copy()
        model.item_embedding_gradients = new_model.item_embedding_gradients.copy()
        model.item_bias_momentum = new_model.item_bias_momentum.copy()
        model.item_embedding_momentum = new_model.item_embedding_momentum.copy()

        # copy modified user biases, embeddings, gradients momentum
        model.user_biases[feature_indices] = new_model.user_biases.copy()
        model.user_embeddings[feature_indices] = new_model.user_embeddings.copy(
        )

        model.user_bias_gradients[feature_indices] = new_model.user_bias_gradients.copy(
        )
        model.user_embedding_gradients[feature_indices] = new_model.user_embedding_gradients.copy(
        )
        model.user_bias_momentum[feature_indices] = new_model.user_bias_momentum.copy(
        )
        model.user_embedding_momentum[feature_indices] = new_model.user_embedding_momentum.copy(
        )
