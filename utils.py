from pathlib import Path

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
