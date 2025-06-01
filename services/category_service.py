from sqlalchemy.orm.scoping import scoped_session
from db_models.category import Category
from dtos.categories.get_category_dto import GetCategoryDto
from dtos.categories.get_category_with_rating_dto import GetCategoryWithRatingDto
from query_models.category_with_rating_view import CategoryWithRatingView
from repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, scoped_session: scoped_session):
        self.category_repository = CategoryRepository(scoped_session)

    def find_by_name_containing(self, name: str) -> list[GetCategoryDto]:
        """
        Finds all categories that have `name`.

        Args:
            name (str): Name of categories.

        Returns:
            list[GetCategoryDto]: List of categories that have `name`.
        """
        models = self.category_repository.find_by_name_containing(name)
        dtos = [self.map_model_to_get_category_dto(model) for model in models]
        return dtos

    def find_by_name_containing_with_liked(self, name: str, user_id: int) -> list[GetCategoryWithRatingDto]:
        """
        Finds all categories that have `name` and if user with `user_id` liked the category or not.

        Args:
            name (str): Name of categories.
            user_id (int): Id of user

        Returns:
            list[GetCategoryWithRatingDto]: List of categories that have `name` and if user with `user_id` liked the category or not.
        """
        views = self.category_repository.find_by_name_containing_with_liked(
            name, user_id)
        dtos = [self.map_category_with_rating_view_to_dto(
            view) for view in views]
        return dtos

    def find_liked_categories(self, user_id: int) -> list[GetCategoryDto]:
        """
        Finds all categories liked categories from user with `user_id`.

        Args:
            user_id (int): Id of user.

        Returns:
            list[GetCategoryDto]: List of categories with user rating from `user_id` that have `name`.
        """
        models = self.category_repository.find_liked_categories(user_id)
        dtos = [self.map_model_to_get_category_dto(model) for model in models]
        return dtos

    @staticmethod
    def map_model_to_get_category_dto(model: Category) -> GetCategoryDto:
        return GetCategoryDto(model.id, model.name)

    @staticmethod
    def map_category_with_rating_view_to_dto(view: CategoryWithRatingView) -> GetCategoryWithRatingDto:
        # converts None to false
        is_liked = (view.liked == True)
        return GetCategoryWithRatingDto(view.id, view.name, is_liked)
