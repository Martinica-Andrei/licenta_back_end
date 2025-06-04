
import joblib
from most_common_words import MostCommonWords
from utils import BOOKS_DATA_USER_PREPROCESSING


class UserPreprocessingRepository:

    __preprocessing : MostCommonWords =  joblib.load(BOOKS_DATA_USER_PREPROCESSING)

    def __init__(self):
        """No attributes."""

    def get_preprocessing(self) -> MostCommonWords:
        return UserPreprocessingRepository.__preprocessing