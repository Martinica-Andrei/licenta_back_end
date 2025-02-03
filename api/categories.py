from flask import Blueprint, request
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
    query = db.session.query(Category.__table__.columns).filter(Category.name.like(f'%{name}%'))
    if current_user.is_authenticated:
        query = query.subquery()
        query1 = db.session.query(LikedCategories.category_id).filter(LikedCategories.user_id == current_user.id).subquery()
        query2 = db.session.query(query, query1).outerjoin(query1, query.c.id == query1.c.category_id)
        results = query2.all()
        df = pd.DataFrame(results).rename(columns={'category_id' : 'liked'})
        df.loc[df['liked'].isna() == False, 'liked'] = True
        df['liked'] = df['liked'].fillna(False)
    else:
        results = query.all()
        df = pd.DataFrame(results)
    return df.to_json(index=False, orient='records'), {'Content-Type': 'application/json'}

@categories_blueprint.get('/me')
@login_required
def me():
    results = db.session.query(LikedCategories.category_id, Category.name).filter(LikedCategories.user_id == current_user.id).join(
        Category, Category.id == LikedCategories.category_id).all()
    df = pd.DataFrame(results)
    return df.to_json(orient='records',index=False), {'Content-Type': 'application/json'}

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
    is_like = body['like'].lower()
    if is_like not in ['true', 'false']:
        return {"like": "Like must have value 'true' or 'false'!"}, 400
    liked_cat = db.session.query(LikedCategories).filter(sa.and_(LikedCategories.user_id == current_user.id, LikedCategories.category_id == id)).first()
    if is_like == 'true':
        if liked_cat is None:
            liked_cat = LikedCategories(category_id=id, user_id=current_user.id)
            db.session.add(liked_cat)
            db.session.commit()
    elif liked_cat is not None:
        db.session.delete(liked_cat)
        db.session.commit()
    return {}
