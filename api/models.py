from flask import Blueprint, g, json
from .api import api_blueprint
from db import db
from lightfm import LightFM
import numpy as np
from load_book_recommendation_model import (model,
                                            item_features,
                                            user_features,
                                            refit_neighbors,
                                            get_nr_items,
                                            get_nr_users,
                                            get_nr_items_features,
                                            get_nr_user_features, 
                                            get_length_common_features_items, 
                                            get_length_common_features_users,
                                            set_item_features,
                                            set_user_features,
                                            user_preprocessing)
from scipy.sparse import csr_matrix, hstack, vstack, identity
import joblib
import utils
from db_models.book import Book
from db_models.book_rating import BookRating
from db_models import LikedCategories
from db_models import Category
import pandas as pd
import threading
from flask_login import login_required, current_user
import sqlalchemy as sa
from custom_precision_at_k import custom_precision_at_k
from thread_locks import books_model_memory_change_lock

models_blueprint = Blueprint('models', __name__,
                             url_prefix='/models')
api_blueprint.register_blueprint(models_blueprint)

books_train_on_user_lock = threading.Lock()

TARGET_PRECISION = 0.4
MINIMUM_POSITIVE_RATINGS = 0

def add_new_users(model: LightFM, user_id):

    # nr_users for user_features
    nr_users = get_nr_users()
    nr_users_to_add = user_id - (nr_users - 1)
    if nr_users_to_add > 0:
        user_features_hstack = hstack([user_features(), csr_matrix((user_features().shape[0], nr_users_to_add))])
        new_user_features = identity(nr_users_to_add)
        new_user_features = hstack([csr_matrix((nr_users_to_add, user_features().shape[1])), new_user_features])
        new_user_features = vstack([user_features_hstack, new_user_features])
        new_user_features = csr_matrix(new_user_features)
        set_user_features(new_user_features)
    # nr_users for model_embeddings
    unique_embeddings_len = model.user_embeddings.shape[0] - get_length_common_features_users()
    nr_users_to_add = user_id - (unique_embeddings_len - 1)
    if nr_users_to_add > 0:
        add_new_user_embeddings(model, nr_users_to_add)


def add_new_user_embeddings(model: LightFM, nr_users_to_add):
    new_user_embedding_gradients = np.zeros(
        (nr_users_to_add, model.no_components))
    new_user_embedding_momentum = np.zeros(
        (nr_users_to_add, model.no_components))

    new_user_bias_gradients = np.zeros(nr_users_to_add)
    zeros_bias = np.zeros(nr_users_to_add)

    if model.learning_schedule == "adagrad":
        new_user_embedding_gradients += 1
        new_user_bias_gradients += 1

    random_state = model.random_state
    no_components = model.no_components

    model.user_embeddings = np.concatenate([model.user_embeddings, (random_state.rand(nr_users_to_add, no_components) - 0.5)
            / no_components], axis=0, dtype=np.float32)
    model.user_embedding_gradients = np.concatenate(
        [model.user_embedding_gradients, new_user_embedding_gradients], axis=0, dtype=np.float32)
    model.user_embedding_momentum = np.concatenate(
        [model.user_embedding_momentum, new_user_embedding_momentum], axis=0, dtype=np.float32)
    model.user_biases = np.concatenate(
        [model.user_biases, zeros_bias], axis=0, dtype=np.float32)
    model.user_bias_gradients = np.concatenate(
        [model.user_bias_gradients, new_user_bias_gradients], axis=0, dtype=np.float32)
    model.user_bias_momentum = np.concatenate(
        [model.user_bias_momentum, zeros_bias], axis=0, dtype=np.float32)


def reset_user_gradients(user_id):
    nr_common_features = get_length_common_features_users()
    model.user_embedding_gradients[nr_common_features + user_id] = np.ones(model.no_components)
    model.user_bias_gradients[nr_common_features + user_id] = 1


