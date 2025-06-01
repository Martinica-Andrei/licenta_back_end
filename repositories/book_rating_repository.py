from sqlalchemy.orm.scoping import scoped_session
from db_models.book_rating import BookRating
from sqlalchemy import and_

class BookRatingRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

    def find_by_user_id_book_id(self, user_id: int, book_id: int) -> BookRating | None:
        """
        Finds book_rating that belongs to `user_id` for `book_id`.

        Args:
            user_id (int): The user that likes `category_id`.
            book_id (int): The book rated by `user_id`.

        Returns:
            BookRating | None
        """
        return self.scoped_session.query(BookRating).where(and_(BookRating.user_id == user_id, BookRating.book_id == book_id)).first()

    def create(self, model : BookRating) -> BookRating:
        """
        Creates book_rating in db.

        Args:
            model (BookRating): Model to create.

        Returns:
            BookRating: Updated model from db.
        """

        self.scoped_session.add(model)
        self.scoped_session.commit()
        return model

    def update(self, model : BookRating) -> BookRating:
        """
        Updates book_rating in db.

        Args:
            model (BookRating): Model to update.

        Returns:
            BookRating: Updated model from db.
        """
        self.scoped_session.commit()
        return model

    def delete(self, model: BookRating) -> None:
        """
        Deletes book_rating in db.

        Args:
            model (BookRating): Model to delete.

        Returns:
            None.
        """
        self.scoped_session.delete(model)
        self.scoped_session.commit()
