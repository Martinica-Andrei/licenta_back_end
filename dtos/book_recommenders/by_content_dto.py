from dtos.converter import Converter


class ByContentDto:
    def __init__(self, content: str, authors: list[str], categories: list[str], user_id : int | None = None):
        self.content = content
        self.authors = authors
        self.categories = categories
        self.user_id = user_id

    @staticmethod
    def convert_from_dict(body: dict, user_id : int | None = None) -> "ByContentDto":
        """
        Converts dict to ByContentDto.

        Args:
            body (dict): Dictionary to be converted.

        Returns:
            ByContentDto.

        Raises:
            ValidationError: If any validation fails.
        """
        body = {k.lower(): v for k, v in body.items()}
        content = str(body['content']) if 'content' in body else ''
        categories = []
        authors = []
        if 'categories' in body:
            Converter.validate_is_list(body, 'categories')
            categories = [str(v) for v in body['categories']]
        if 'authors' in body:
            Converter.validate_is_list(body, 'authors')
            authors = [str(v) for v in body['authors']]
            
        return ByContentDto(content, authors, categories, user_id)