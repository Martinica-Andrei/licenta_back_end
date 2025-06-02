from sqlalchemy.orm.scoping import scoped_session
from db_models.book_rating import BookRating
from dtos.users.get_rating_dto import GetRatingDto
from repositories.book_image_repository import BookImageRepository
from repositories.user_repository import UserRepository
from dtos.users.get_user_with_book_rating_dto import GetUserWithBookRatingDto
from db_models.user import User


class UserService:
    def __init__(self, scoped_session: scoped_session):
        self.user_repository = UserRepository(scoped_session)

    def find_by_id_with_book_rating(self, id: int) -> GetUserWithBookRatingDto | None:
        """
        Finds user by id with books that he rated.

        Args:
            id (int): User id.

        Returns:
            GetUserDto | None
        """
        model = self.user_repository.find_by_id_with_book_rating(id)
        if model is not None:
            return self.map_to_dto(model)
        return None

    @staticmethod
    def map_to_dto(model: User) -> GetUserWithBookRatingDto:
        rating_dtos = [UserService.map_rating_to_dto(
            rating) for rating in model.book_ratings]
        return GetUserWithBookRatingDto(model.name, rating_dtos)

    @staticmethod
    def map_rating_to_dto(model: BookRating) -> GetRatingDto:
        image = BookImageRepository.convert_image_base64(model.book.image_link)
        dto = GetRatingDto(model.book_id,
                           model.book.title,
                           model.rating,
                           image,
                           model.book.link,
                           model.book.nr_likes,
                           model.book.nr_dislikes)
        return dto

    @staticmethod
    def map_to_model_from_get(dto: GetUserWithBookRatingDto):
        return User(name=dto.name, password=dto.password)
