from sqlalchemy.orm.scoping import scoped_session
from db_models.category import Category
from db_models.liked_categories import LikedCategories
from query_models.category_with_rating_view import CategoryWithRatingView


class CategoryRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

    def find_by_name_containing(self, name: str) -> list[Category]:
        """
        Finds all categories that have `name`.

        Args:
            name (str): Name of categories.

        Returns:
            list[Category]: List of categories that have `name`.
        """
        models = self.scoped_session.query(Category).\
            filter(Category.name.like(f"%{name}%")).all()
        return models

    def find_by_name_containing_with_liked(self, name: str, user_id: int) -> list[CategoryWithRatingView]:
        """
        Finds all categories that have `name` and if user with `user_id` liked the category or not.

        Args:
            name (str): Name of categories.
            user_id (int): Id of user.

        Returns:
            list[CategoryWithRatingView]: List of categories that have `name` and if user with `user_id` liked the category or not.
        """
        # all categories containing name
        category_query = self.scoped_session.query(Category).filter(
            Category.name.like(f'%{name}%')).subquery()
        # liked categories of user with user_id
        liked_categories_query = self.scoped_session.query(
            LikedCategories.category_id).filter(LikedCategories.user_id == user_id).subquery()
        # left join categories containing name with liked categories of user with user_id
        models = self.scoped_session.query(category_query, liked_categories_query).\
            outerjoin(liked_categories_query,
                      liked_categories_query.c.category_id == category_query.c.id).all()
        views = [CategoryWithRatingView(
            model[0], model[1], model[2] is not None) for model in models]
        return views

    def find_liked_categories(self, user_id: int) -> list[Category]:
        """
        Finds all categories liked categories from user with `user_id`.

        Args:
            user_id (int): Id of user.

        Returns:
            list[Category]: List of categories with user rating from `user_id` that have `name`.
        """
        models = self.scoped_session.query(Category).\
            join(LikedCategories, LikedCategories.category_id == Category.id).\
            where(LikedCategories.user_id == user_id).all()
        return models
