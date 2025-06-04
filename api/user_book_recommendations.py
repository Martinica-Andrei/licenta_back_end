from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from db import db
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