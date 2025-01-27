import re
from hashlib import sha256
from pathlib import Path


def convert_for_word_search(x : str):
    x = re.sub(r'[^A-Za-z0-9_]', ' ', x)
    x = x.strip()
    x = re.split(r'\s+', x)
    x_str = [f'+{v}*' for v in x]
    x_str = ' '.join(x_str)
    return (x_str, x)

BOOKS_DATA = Path('books_data')
BOOKS_DATA_MODEL = BOOKS_DATA / 'model_adagrad.pkl'
BOOKS_DATA_ITEM_FEATURES = BOOKS_DATA / 'item_features.npz'
BOOKS_DATA_USER_FEATURES = BOOKS_DATA / 'user_features.npz'
BOOKS_DATA_BOOKS_PROCESSED = BOOKS_DATA / 'books_processed.csv'
BOOKS_DATA_Y = BOOKS_DATA / 'y.npz'
BOOKS_DATA_NEGATIVE_RATINGS = BOOKS_DATA / 'negative_ratings.npz'
BOOKS_DATA_IMAGES = BOOKS_DATA / 'images'
BOOKS_AUTHORS = BOOKS_DATA / 'book_authors.csv'
BOOKS_CATEGORIES = BOOKS_DATA / 'categories.csv'

def string_list_to_list(x): 
    return [item.strip(' \'"') for item in x.strip('[]').split(',')]
