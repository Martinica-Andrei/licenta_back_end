from dtos.converter import Converter
from load_book_recommendation_model import get_nr_items

class PostLikedCategoryDto:
    def __init__(self, category_id : int, user_id : int, like : bool):
        self.category_id = category_id
        self.user_id = user_id
        self.like = like

    @staticmethod
    def convert_from_dict(body: dict, user_id: int) -> "PostLikedCategoryDto":
        """
        Converts dict to PostLikedCategoryDto.

        Args:
            body (dict): Dictionary to be converted.
            user_id (int): The user that likes or not likes this category.

        Returns:
            PostLikedCategoryDto.

        Raises:
            ValidationError: If any validation fails.
        """
        
        Converter.validate_is_required(body, 'id')
        body['id'] = Converter.convert_int_from_dict(body, 'id')

        Converter.validate_is_required(body, 'like')
        is_like = Converter.convert_bool_from_dict(body, 'like')
        return PostLikedCategoryDto(body['id'], user_id, is_like)