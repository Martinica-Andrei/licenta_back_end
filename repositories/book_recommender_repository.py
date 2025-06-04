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