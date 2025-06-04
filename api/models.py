# from flask import Blueprint, g, json

# from repositories.book_image_repository import BookImageRepository
# from repositories.book_recommender_repository import BookRecommenderRepository
# from repositories.user_repository import UserRepository
# from .api import api_blueprint
# from db import db
# from lightfm import LightFM
# import numpy as np
# from scipy.sparse import csr_matrix, hstack, vstack, identity
# import joblib
# import utils
# from db_models.book import Book
# from db_models.book_rating import BookRating
# import pandas as pd
# import threading
# from flask_login import login_required, current_user
# import sqlalchemy as sa
# from custom_precision_at_k import custom_precision_at_k
# from thread_locks import books_model_memory_change_lock
# from repositories.lightfm_repository import LightfmRepository

# models_blueprint = Blueprint('models', __name__,
#                              url_prefix='/models')
# api_blueprint.register_blueprint(models_blueprint)

# books_train_on_user_lock = threading.Lock()

# TARGET_PRECISION = 0.4
# MINIMUM_POSITIVE_RATINGS = 1

# def get_user_categories(user_id):
#     categories = UserRepository(db.session).find_liked_categories(user_id)
#     categories = pd.Series([[x.name for x in categories]])
#     return user_preprocessing().transform(categories)[0]

# def concat_categories_user_feature(categories, user_id):
#     user_feature = user_features()[user_id]
#     nr_common_features = get_length_common_features_users()
#     return hstack([categories, user_feature[:, nr_common_features:]])


# # get feature of single user and add preprocessing features (categories)
# def create_single_user_feature(user_id):
#     return concat_categories_user_feature(get_user_categories(user_id), user_id)

# def compute_user_precision(model, nr_positive_ratings, y, item_features, user_features):
#     # k = nr_positive_ratings because precision is computed for all items here
#     return custom_precision_at_k(model, y, item_features=item_features, user_features=user_features, 
#                                  k=nr_positive_ratings, num_threads=12).mean()


# def model_books_train_on_user(positive_book_ratings, user_id, user_categories):
#     with books_train_on_user_lock:
#         LightfmRepository.add_new_users(user_id)
#         LightfmRepository.reset_user_gradients(user_id)

#         user_feature = concat_categories_user_feature(user_categories, user_id)
#         single_user_model = LightfmRepository.new_model_with_single_user(user_feature)

#         y = BookRecommenderRepository.convert_positive_book_ratings_to_csr(positive_book_ratings)
        
#         user_feature_ones = csr_matrix(user_feature.data)
        
#         max_percentage = 0
#         precision = compute_user_precision(
#             single_user_model, len(positive_book_ratings), y, item_features=item_features(), user_features=user_feature_ones)
#         print("start training")
#         while precision < TARGET_PRECISION:
#             single_user_model.fit_partial(y, item_features=item_features(), user_features=user_feature_ones, epochs=1000, num_threads=12)
#             precision = compute_user_precision(
#                 single_user_model, len(positive_book_ratings), y, item_features=item_features(), user_features=user_feature_ones)
#             print("precision: ", precision)
#             percentage = round(precision / TARGET_PRECISION, 2)
#             percentage = min(1, percentage)
#             if percentage > max_percentage:
#                 max_percentage = percentage
#                 data = {'percentage': max_percentage}
#                 yield json.dumps(data) + '\n'
#         with books_model_memory_change_lock.gen_wlock():
#             LightfmRepository.transfer_data_from_new_model_to_model(
#                 single_user_model, model, user_feature)
#             refit_neighbors()
#             joblib.dump(model, utils.BOOKS_DATA_MODEL)


# def validate_training_status(user_id):
#     positive_book_ratings = db.session.query(BookRating.book_id).filter(sa.and_(
#         BookRating.user_id == user_id, BookRating.rating == 'Like')).all()
#     positive_book_ratings = [x[0] for x in positive_book_ratings]
#     g.positive_book_ratings = positive_book_ratings
#     if len(positive_book_ratings) < MINIMUM_POSITIVE_RATINGS:
#         return {"cannot_train": f"Minimum {MINIMUM_POSITIVE_RATINGS} positive ratings are required for recommendations. Like" +
#                 f" {MINIMUM_POSITIVE_RATINGS - len(positive_book_ratings)} more books."}
#     with books_model_memory_change_lock.gen_rlock():
#         if LightfmRepository.is_user_added(user_id) == False:
#             return {"must_train": True}
#         y = BookRecommenderRepository.convert_positive_book_ratings_to_csr(positive_book_ratings)
#         user_feature = create_single_user_feature(user_id)
#         precision = compute_user_precision(model, len(positive_book_ratings), y, item_features(), user_feature)
#     if precision < 0.2:
#         return {"must_train": True}
#     if precision < TARGET_PRECISION:
#         return {"can_train": True}
#     else:
#         return {"can_train": False}


# @models_blueprint.get('books/training_status')
# @login_required
# def training_status():
#     return validate_training_status(current_user.id)


# @models_blueprint.get('books/user_train')
# @login_required
# def user_train():
#     validation = validate_training_status(current_user.id)
#     if 'cannot_train' in validation or validation.get('can_train', True) == False:
#         return validation
#     user_categories = get_user_categories(current_user.id)
#     v = model_books_train_on_user(g.positive_book_ratings, current_user.id, user_categories)
#     return v, {'content_type': 'Application/json'}


# @models_blueprint.get("/books/user_recommendations")
# @login_required
# def books_recommendations():
#     validation = validate_training_status(current_user.id)
#     if 'cannot_train' in validation or validation.get('must_train', False) == True:
#         return validation
#     books_not_to_show = np.array(
#         [rating.book_id for rating in current_user.book_ratings])

#     with books_model_memory_change_lock.gen_rlock():
#         books_indices = np.arange(get_nr_items())
#         user_feature = create_single_user_feature(current_user.id)
#         user_features_ = user_features()
#         user_features_[current_user.id] = user_feature[0]
#         predictions = model.predict(current_user.id, books_indices, item_features=item_features(), user_features=user_features_)
#     prediction_indices_sorted = np.argsort(-predictions)
#     prediction_indices_sorted = prediction_indices_sorted[np.isin(
#         prediction_indices_sorted, books_not_to_show) == False]

#     p_indices_sorted = prediction_indices_sorted[:100].tolist()

#     books = db.session.query(Book.id, Book.title, Book.image_link, Book.link, Book.nr_likes, Book.nr_dislikes).filter(
#         Book.id.in_(p_indices_sorted))

#     df = pd.DataFrame(books)
#     df.rename(columns={'image_link': 'image'}, inplace=True)
#     df['image'] = df['image'].apply(lambda x : BookImageRepository.convert_image_base64(x))
#     df.set_index('id', inplace=True)
#     df = df.reindex(index=p_indices_sorted)
#     df.reset_index(inplace=True)
#     return df.to_json(orient='records'), {'Content-Type': 'application/json'}
