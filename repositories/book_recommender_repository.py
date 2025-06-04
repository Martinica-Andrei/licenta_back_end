import numpy as np
import pandas as pd
from readerwriterlock.rwlock import RWLockWrite
from db_models.category import Category
from load_book_recommendation_model import (item_preprocessing,
                                            model_item_representations,
                                            user_preprocessing,
                                            item_features,
                                            get_nr_items,
                                            model,
                                            neighbors)
from scipy.sparse import csr_matrix, hstack

books_model_memory_change_lock = RWLockWrite()


class BookRecommenderRepository:

    lock = RWLockWrite()

    @staticmethod
    def find_nearest_neighbors_by_id(id: int) -> np.ndarray | None:
        """
        Finds nearest neighbors indices of book by `id`.

        Args:
            id (int). Id of the book to get its nearest neighbors indices.

        Returns:
            np.ndarray (one dimensional array): A one dimensional array containing the indices of the nearest neighbors of book.
            or
            None: If id doesn't exist.

        """
        with BookRecommenderRepository.lock.gen_rlock():
            item_representation = BookRecommenderRepository.__find_item_representation_by_id(
                id)
            if item_representation is None:
                return None
            indices = BookRecommenderRepository.__get_nearest_neighbors_by_representation(
                item_representation)
            return indices

    @staticmethod
    def get_nearest_neighbors_by_content(content: str, categories: list, authors: list) -> np.ndarray:
        """
        Gets nearest neighbors indices using `content`, `categories`, and `authors`.

        Args:
            content (str): Book description.
            categories (list): Book categories.
            authors (list): Book authors.

        Returns:
            np.ndarray (one dimensional array): A one dimensional array containing the indices of the nearest neighbors using content.

        """
        with BookRecommenderRepository.lock.gen_rlock():
            item_representation = BookRecommenderRepository.__get_item_representations_by_content(
                content, categories, authors)
            indices = BookRecommenderRepository.__get_nearest_neighbors_by_representation(
                item_representation)
            return indices

    @staticmethod
    def transform_categories(categories: list[Category]) -> csr_matrix:
        """
        Transforms categories to single row csr_matrix.

        Args:
            categories (list[Category]): Single row list containing categories.

        Returns:
            csr_matrix
        """
        categories = pd.Series([[x.name for x in categories]])
        return user_preprocessing().transform(categories)[0]
    
    @staticmethod
    def convert_positive_book_ratings_to_csr(positive_book_ratings : list[int]) -> csr_matrix:
        """
        Converts `positive_book_ratings` ids to csr matrix.

        Args:
            positive_book_ratings (list[int]): List containing ids of positive book ratings.

        Returns:
            csr_matrix: Csr matrix of shape single row and all book ids as columns, where `positive_book_ratings` ids are set to 1 while others are set to 0.
        """
        ones = np.ones_like(positive_book_ratings)
        row_zeros = np.zeros_like(positive_book_ratings)

        nr_books = get_nr_items()
        y = csr_matrix((ones, (row_zeros, positive_book_ratings)),
                    shape=(1, nr_books), dtype=int)
        return y

    @staticmethod
    def __get_item_representations_by_content(content: str, categories: list, authors: list) -> np.ndarray:
        """
        Gets item_representation by `content`, `categories` and `authors`. 

        Args:
            content (str): Book description.
            categories (list): Book categories.
            authors (list): Book authors.

        Returns:
            np.ndarray (single dimensional array): Represents the concatenation between bias and components.
        """

        feature_df = pd.DataFrame({'content': [content], 'categories': [
                                  categories], 'authors': [authors]})
        transformed = item_preprocessing().transform(feature_df)

        with BookRecommenderRepository.lock.gen_rlock():
            # item_preprocessing returns common features only
            # therefore it is required to concatenate unique features as 0
            # to get the full representation of item
            nr_zeros_to_add = item_features().shape[1] - transformed.shape[1]
            # concatenate horizontally: transformed with unique features
            # the format is [shared_features, unique_features]
            transformed = hstack(
                [transformed, csr_matrix((1, nr_zeros_to_add))])
            # bias and components are 2 dim arrays, here it is one row and n columns
            bias, components = model.get_item_representations(transformed)
            # concatenate bias with components because model_item_representations does the same
            # and kneighbors expects bias with components to be concatenated
            # item_representations is of shape 1 row n columns
            item_representations = np.concatenate(
                [bias.reshape(-1, 1), components], axis=1)
            return item_representations[0]

    @staticmethod
    def __find_item_representation_by_id(id: int) -> np.ndarray | None:
        """
        Finds item_representation by book `id`. 

        Args:
            id (int). Id of the book to get its representation.

        Returns:
            np.ndarray (single dimensional array) | None.
        """
        with BookRecommenderRepository.lock.gen_rlock():
            item_representations = model_item_representations()
            if id < 0 or id >= len(item_representations):
                return None
            return item_representations[id]

    @staticmethod
    def __get_nearest_neighbors_by_representation(item_representation: np.ndarray) -> np.ndarray:
        """
        Gets the indices of the nearest neighbors of a single book using `item_representation`.

        Args:
            item_representation (np.ndarray): A one dimensional array obtained by concatenating the bias and components.

        Returns:
            np.ndarray (one dimensional array): A one dimensional array containing the indices of the nearest neighbors of book.
        """
        # kneighbors takes as input an array with 2 dim, one row for each item
        # and also returns a tuple therefore index it by [0]
        indices = neighbors.kneighbors(
            [item_representation], return_distance=False)[0]
        return indices
