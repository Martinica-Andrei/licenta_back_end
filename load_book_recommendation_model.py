from lightfm import LightFM
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import load_npz, save_npz, csr_matrix
import utils
from most_common_words import MostCommonWords
from sklearn.compose import ColumnTransformer

model : LightFM = joblib.load(utils.BOOKS_DATA_MODEL)
neighbors = NearestNeighbors(n_neighbors=30, metric='cosine')

_item_features = csr_matrix(load_npz(utils.BOOKS_DATA_ITEM_FEATURES))
_user_features = csr_matrix(load_npz(utils.BOOKS_DATA_USER_FEATURES))

_user_preprocessing : MostCommonWords
_item_preprocessing : ColumnTransformer

def load_user_preprocessing():
    global _user_preprocessing
    _user_preprocessing = joblib.load(utils.BOOKS_DATA_USER_PREPROCESSING)

def load_item_preprocessing():
    global _item_preprocessing
    _item_preprocessing = joblib.load(utils.BOOKS_DATA_ITEM_PREPROCESSING)


def user_preprocessing():
    return _user_preprocessing

def item_preprocessing():
    return _item_preprocessing

def model_item_representations() -> np.ndarray:
    """Returns the concatenation between bias and embedding for each item from `model`."""
    bias, components = model.get_item_representations(_item_features) 
    return np.concatenate([bias.reshape(-1,1), components], axis=1)

def refit_neighbors():
    global neighbors
    item_representations = model_item_representations()
    neighbors.fit(item_representations)

refit_neighbors()

def item_features():
    return _item_features

def user_features():
    return _user_features

def set_item_features(item_features):
    global _item_features
    _item_features = item_features
    save_npz(utils.BOOKS_DATA_ITEM_FEATURES, _item_features)

def set_user_features(user_features):
    global _user_features
    _user_features = user_features
    save_npz(utils.BOOKS_DATA_USER_FEATURES, _user_features)

def get_nr_users():
    return _user_features.shape[0]

def get_nr_user_features():
    return _user_features.shape[1]

def get_nr_items():
    return _item_features.shape[0]

def get_nr_items_features():
    return _item_features.shape[1]

def get_length_common_features_items():
    #each item has 1 unique feature
    #therefore by subtracting nr items from features results in number ofcommon features
    return get_nr_items_features() - get_nr_items()

def get_length_common_features_users():
    #each user has 1 unique feature
    #therefore by subtracting nr user from features results in number of common features
    return get_nr_user_features() - get_nr_users()