from flask import Blueprint, request
from .api import api_blueprint
from flask_login import login_required, current_user
from db import db
import sqlalchemy as sa
from db_models.author import Author
import pandas as pd
from load_book_recommendation_model import get_nr_items
from db_models import LikedCategories

authors_blueprint = Blueprint('authors', __name__,
                         url_prefix='/authors')
api_blueprint.register_blueprint(authors_blueprint)


@authors_blueprint.get("/")
def index():
    name = request.args.get('name', '')
    results = db.session.query(Author.id, Author.name).filter(Author.name.like(f'%{name}%')).limit(100).all()
    df = pd.DataFrame(results)
    return df.to_json(index=False, orient='records'), {'Content-Type': 'application/json'}