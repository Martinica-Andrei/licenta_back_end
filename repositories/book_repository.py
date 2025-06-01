from sqlalchemy.orm.scoping import scoped_session
from db_models.book import Book
from repositories.helper_methods import HelperMethods
import sqlalchemy as sa

class BookRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

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
        results = self.scoped_session.query(Book).from_statement(sa.text(query)).params(params).all()
        return results