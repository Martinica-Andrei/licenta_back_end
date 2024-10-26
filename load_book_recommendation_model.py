from lightfm import LightFM
from pathlib import Path
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors
import utils

model : LightFM = joblib.load(utils.BOOKS_DATA_MODEL)
bias, components = model.get_item_representations() 
item_representations = np.concatenate([bias.reshape(-1,1), components], axis=1)
neighbors = NearestNeighbors(n_neighbors=12).fit(item_representations)