def new_model_with_single_user(user_feature):
    user_feature = user_feature.nonzero()[1]
    new_model = LightFM()
    new_model.set_params(**model.get_params())
    new_model.item_biases = model.item_biases.copy()
    new_model.item_embeddings = model.item_embeddings.copy()

    new_model.item_bias_gradients = model.item_bias_gradients.copy()
    new_model.item_embedding_gradients = model.item_embedding_gradients.copy()
    new_model.item_bias_momentum = model.item_bias_momentum.copy()
    new_model.item_embedding_momentum = model.item_embedding_momentum.copy()

    new_model.user_biases = model.user_biases[user_feature].copy()
    new_model.user_embeddings = model.user_embeddings[user_feature].copy(
    )

    new_model.user_bias_gradients = model.user_bias_gradients[user_feature].copy(
    )
    new_model.user_embedding_gradients = model.user_embedding_gradients[user_feature].copy(
    )
    new_model.user_bias_momentum = model.user_bias_momentum[user_feature].copy(
    )
    new_model.user_embedding_momentum = model.user_embedding_momentum[user_feature].copy(
    )

    return new_model


def transfer_data_from_new_model_to_model(new_model, model, user_feature):
    user_feature = user_feature.nonzero()[1]
    model.item_biases = new_model.item_biases.copy()
    model.item_embeddings = new_model.item_embeddings.copy()

    model.item_bias_gradients = new_model.item_bias_gradients.copy()
    model.item_embedding_gradients = new_model.item_embedding_gradients.copy()
    model.item_bias_momentum = new_model.item_bias_momentum.copy()
    model.item_embedding_momentum = new_model.item_embedding_momentum.copy()

    model.user_biases[user_feature] = new_model.user_biases.copy()
    model.user_embeddings[user_feature] = new_model.user_embeddings.copy()

    model.user_bias_gradients[user_feature] = new_model.user_bias_gradients.copy()
    model.user_embedding_gradients[user_feature] = new_model.user_embedding_gradients.copy()
    model.user_bias_momentum[user_feature] = new_model.user_bias_momentum.copy()
    model.user_embedding_momentum[user_feature] = new_model.user_embedding_momentum.copy()
    
def get_user_categories(user_id):
    # sqlalchemy must have columns from all joins therefore include LikedCategories.category_id
    # then discard it
    categories = db.session.query(LikedCategories.category_id, Category.name).filter(LikedCategories.user_id == user_id).join(
        Category, Category.id == LikedCategories.category_id).all()
    categories = pd.Series([[x.name for x in categories]])
    return user_preprocessing().transform(categories)[0]

def concat_categories_user_feature(categories, user_id):
    user_feature = user_features()[user_id]
    nr_common_features = get_length_common_features_users()
    return hstack([categories, user_feature[:, nr_common_features:]])


# get feature of single user and add preprocessing features (categories)
def create_single_user_feature(user_id):
    return concat_categories_user_feature(get_user_categories(user_id), user_id)


def is_user_added(user_id):
    unique_embeddings_len = model.user_embeddings.shape[0] - get_length_common_features_users()
    return user_id < unique_embeddings_len


def convert_positive_book_ratings_to_csr(positive_book_ratings, nr_users, user_id):
    ones = np.ones_like(positive_book_ratings)
    user_id_arr = np.full_like(ones, user_id)

    nr_books = get_nr_items()
    y = csr_matrix((ones, (user_id_arr, positive_book_ratings)),
                   shape=(nr_users, nr_books), dtype=int)
    return y


def compute_user_precision(model, nr_positive_ratings, y, item_features, user_features):

    return custom_precision_at_k(model, y, item_features=item_features, user_features=user_features, 
                                 k=nr_positive_ratings, num_threads=8).mean()


