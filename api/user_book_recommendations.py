from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from db import db
from dtos.book_recommenders.training_status_dto import TrainingStatus
from services.book_recommender_service import BookRecommenderService
from .api import api_blueprint

blueprint = Blueprint('user_book_recommendations', __name__,
                             url_prefix='/user_book_recommendations')
api_blueprint.register_blueprint(blueprint)


@blueprint.get('/training_status')
@login_required
def training_status():
    book_recommender_service = BookRecommenderService(db.session)
    dto = book_recommender_service.validate_training_status(current_user.id)
    json = dto.to_json()
    return jsonify(json)


@blueprint.get("/recommendations")
@login_required
def recommendations():
    book_recommender_service = BookRecommenderService(db.session)
    validation_dto = book_recommender_service.validate_training_status(
        current_user.id)
    if validation_dto.training_status == TrainingStatus.MUST_TRAIN:
        json = validation_dto.to_json()
        return jsonify(json)
    dtos = book_recommender_service.get_recommendations_by_user(
        current_user.id)
    list_with_json = [dto.to_json() for dto in dtos]
    return jsonify(list_with_json)


@blueprint.post("train_logged_in_user")
@login_required
def train_logged_in_user():
    book_recommender_service = BookRecommenderService(db.session)
    validation_dto = book_recommender_service.validate_training_status(
        current_user.id)
    
    if validation_dto.training_status in [TrainingStatus.CANNOT_TRAIN, 
                                          TrainingStatus.CURRENTLY_TRAINING_OTHER_USER, 
                                          TrainingStatus.ALREADY_TRAINED]:
        json = validation_dto.to_json()
        return jsonify(json)
    
    if validation_dto.training_status == TrainingStatus.CURRENTLY_TRAINING_LOGGED_IN_USER:
        return book_recommender_service.get_training_progress(), {'content_type': 'Application/json'}
 
    book_recommender_service.train_on_single_user(current_user.id)
    return book_recommender_service.get_training_progress(), {'content_type': 'Application/json'}
