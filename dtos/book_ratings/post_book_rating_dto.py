from dtos.converter import Converter


class PostBookRatingDto:
    def __init__(self, user_id: int, book_id: int, rating: str):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating

    @staticmethod
    def convert_from_dict(body: dict, user_id: int) -> "PostBookRatingDto":
        """
        Converts dict to PostBookRatingDto.

        Args:
            body (dict): Dictionary to be converted.
            user_id (int): User id that rates book.

        Returns:
            PostBookRatingDto.

        Raises:
            ValidationError: If any validation fails.
        """
        body = {k.lower(): v for k, v in body.items()}

        Converter.validate_is_required(body, 'book_id')
        Converter.validate_is_required(body, 'rating')
        body['rating'] = str(body['rating']).lower()
        Converter.validate_has_value_in_list(
            body, 'rating', {'like', 'dislike', 'none'})
        return PostBookRatingDto(user_id, body['book_id'], body['rating'])
