from dtos.converter import Converter


class BookRecommendationByContentDto:
    def __init__(self, content: str, authors: list[str], categories: list[str]):
        self.content = content
        self.authors = authors
        self.categories = categories

    @staticmethod
    def convert_from_dict(body: dict) -> "BookRecommendationByContentDto":
        """
        Converts dict to BookRecommendationByContentDto.

        Args:
            body (dict): Dictionary to be converted.

        Returns:
            BookRecommendationByContentDto.

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
            
        return BookRecommendationByContentDto(content, authors, categories)