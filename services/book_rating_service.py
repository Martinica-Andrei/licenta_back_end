from sqlalchemy.orm.scoping import scoped_session
from db_models.book_rating import BookRating
from dtos.book_ratings.post_book_rating_dto import PostBookRatingDto
from repositories.book_rating_repository import BookRatingRepository
from repositories.book_repository import BookRepository


class BookRatingError(Exception):
    def __init__(self, message: dict, code=400):
        super().__init__()
        self.message = message
        self.code = code

    def to_tuple(self) -> tuple:
        """
        Returns (`message`, `code`).
        """
        return (self.message, self.code)


class BookRatingService:
    def __init__(self, scoped_session: scoped_session):
        self.book_rating_repository = BookRatingRepository(scoped_session)
        self.book_repository = BookRepository(scoped_session)

    def rate(self, dto: PostBookRatingDto) -> None:
        """
        Adds, deletes or updates book_rating based on `dto.rating`.

        Args:
            dto (PostBookRatingDto): book_rating to create, delete or update.

        Returns:
            None.

        Raises:
            BookRatingError: If book doesn't exist.
        """
        if self.book_repository.find_by_id(dto.book_id) is None:
            raise BookRatingError({"book_id": "* Book id doesn't exist!"})

        model = self.book_rating_repository.find_by_user_id_book_id(
            dto.user_id, dto.book_id)


        if model is None:
            # model is None and rating is like or dislike -> create model
            if dto.rating != 'none':
                book_rating = BookRating(
                    book_id=dto.book_id, user_id=dto.user_id, rating=dto.rating)
                self.book_rating_repository.create(book_rating)
        # model is not none, rating is not none -> update model
        elif dto.rating != 'none':
            model.rating = dto.rating
            self.book_rating_repository.update(model)
        # model is not none, rating is none -> delete model
        else:
            self.book_rating_repository.delete(model)