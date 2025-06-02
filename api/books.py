from flask import request, Blueprint
from dtos.book_ratings.post_book_rating_dto import PostBookRatingDto
from dtos.book_recommenders.by_content_dto import ByContentDto
from dtos.book_recommenders.by_id_dto import ByIdDto
from dtos.books.search_book_dto import SearchBookDto
from dtos.converter import ValidationError
from services.book_rating_service import BookRatingError, BookRatingService
from services.book_recommender_service import BookRecommenderError, BookRecommenderService
from services.book_service import BookService
from .api import api_blueprint
from db import db
from flask import jsonify
from flask_login import login_required, current_user
from csrf import csrf

books_blueprint = Blueprint('books', __name__,
                            url_prefix='/books')
api_blueprint.register_blueprint(books_blueprint)


@books_blueprint.get("/search")
def search():
    try:
        dto = SearchBookDto.convert_from_dict(request.args, '', 100)
    except ValidationError as err:
        return err.to_tuple()
    book_service = BookService(db.session)
    dtos = book_service.find_by_title_containing(dto)
    list_with_json = [dto.to_json() for dto in dtos]
    return jsonify(list_with_json)


@books_blueprint.get("/recommendations")
def books_recommendations_by_id():
    user_id = current_user.id if current_user.is_authenticated else None
    try:
        dto = ByIdDto.convert_from_dict(request.args, user_id)
    except ValidationError as err:
        return err.to_tuple()
    book_recommender_service = BookRecommenderService(db.session)
    try:
        get_dtos = book_recommender_service.get_recommendations_by_id(dto)
    except BookRecommenderError as err:
        return err.to_tuple()
    list_with_json = [dto.to_json() for dto in get_dtos]
    return jsonify(list_with_json)


@books_blueprint.post("/recommendations")
@csrf.exempt
def books_recommendations_by_content():
    user_id = current_user.id if current_user.is_authenticated else None
    body = request.get_json()
    try:
        dto = ByContentDto.convert_from_dict(body, user_id)
    except ValidationError as err:
        return err.to_tuple()
    book_recommender_service = BookRecommenderService(db.session)
    get_dtos = book_recommender_service.get_recommendations_by_content(dto)
    list_with_json = [dto.to_json() for dto in get_dtos]
    return jsonify(list_with_json)



@books_blueprint.post("/rate")
@login_required
def rate_book():
    body = request.get_json()
    try:
        dto = PostBookRatingDto.convert_from_dict(body, current_user.id)
    except ValidationError as err:
        return err.to_tuple()
    book_rating_service = BookRatingService(db.session)
    try:
        book_rating_service.rate(dto)
    except BookRatingError as err:
        return err.to_tuple()
    return {}
