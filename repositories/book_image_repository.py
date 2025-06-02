import base64
from pathlib import Path
import utils


class BookImageRepository:

    @staticmethod
    def convert_image_base64(filename: str | Path) -> str | None:
        """
        Finds image and converts it to base64.

        Args:
            filename (str | Path): Image filepath to convert.

        Returns:
            str | None.
        """
        if type(filename) not in [str, Path]:
            return None
        filepath: Path = utils.BOOKS_DATA_IMAGES / filename
        if filepath.is_file():
            with open(filepath, 'rb') as file:
                binary_data = file.read()
                base64_bytes = base64.b64encode(binary_data)
                base64_str = base64_bytes.decode('utf-8')
                return base64_str
        else:
            return None
