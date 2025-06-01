from dtos.converter import Converter


class SearchBookDto:
    def __init__(self, title: str, count: int):
        self.title = title
        self.count = count

    @staticmethod
    def convert_from_dict(body: dict, default_title: str, default_count: int) -> "SearchBookDto":
        """
        Converts dict to SearchBookDto.

        Args:
            body (dict): Dictionary to be converted.
            default_title (str): Default if title not in `body`.
            default_count (int): Default if count not in `body`.

        Returns:
            SearchBookDto.

        Raises:
            ValidationError: If any validation fails.
        """
        title = body['title'] if 'title' in body else default_title
        count = default_count
        if "count" in body:
            count = Converter.convert_int_from_dict(body, 'count')
        return SearchBookDto(title, count)
