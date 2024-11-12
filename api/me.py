from flask import Blueprint, g, jsonify
from .api import api_blueprint
from db import db
from decorators.login_required import login_required

me_blueprint = Blueprint('me', __name__,
                            url_prefix='/me')
api_blueprint.register_blueprint(me_blueprint)

@me_blueprint.get("/")
@login_required
def index():
    json = {"name" : g.user.name, "ratings" : [{'title' : rating.book.title, 'rating' : rating.rating, 'id' : rating.book_id} for rating in g.user.book_ratings]}
    return jsonify(json)