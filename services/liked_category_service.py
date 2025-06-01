from sqlalchemy.orm.scoping import scoped_session
from db_models.liked_categories import LikedCategories
from dtos.liked_categories.post_liked_category_dto import PostLikedCategoryDto
from repositories.liked_category_repository import LikedCategoryRepository


class LikedCategoryService:
    def __init__(self, scoped_session: scoped_session):
        self.liked_category_repository = LikedCategoryRepository(
            scoped_session)

    def update(self, dto: PostLikedCategoryDto) -> None:
        """
        Adds or deletes liked_category based on `dto.like` value.

        Args:
            dto (PostLikedCategoryDto): Category to create or delete.

        Returns:
            None.
        """
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
