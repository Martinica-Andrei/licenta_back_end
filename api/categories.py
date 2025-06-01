from flask import Blueprint, request
from flask import jsonify
from services.category_service import CategoryService
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
    category_service = CategoryService(db.session)
    dtos = category_service.find_liked_categories(current_user.id)
    list_with_json = [dto.to_json() for dto in dtos]
    return jsonify(list_with_json)

@categories_blueprint.post("/like")
@login_required
def like_category():
    body = request.get_json()
    body = {k.lower(): v for k, v in body.items()} 
    if 'id' not in body:
        return {"id": "Id is required!"}, 400
    try:
        id = int(body['id'])
    except:
        return {"id": "Id must be an integer!"}, 400
    if id < 0 or id >= get_nr_items():
        return {"id": "Invalid id!"}, 400
    if 'like' not in body:
        return {"like": "Like is required!"}, 400
    is_like = body['like']
    if is_like not in [True, False]:
        return {"like": "Like must have value true or false!"}, 400
    liked_cat = db.session.query(LikedCategories).filter(sa.and_(LikedCategories.user_id == current_user.id, LikedCategories.category_id == id)).first()
    if is_like:
        if liked_cat is None:
            liked_cat = LikedCategories(category_id=id, user_id=current_user.id)
            db.session.add(liked_cat)
            db.session.commit()
    elif liked_cat is not None:
        db.session.delete(liked_cat)
        db.session.commit()
    return {}
