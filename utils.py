from pathlib import Path

import numpy as np
import pandas as pd

BOOKS_DATA = Path('books_data')
BOOKS_DATA_MODEL = BOOKS_DATA / 'model_adagrad_200.pkl'
BOOKS_DATA_ITEM_FEATURES = BOOKS_DATA / 'item_features.npz'
BOOKS_DATA_USER_FEATURES = BOOKS_DATA / 'user_features.npz'
BOOKS_DATA_BOOKS_PROCESSED = BOOKS_DATA / 'books_processed.csv'
BOOKS_DATA_Y = BOOKS_DATA / 'y.npz'
BOOKS_DATA_NEGATIVE_RATINGS = BOOKS_DATA / 'negative_ratings.npz'
BOOKS_DATA_IMAGES = BOOKS_DATA / 'images'
BOOKS_AUTHORS = BOOKS_DATA / 'book_authors.csv'
BOOKS_CATEGORIES = BOOKS_DATA / 'categories.csv'
BOOKS_DATA_USER_PREPROCESSING = BOOKS_DATA / 'user_processing.pkl'
BOOKS_DATA_ITEM_PREPROCESSING = BOOKS_DATA / 'item_preprocessing.pkl'


def string_list_to_list(x):
    return [item.strip(' \'"') for item in x.strip('[]').split(',')]


def replace_no_photo_link(s: pd.Series) -> pd.Series:
    """
    Replaces `s` pd.Series no photo link with np.nan

    Args:
        s (pd.Series): Pandas series to replace no photo link

    Returns:
        pd.Series: Series with no photo link replaced with np.nan.
    """
    no_photo_link = 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png'
    return s.replace({no_photo_link: np.nan})

__base_url = 'https://images.gr-assets.com/books/'

def process_book_scraped_url(url : str) -> str:
    """
    Processes `url` by removing leaving only name and replaces / with - ."

    Args:
        url (str): Url to process.
    
    Returns:
        str: Processed url.s
    """
    if type(url) is str:
        return url.replace(__base_url, '').replace('/', '-')
    return url