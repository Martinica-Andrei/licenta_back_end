import numpy as np
from sqlalchemy.orm.scoping import scoped_session
from db_models.book import Book
from db_models.book_authors import BookAuthors
from db_models.book_rating import BookRating
from repositories.helper_methods import HelperMethods
import sqlalchemy as sa
from sqlalchemy.orm import selectinload, with_loader_criteria


class BookRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

    def find_by_id(self, id: int) -> Book | None:
        """
        Finds book by `id`.

        Args:
            id (int): Id to fetch book.

        Returns:
            Book | None
        """

        return self.scoped_session.query(Book).where(Book.id == id).first()

    def find_by_title_containing(self, title: str, count: int) -> list[Book]:
        """
        Finds all books that have `title` using full-text search in boolean mode.

        Args:
            title (str): Books that contain title.
            count (int): Number of books to fetch.

        Returns:
            list[Book]: List of books that have `title`.
        """
        # words_str: the words to match against
        # words: used for creating locate_str and mapping location parameters to words
        # ex: words_str '+one* +punch*' while words = ['one', 'punch']
        words_str, words = HelperMethods.convert_for_word_search_mysql(title)
        if len(words_str) == 0:
            return []
        # locate each word to sort by index ( to take into account the order of words)
        locate_str = ', '.join(
            [f'LOCATE(:pos_{i}, title) AS pos_{i}' for i in range(len(words))])
        # pos_names for order by, same as locate_str aliases
        pos_names = [f'pos_{i}' for i in range(len(words))]
        query = f"""SELECT *, LENGTH(title) as len_title, {locate_str} 
                    FROM book WHERE MATCH(title) AGAINST (:words IN BOOLEAN MODE) 
                    ORDER BY {', '.join(pos_names)}, len_title LIMIT :limit;
                 """
        # pass parameters to be replaced in query
        # keys don't have to start with ':' here
        # first params are positions values, ex : pos_0 : one, pos_1: punch
        params = dict(zip(pos_names, words))
        params['words'] = words_str
        params['limit'] = count
        models = self.scoped_session.query(Book).from_statement(
            sa.text(query)).params(params).all()
        return models

    def find_by_ids_with_categories_authors(self, ids: list | np.ndarray) -> list[Book]:
        """
        Finds all books by `ids` with categories and authors.

        Args:
            ids (list | np.ndarray): Single dimension array or list containing indices to fetch books.

        Returns:
            list[Book]. List of books containing authors and categories with id in `ids`.
        """
        models = self.scoped_session.query(Book).where(Book.id.in_(ids)).\
            options(selectinload(Book.categories),
                    selectinload(Book.authors).selectinload(BookAuthors.author)).all()
        models = self.__order_to_initial_ids(models, ids)
        return models

    def find_by_ids_with_categories_authors_rating(self, ids: list | np.ndarray, user_id: int) -> list[Book]:
        """
        Finds all books by `ids` with categories, authors and also finds user rating for `user_id`.

        Args:
            ids (list | np.ndarray): Single dimension array or list containing indices to fetch books by id.
            user_id (int): Fetch rating from user with this id.

        Returns:
            list[Book]. List of books containing authors, categories and user rating for `user_id` where book has id in ids.
        """
        models = self.scoped_session.query(Book).where(Book.id.in_(ids)).\
            options(selectinload(Book.categories),
                    selectinload(Book.authors).selectinload(
                        BookAuthors.author),
                    selectinload(Book.ratings),
                    with_loader_criteria(BookRating, BookRating.user_id == user_id)).all()
        models = self.__order_to_initial_ids(models, ids)
        return models

    @staticmethod
    def __order_to_initial_ids(models: Book, ids: list | np.ndarray) -> list[Book]:
        """
        Orders books to initial ids. For example, if fetch gets ids [3,7,1], sql might change the order to [7,1,3].

        Args:
            ids (list | np.ndarray): Single dimension array or list to reorder `models`.

        Returns:
            list[Book]. List that has same order as `ids`.
        """
        # list has index method while np.ndarray doesn't
        # therefore convert to list, does nothing if it is already a list
        ids = list(ids)
        models = sorted(models, key=lambda x: ids.index(x.id))
        return models
