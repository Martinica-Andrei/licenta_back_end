from flask import Blueprint
from .api import api_blueprint
from flask_login import login_required, current_user

me_blueprint = Blueprint('me', __name__,
                            url_prefix='/me')
api_blueprint.register_blueprint(me_blueprint)

@me_blueprint.get("/")
@login_required
def index():
    json = {"name" : current_user.name, 
            "ratings" : [{'title' : rating.book.title, 'rating' : rating.rating, 'id' : rating.book_id} for rating in current_user.book_ratings]}
    return json