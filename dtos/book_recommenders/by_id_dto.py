from dtos.converter import Converter


class ByIdDto:
    def __init__(self, id : int, user_id : int | None = None):
        self.book_id = id
        self.user_id = user_id

    @staticmethod
    def convert_from_dict(body: dict, user_id : int | None = None) -> "ByIdDto":
        """
        Converts dict to ByIdDto.

        Args:
            body (dict): Dictionary to be converted.

        Returns:
            ByIdDto.

        Raises:
            ValidationError: If any validation fails.
        """
        Converter.validate_is_required(body, 'id')
        id_ = Converter.convert_int_from_dict(body, 'id')

        return ByIdDto(id_, user_id)
