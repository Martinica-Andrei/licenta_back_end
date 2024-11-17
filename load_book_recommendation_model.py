from lightfm import LightFM
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors
import utils

model : LightFM = joblib.load(utils.BOOKS_DATA_MODEL)
model.set_params(learning_schedule='adagrad')
neighbors = NearestNeighbors(n_neighbors=30)

def model_item_representations():
    bias, components = model.get_item_representations() 
    return np.concatenate([bias.reshape(-1,1), components], axis=1)

def refit_neighbors():
    global neighbors
    item_representations = model_item_representations()
    neighbors.fit(item_representations)

refit_neighbors()