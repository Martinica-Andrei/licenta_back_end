from sqlalchemy.orm.scoping import scoped_session
from db_models.liked_categories import LikedCategories
from sqlalchemy import and_


class LikedCategoryRepository:
    def __init__(self, scoped_session: scoped_session):
        self.scoped_session = scoped_session

    def find_by_user_id_category_id(self, user_id: int, category_id: int) -> LikedCategories | None:
        """
        Finds liked_category that belongs to `user_id` for `category_id`.

        Args:
            user_id (int): The user that likes `category_id`.
            category_id (int): The category liked by `user_id`.

        Returns:
            LikedCategories | None
        """
        return self.scoped_session.query(LikedCategories).\
            where(and_(LikedCategories.user_id == user_id,
                       LikedCategories.category_id == category_id)).first()

    def create(self, model: LikedCategories) -> LikedCategories:
        """
        Creates liked_category in db.

        Args:
            model (LikedCategories): Model to create.

        Returns:
            LikedCategories: Updated model from db.
        """
        self.scoped_session.add(model)
        self.scoped_session.commit()
        return model

    def delete(self, model: LikedCategories) -> None:
        """
        Deletes liked_category in db.

        Args:
            model (LikedCategories): Model to delete.

        Returns:
            LikedCategories: Updated model from db.
        """
        self.scoped_session.delete(model)
        self.scoped_session.commit()
