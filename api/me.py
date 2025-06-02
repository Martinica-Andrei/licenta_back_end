from flask import Blueprint, jsonify
from db import db
from services.user_service import UserService
from .api import api_blueprint
from flask_login import login_required, current_user

me_blueprint = Blueprint('me', __name__,
                         url_prefix='/me')
api_blueprint.register_blueprint(me_blueprint)


@me_blueprint.get("/")
@login_required
def index():
    user_service = UserService(db.session)
    dto = user_service.find_by_id_with_book_rating(current_user.id)
    json = dto.to_json()
    return jsonify(json)
