from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from db import db
from dtos.book_recommenders.training_status_dto import TrainingStatus
from services.book_recommender_service import BookRecommenderService
from .api import api_blueprint

models_blueprint = Blueprint('user_book_recommendations', __name__,
                             url_prefix='/user_book_recommendations')
api_blueprint.register_blueprint(models_blueprint)

@models_blueprint.get('/training_status')
@login_required
def training_status():
    book_recommender_service = BookRecommenderService(db.session)
    dto = book_recommender_service.validate_training_status(current_user.id)
    json = dto.to_json()
    return jsonify(json)


@models_blueprint.get("/recommendations")
@login_required
def recommendations():
    book_recommender_service = BookRecommenderService(db.session)
    validation_dto = book_recommender_service.validate_training_status(current_user.id)
    if validation_dto.training_status == TrainingStatus.MUST_TRAIN:
        json = validation_dto.to_json()
        return jsonify(json)
    dtos = book_recommender_service.get_recommendations_by_user(current_user.id)
    list_with_json = [dto.to_json() for dto in dtos]
    return jsonify(list_with_json)