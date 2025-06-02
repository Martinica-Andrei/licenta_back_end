from dtos.converter import Converter


class BookRecommendationByIdDto:
    def __init__(self, id : int):
        self.id = id

    @staticmethod
    def convert_from_dict(body: dict) -> "BookRecommendationByIdDto":
        """
        Converts dict to BookRecommendationByIdDto.

        Args:
            body (dict): Dictionary to be converted.

        Returns:
            BookRecommendationByIdDto.

        Raises:
            ValidationError: If any validation fails.
        """
        id_ = Converter.convert_int_from_dict(body, 'id')

        return BookRecommendationByIdDto(id_)
