from lightfm import LightFM
from pathlib import Path
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors

model : LightFM = joblib.load(Path('models/amazon-book-reviews-no-item-features-model.pkl'))
bias, components = model.get_item_representations() 
item_representations = np.concatenate([bias.reshape(-1,1), components], axis=1)
neighbors = NearestNeighbors(n_neighbors=6).fit(item_representations)
