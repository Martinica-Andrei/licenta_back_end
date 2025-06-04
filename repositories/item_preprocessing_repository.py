import joblib
from sklearn.compose import ColumnTransformer
from utils import BOOKS_DATA_ITEM_PREPROCESSING


class ItemPreprocessingRepository:

    __preprocessing: ColumnTransformer = joblib.load(
        BOOKS_DATA_ITEM_PREPROCESSING)

    def __init__(self):
        """No attributes."""

    def get_preprocessing(self) -> ColumnTransformer:
        return ItemPreprocessingRepository.__preprocessing

 