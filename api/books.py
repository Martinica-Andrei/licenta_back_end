from flask import request, Blueprint
import pandas as pd
from dtos.book_ratings.post_book_rating_dto import PostBookRatingDto
from dtos.books.book_recomendation_by_content_dto import BookRecommendationByContentDto
from dtos.books.book_recommendation_by_id_dto import BookRecommendationByIdDto
from dtos.books.search_book_dto import SearchBookDto
from dtos.converter import ValidationError
from repositories.book_recommender_repository import BookRecommenderRepository
from services.book_rating_service import BookRatingError, BookRatingService
from services.book_service import BookService
from load_book_recommendation_model import (neighbors,
                                            model_item_representations,
                                            item_preprocessing,
                                            model,
                                            item_features)
from .api import api_blueprint
from db_models.book import Book
from db_models.book_rating import BookRating
from db_models.author import Author
from db_models.book_authors import BookAuthors
from db_models.category import Category
from db_models.book_categories import BookCategories
from db import db
import sqlalchemy as sa
from flask import jsonify
from flask_login import login_required, current_user
from thread_locks import books_model_memory_change_lock
from sqlalchemy import func, literal_column
import numpy as np
from csrf import csrf
from scipy.sparse import hstack, csr_matrix

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


@books_blueprint.route("/recommendations", methods=['GET', 'POST'])
@csrf.exempt
def books_recommendations():
    if request.method == 'GET':
        try:
            dto = BookRecommendationByIdDto.convert_from_dict(request.args)
        except ValidationError as err:
            return err.to_tuple()
        id = dto.id
        indices = BookRecommenderRepository.find_nearest_neighbors_by_id(id)
    else:
        body = request.get_json()
        try:
            dto = BookRecommendationByContentDto.convert_from_dict(body)
        except ValidationError as err:
            return err.to_tuple()
        indices = BookRecommenderRepository.get_nearest_neighbors_by_content(dto.content, dto.categories, dto.authors)

    indices = indices.tolist()
    grp_conc_sep = ' | '
    ifnull = ' '

    # query with Book.__table__.columns so it returns named tuples instead of Book objects
    # it is easy to convert named tuples to DataFrame
    # unfortunately , there isn't a easier way to add custom separator other than using the syntax below
    # group concat discards nulls therefore ifnull converts nulls to spaces
    # query fetches book, authors and author roles based on indices
    query = db.session.query(Book.__table__.columns,
                             func.group_concat(func.ifnull(Author.name, ifnull).op(
                                 'SEPARATOR')(literal_column(f'"{grp_conc_sep}"'))).label('author_names'),
                             func.group_concat(func.ifnull(BookAuthors.role, ifnull).op(
                                 'SEPARATOR')(literal_column(f'"{grp_conc_sep}"'))).label('author_roles')).filter(
        Book.id.in_(indices)).outerjoin(BookAuthors, BookAuthors.book_id == Book.id).outerjoin(
            Author, Author.id == BookAuthors.author_id).group_by(Book).subquery()
    # query1 adds categories to query
    query1 = db.session.query(query,
                              func.group_concat(func.ifnull(Category.name, ifnull).op(
                                  'SEPARATOR')(literal_column(f'"{grp_conc_sep}"'))).label('categories')).outerjoin(
        BookCategories, BookCategories.book_id == query.c.id).outerjoin(
        Category, Category.id == BookCategories.category_id
    ).group_by(query)

    if current_user.is_authenticated:
        query1 = query1.subquery()
        # add user rating for each book
        query2 = db.session.query(BookRating).filter(
            BookRating.user_id == current_user.id).subquery()
        results = db.session.query(query1, query2.c.rating).outerjoin(
            query2, query1.c.id == query2.c.book_id).all()
    else:
        results = query1.all()

    df = pd.DataFrame(results)

    df['author_names'] = df['author_names'].apply(
        lambda x: [v if v != ifnull else np.nan for v in x.split(grp_conc_sep)])
    df['author_roles'] = df['author_roles'].apply(
        lambda x: [v if v != ifnull else np.nan for v in x.split(grp_conc_sep)])
    df['authors'] = df[['author_names', 'author_roles']].apply(lambda x: {name: role for name, role in
                                                                          zip(x['author_names'], x['author_roles'])}, axis=1)

    df.drop(columns=['author_names', 'author_roles'], inplace=True)
    # str.split takes regex and | needs to be escaped therefore use lambda to split
    df['categories'] = df['categories'].apply(lambda x: x.split(grp_conc_sep))
    df.set_index('id', inplace=True)
    df = df.reindex(index=indices)
    df = df.reset_index(drop=False)

    df.rename(columns={"image_link": "image"}, inplace=True)
    df["image"] = df["image"].apply(Book.get_image_base64)

    return df.to_json(orient='records'), {'Content-Type': 'application/json'}


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
