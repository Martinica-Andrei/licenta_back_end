from lightfm import LightFM
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors
import utils

model : LightFM = joblib.load(utils.BOOKS_DATA_MODEL)
model.set_params(learning_schedule='adagrad')
bias, components = model.get_item_representations() 
item_representations = np.concatenate([bias.reshape(-1,1), components], axis=1)
neighbors = NearestNeighbors(n_neighbors=30).fit(item_representations)
