from sqlalchemy.orm.scoping import scoped_session
from db_models.liked_categories import LikedCategories
from dtos.liked_categories.post_liked_category_dto import PostLikedCategoryDto
from repositories.book_repository import BookRepository
from repositories.category_repository import CategoryRepository
from repositories.liked_category_repository import LikedCategoryRepository


class LikedCategoryError(Exception):
    def __init__(self, message: dict, code=400):
        super().__init__()
        self.message = message
        self.code = code

    def to_tuple(self) -> tuple:
        """
        Returns (`message`, `code`).
        """
        return (self.message, self.code)


class LikedCategoryService:
    def __init__(self, scoped_session: scoped_session):
        self.liked_category_repository = LikedCategoryRepository(
            scoped_session)
        self.category_repository = CategoryRepository(scoped_session)

    def update(self, dto: PostLikedCategoryDto) -> None:
        """
        Adds or deletes liked_category based on `dto.like` value.

        Args:
            dto (PostLikedCategoryDto): Category to create or delete.

        Returns:
            None.

        Raises:
            LikedCategoryError: If category doesn't exist.
        """
        if self.category_repository.find_by_id(dto.category_id) is None:
            raise LikedCategoryError({"category_id": "* Category doesn't exist!"})

        model = self.liked_category_repository.find_by_user_id_category_id(
            dto.user_id, dto.category_id)

        # if user likes the category and there is no model, create it
        # otherwise if user doesn't like and there is a model, delete it
        if dto.like:
            if model is None:
                model = LikedCategories(
                    category_id=dto.category_id, user_id=dto.user_id)
                self.liked_category_repository.create(model)
        elif model is not None:
            self.liked_category_repository.delete(model)
