from flask import Blueprint
from .api import api_blueprint
from flask_login import login_required, current_user

me_blueprint = Blueprint('me', __name__,
                         url_prefix='/me')
api_blueprint.register_blueprint(me_blueprint)


@me_blueprint.get("/")
@login_required
def index():
    json = {"name": current_user.name,
            "ratings": [{'title': rating.book.title, 'rating': rating.rating, 'id': rating.book_id, 
                         'image' : rating.book.image_base64(), 'link' : rating.book.link,
                         'nr_likes' : rating.book.nr_likes, 'nr_dislikes' : rating.book.nr_dislikes}
                        for rating in current_user.book_ratings]}
    return json
