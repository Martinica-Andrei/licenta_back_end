from load_book_recommendation_model import (model,
                                            get_nr_users,
                                            get_nr_user_features,
                                            set_user_features,
                                            user_features,
                                            get_length_common_features_users)
import numpy as np
from scipy.sparse import hstack, csr_matrix, identity, vstack


class LightfmRepository:

    @staticmethod
    def add_new_users(user_id: int):
        nr_user_features_to_add = LightfmRepository.__get_nr_user_features_to_add(user_id)
        if nr_user_features_to_add > 0:
            LightfmRepository.__add_new_user_features(nr_user_features_to_add)

        nr_user_embeddings_to_add = LightfmRepository.__get_nr_user_embeddings_to_add(user_id)
        if nr_user_embeddings_to_add > 0:
            LightfmRepository.__add_new_user_embeddings(nr_user_embeddings_to_add)

    @staticmethod
    def __add_new_user_embeddings(nr_users_to_add: int) -> None:
        """
        Adds new user embedding, biases, gradients and momentum for each new user feature. Code imitates _initialize method from
        https://github.com/lyst/lightfm/blob/master/lightfm/lightfm.py

        Args:
            nr_users_to_add (int): Number of users.

        Returns:
            None.
        """
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
    def __add_new_user_features(nr_users_to_add: int) -> None:
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
            [user_features(), csr_matrix((get_nr_users(), nr_users_to_add))])
        # identity matrix representing each new user unique feature
        new_user_features = identity(nr_users_to_add)
        # prepend 0 repeated by get_nr_user_features so new_user_features has same number of features + new features
        new_user_features = hstack(
            [csr_matrix((nr_users_to_add, get_nr_user_features())), new_user_features])
        # append new user features as rows
        new_user_features = vstack(
            [user_features_hstack, new_user_features])
        # ensure new features are csr_matrix by converting
        new_user_features = csr_matrix(new_user_features)
        set_user_features(new_user_features)

    @staticmethod
    def __get_nr_user_features_to_add(user_id: int) -> None:
        """
        Gets number of user features to add for each new user by computing the distance between user_id and (size - 1) from user count in features.

        Args:
            user_id (int): User id.

        Returns:
            None.
        """
        # user_id starts count from 0 while nr_users starts from 1, therefore subtract 1 from nr_users
        nr_features_to_add = user_id - (get_nr_users() - 1)
        return nr_features_to_add

    @staticmethod
    def __get_nr_user_embeddings_to_add(user_id: int):
        """
        Gets number of user embeddings to add for each new user by computing the distance between user_id and (unique embeddings - 1) from model.

        Args:
            user_id (int): User id.

        Returns:
            None.
        """
        # user_embeddings also has common embeddings, therefore remove them
        unique_embeddings_len = model.user_embeddings.shape[0] - \
            get_length_common_features_users()
        # user id starts count from 0 while unique_embeddings_len starts from 1, therefore subtract 1 from embeddings
        nr_embeddings_to_add = user_id - (unique_embeddings_len - 1)
        return nr_embeddings_to_add
