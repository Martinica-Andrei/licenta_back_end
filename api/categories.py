from flask import Blueprint, request
from flask import jsonify
from dtos.converter import ValidationError
from dtos.liked_categories.post_liked_category_dto import PostLikedCategoryDto
from services.category_service import CategoryService
from services.liked_category_service import LikedCategoryService
from .api import api_blueprint
from flask_login import login_required, current_user
from db import db
import sqlalchemy as sa
from db_models.category import Category
import pandas as pd
from load_book_recommendation_model import get_nr_items
from db_models import LikedCategories

categories_blueprint = Blueprint('categories', __name__,
                         url_prefix='/categories')
api_blueprint.register_blueprint(categories_blueprint)


@categories_blueprint.get("/")
def index():
    """Gets categories that contain `name`, if user is logged in, also gets if user liked."""
    name = request.args.get('name', '')
    category_service = CategoryService(db.session)
    if current_user.is_authenticated:
        dtos = category_service.find_by_name_containing_with_liked(name, current_user.id)
    else:
        dtos = category_service.find_by_name_containing(name)
    list_with_json = [dto.to_json() for dto in dtos]
    return jsonify(list_with_json)

@categories_blueprint.get('/me')
@login_required
def me():
    """Gets all categories that user liked."""
    category_service = CategoryService(db.session)
    dtos = category_service.find_liked_categories(current_user.id)
    list_with_json = [dto.to_json() for dto in dtos]
    return jsonify(list_with_json)

@categories_blueprint.post("/like")
@login_required
def like_category():
    """User likes category or removes category."""
    body = request.get_json()
    try:
        dto = PostLikedCategoryDto.convert_from_dict(body, current_user.id)
    except ValidationError as err:
        return err.to_tuple()
    liked_category_service = LikedCategoryService(db.session)
    liked_category_service.update(dto)
    return {}