def model_books_train_on_user(positive_book_ratings, user_id, user_categories):
    with books_train_on_user_lock:
        add_new_users(model, user_id)
        reset_user_gradients(user_id)

        user_feature = concat_categories_user_feature(user_categories, user_id)
        single_user_model = new_model_with_single_user(user_feature)

        y = convert_positive_book_ratings_to_csr(
            positive_book_ratings, 1, 0)
        
        user_feature_ones = csr_matrix(user_feature.data)
        
        max_percentage = 0
        precision = compute_user_precision(
            single_user_model, len(positive_book_ratings), y, item_features=item_features(), user_features=user_feature_ones)
        while precision < TARGET_PRECISION:
            single_user_model.fit_partial(y, item_features=item_features(), user_features=user_feature_ones, epochs=10, num_threads=8)
            precision = compute_user_precision(
                single_user_model, len(positive_book_ratings), y, item_features=item_features(), user_features=user_feature_ones)
            percentage = round(precision / TARGET_PRECISION, 2)
            percentage = min(1, percentage)
            if percentage > max_percentage:
                max_percentage = percentage
                data = {'percentage': max_percentage}
                yield json.dumps(data) + '\n'
        with books_model_memory_change_lock.gen_wlock():
            transfer_data_from_new_model_to_model(
                single_user_model, model, user_feature)
            refit_neighbors()
            joblib.dump(model, utils.BOOKS_DATA_MODEL)


def validate_training_status(user_id):
    positive_book_ratings = db.session.query(BookRating.book_id).filter(sa.and_(
        BookRating.user_id == user_id, BookRating.rating == 'Like')).all()
    positive_book_ratings = [x[0] for x in positive_book_ratings]
    g.positive_book_ratings = positive_book_ratings
    if len(positive_book_ratings) < MINIMUM_POSITIVE_RATINGS:
        return {"cannot_train": f"Minimum {MINIMUM_POSITIVE_RATINGS} positive ratings are required for recommendations. Like" +
                f" {MINIMUM_POSITIVE_RATINGS - len(positive_book_ratings)} more books."}
    with books_model_memory_change_lock.gen_rlock():
        if is_user_added(user_id) == False:
            return {"must_train": True}
        y = convert_positive_book_ratings_to_csr(
            positive_book_ratings, get_nr_users(), user_id)
        user_feature = create_single_user_feature(user_id)
        user_features_ = user_features()
        user_features_[user_id] = user_feature[0]
        precision = compute_user_precision(
            model, len(positive_book_ratings), y, item_features=item_features(), user_features=user_features_)
    if precision < 0.2:
        return {"must_train": True}
    if precision < TARGET_PRECISION:
        return {"can_train": True}
    else:
        return {"can_train": False}


@models_blueprint.get('books/training_status')
@login_required
def training_status():
    return validate_training_status(current_user.id)


@models_blueprint.get('books/user_train')
@login_required
def user_train():
    validation = validate_training_status(current_user.id)
    if 'cannot_train' in validation or validation.get('can_train', True) == False:
        return validation
    user_categories = get_user_categories(current_user.id)
    v = model_books_train_on_user(g.positive_book_ratings, current_user.id, user_categories)
    return v, {'content_type': 'Application/json'}


@models_blueprint.get("/books/user_recommendations")
@login_required
def books_recommendations():
    validation = validate_training_status(current_user.id)
    if 'cannot_train' in validation or validation.get('must_train', False) == True:
        return validation
    books_not_to_show = np.array(
        [rating.book_id for rating in current_user.book_ratings])

    with books_model_memory_change_lock.gen_rlock():
        books_indices = np.arange(get_nr_items())
        user_feature = create_single_user_feature(current_user.id)
        user_features_ = user_features()
        user_features_[current_user.id] = user_feature[0]
        predictions = model.predict(current_user.id, books_indices, item_features=item_features(), user_features=user_features_)
    prediction_indices_sorted = np.argsort(-predictions)
    prediction_indices_sorted = prediction_indices_sorted[np.isin(
        prediction_indices_sorted, books_not_to_show) == False]

    p_indices_sorted = prediction_indices_sorted[:100].tolist()

    books = db.session.query(Book.id, Book.title, Book.image_link, Book.link, Book.nr_likes, Book.nr_dislikes).filter(
        Book.id.in_(p_indices_sorted))

    df = pd.DataFrame(books)
    df.rename(columns={'image_link': 'image'}, inplace=True)
    df['image'] = df['image'].apply(Book.get_image_base64)
    df.set_index('id', inplace=True)
    df = df.reindex(index=p_indices_sorted)
    df.reset_index(inplace=True)
    return df.to_json(orient='records'), {'Content-Type': 'application/json'}
