from flask import Blueprint, g, jsonify
from .api import api_blueprint
from db import db
from lightfm import LightFM
import numpy as np
from load_book_recommendation_model import model
from scipy.sparse import csr_matrix
import joblib
import utils
from db_models.book import Book
import pandas as pd
import threading
from flask_login import login_required, current_user

models_blueprint = Blueprint('models', __name__,
                            url_prefix='/models')
api_blueprint.register_blueprint(models_blueprint)

books_train_on_user_lock = threading.Lock()

def add_new_users(model : LightFM, user_id):

    nr_users = model.get_user_representations()[0].shape[0]
    nr_users_to_add = user_id - (nr_users - 1)
    if nr_users_to_add <= 0:
        return
    
    new_user_embedding_gradients = np.zeros((nr_users_to_add, model.no_components))
    new_user_embedding_momentum = np.zeros((nr_users_to_add, model.no_components))

    new_user_bias_gradients = np.zeros(nr_users_to_add)
    zeros_bias = np.zeros(nr_users_to_add)

    if model.learning_schedule == "adagrad":
        new_user_embedding_gradients += 1
        new_user_bias_gradients += 1

    model.user_embeddings = np.concatenate([model.user_embeddings, np.random.rand(nr_users_to_add, model.no_components)], axis=0, dtype=np.float32)
    model.user_embedding_gradients = np.concatenate([model.user_embedding_gradients, new_user_embedding_gradients], axis=0, dtype=np.float32)
    model.user_embedding_momentum = np.concatenate([model.user_embedding_momentum, new_user_embedding_momentum], axis=0, dtype=np.float32)
    model.user_biases = np.concatenate([model.user_biases, zeros_bias], axis=0, dtype=np.float32)
    model.user_bias_gradients = np.concatenate([model.user_bias_gradients, new_user_bias_gradients], axis=0, dtype=np.float32)
    model.user_bias_momentum = np.concatenate([model.user_bias_momentum, zeros_bias], axis=0, dtype=np.float32)


def reset_user_gradients(user_id):
    model.user_embedding_gradients[user_id] = np.ones(model.no_components)
    model.user_bias_gradients[user_id] = 1

def is_user_added(model, user_id):
    nr_users = model.get_user_representations()[0].shape[0]
    return user_id < nr_users

def model_books_train_on_user(positive_book_ratings, user_id):
    with books_train_on_user_lock:
        if is_user_added(model, user_id) == False:
            add_new_users(model, user_id)
        reset_user_gradients(user_id)

        ones = np.ones_like(positive_book_ratings)
        user_id_arr = np.full_like(ones, user_id)

        nr_books = model.get_item_representations()[0].shape[0]
        nr_users = model.get_user_representations()[0].shape[0]
        y = csr_matrix((ones, (user_id_arr, positive_book_ratings)), shape=(nr_users, nr_books), dtype=int)

        epochs = 1000
        previous_percent = 0
        for i in range(1, epochs + 1):
            model.fit_partial(y, epochs=1, num_threads=8)
            percent = i / epochs
            if percent - previous_percent >= 0.01:
                previous_percent = percent
                yield f"{round(percent, 2)}\n"
        joblib.dump(model, utils.BOOKS_DATA_MODEL)
    
@models_blueprint.post("/books/user_train")
@login_required
def books_train_on_user():
    positive_book_ratings = np.array([rating.book_id for rating in current_user.book_ratings if rating.rating == 'Like'])
    if len(positive_book_ratings) < 5:
        return {"err" : "Minimum 5 positive ratings are required for training!"}, 400
    return model_books_train_on_user(positive_book_ratings, current_user.id)

@models_blueprint.get("/books/user_recommendations")
@login_required
def books_recommendations():
    if is_user_added(model, current_user.id) == False:
        return {"err" : "First train model!"}, 400
    books_not_to_show = np.array([rating.book_id for rating in current_user.book_ratings])

    nr_books = model.get_item_representations()[0].shape[0]
    books_indices = np.arange(nr_books)

    predictions = model.predict(current_user.id, books_indices)
    prediction_indices_sorted = np.argsort(-predictions)
    prediction_indices_sorted = prediction_indices_sorted[np.isin(prediction_indices_sorted, books_not_to_show) == False]

    p_indices_sorted = prediction_indices_sorted[:100].tolist()

    books = db.session.query(Book).filter(Book.id.in_(p_indices_sorted))
    books = [{'id' : book.id, 'title' : book.title} for book in books]
    
    df = pd.DataFrame(books)
    df.set_index('id', inplace=True)
    df = df.reindex(index=p_indices_sorted)
    df.reset_index(inplace=True)
    return df.to_json(orient='records'), {'Content-Type': 'application/json'}