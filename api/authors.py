from flask import Blueprint, request
from flask import jsonify
from services.author_service import AuthorService
from .api import api_blueprint
from db import db

authors_blueprint = Blueprint('authors', __name__,
                         url_prefix='/authors')
api_blueprint.register_blueprint(authors_blueprint)


@authors_blueprint.get("/")
def index():
    """Gets max 100 authors that have name from query string `name`."""
    name = request.args.get('name', '')
    author_service = AuthorService(db.session)
    dtos = author_service.find_by_name_containing(name, 0, 100)
    list_with_json = [dto.to_json() for dto in dtos]
    return jsonify(list_with_json)