from flask import request, Blueprint
import pandas as pd
import utils
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


def validate_rate_book(body):
    if 'book_id' not in body:
        return {"book_id": "Book id is required!"}, 400
    book_id = body['book_id']
    book = db.session.query(Book.id).filter(Book.id == book_id).first()
    if book is None:
        return {"book_id": f"Book with id {book_id} doesn't exist!"}, 400
    if 'rating' not in body:
        return {"rating": "Rating is required!"}, 400
    body['rating'] = body['rating'].lower()
    if body['rating'] not in ['like', 'dislike', 'none']:
        return {"rating": "Rating must have value 'like', 'dislike' or 'none'!"}, 400
    return True

def validate_recommendations(body):
    if 'content' not in body:
        return {'content': 'Content is required!'}, 400
    if 'authors' not in body:
        body['authors'] = []
    elif type(body['authors']) is not list:
        return {'authors' :'Authors must be an array!'}, 400
    if 'categories' not in body:
        body['categories'] = []
    elif type(body['categories']) is not list:
        return {'categories' :'Categories must be an array!'}, 400
    return True

@books_blueprint.get("/search")
def search():
    title = request.args.get('title', '')
    words_str, words_list = utils.convert_for_word_search(title)
    count = int(request.args.get('count', 5))
    if len(words_str) == 0 or count <= 0:
        return []
    locate_str = ', '.join(
        [f'LOCATE(:pos_{i}, title) AS pos_{i}' for i in range(len(words_list))])
    pos_names = [f'pos_{i}' for i in range(len(words_list))]
    query = f"""SELECT id, title FROM
                (SELECT id, title, LENGTH(title) as len_title, {locate_str} 
                FROM book WHERE MATCH(title) AGAINST (:title IN BOOLEAN MODE) ORDER BY {', '.join(pos_names)}, 
                len_title LIMIT :limit) as query 
            """
    params = dict(zip(pos_names, words_list))
    params['title'] = words_str
    params['limit'] = count
    results = db.session.execute(sa.text(query), params).fetchall()
    results = [{"id": x[0], "title": x[1]} for x in results]
    return jsonify(results)


@books_blueprint.route("/recommendations", methods=['GET', 'POST'])
@csrf.exempt
def books_recommendations():
    if request.method == 'GET':
        try:
            id = int(request.args.get('id'))
        except:
            return {"err": "Query string id is required."}, 400
        with books_model_memory_change_lock.gen_rlock():
            item_representations = model_item_representations()
            if id < 0 or id >= len(item_representations):
                return {"err": f"Invalid id : {id}"}, 400
            target_item = item_representations[id:id+1]
            indices = neighbors.kneighbors(target_item, return_distance=False)[0]
    else:
        body = request.get_json()
        body = {k.lower(): v for k, v in body.items()}
        validation_result = validate_recommendations(body)
        if validation_result != True:
            return validation_result
        content, categories, authors = body['content'], body['categories'], body['authors']
        feature_df = pd.DataFrame({'content' : [content], 'categories' : [categories], 'authors' : [authors]})  
        transformed = item_preprocessing().transform(feature_df)
        with books_model_memory_change_lock.gen_rlock():
            nr_zeros_to_add = item_features().shape[1] - transformed.shape[1]
            transformed = hstack([transformed, csr_matrix((1, nr_zeros_to_add))])
            bias, components = model.get_item_representations(transformed)
            item_representations = np.concatenate([bias.reshape(-1,1), components], axis=1)
            indices = neighbors.kneighbors(item_representations, return_distance=False)[0]

    indices = indices.tolist()
    grp_conc_sep = ' | '
    ifnull = ' '
    
    # query with Book.__table__.columns so it returns named tuples instead of Book objects
    # it is easy to convert named tuples to DataFrame
    # unfortunately , there isn't a easier way to add custom separator other than using the syntax below
    # group concat discards nulls therefore ifnull converts nulls to spaces
    #query fetches book, authors and author roles based on indices
    query = db.session.query(Book.__table__.columns, 
                                func.group_concat(func.ifnull(Author.name, ifnull).op(
                                    'SEPARATOR')(literal_column(f'"{grp_conc_sep}"'))).label('author_names'), 
                                func.group_concat(func.ifnull(BookAuthors.role, ifnull).op(
                                    'SEPARATOR')(literal_column(f'"{grp_conc_sep}"'))).label('author_roles')).filter(
        Book.id.in_(indices)).outerjoin(BookAuthors, BookAuthors.book_id == Book.id).outerjoin(
            Author, Author.id == BookAuthors.author_id).group_by(Book).subquery()
    #query1 adds categories to query
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

    df['author_names'] = df['author_names'].apply(lambda x : [v if v != ifnull else np.nan for v in x.split(grp_conc_sep)])
    df['author_roles'] = df['author_roles'].apply(lambda x : [v if v != ifnull else np.nan for v in x.split(grp_conc_sep)])
    df['authors'] = df[['author_names', 'author_roles']].apply(lambda x : {name : role for name, role in 
                                                                          zip(x['author_names'], x['author_roles'])}, axis=1)
    
    df.drop(columns=['author_names','author_roles'], inplace=True)
    # str.split takes regex and | needs to be escaped therefore use lambda to split
    df['categories'] = df['categories'].apply(lambda x : x.split(grp_conc_sep))
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
    body = {k.lower(): v for k, v in body.items()}
    validation_result = validate_rate_book(body)
    if validation_result != True:
        return validation_result
    book_id = body['book_id']
    rating = body['rating']
    book_rating = db.session.query(BookRating).filter(sa.and_(
        BookRating.book_id == book_id, BookRating.user_id == current_user.id)).first()
    if book_rating is None:
        if rating != 'none':
            book_rating = BookRating(
                book_id=book_id, user_id=current_user.id, rating=rating)
            db.session.add(book_rating)
            db.session.commit()
        return {}
    if rating != 'none':
        book_rating.rating = rating
        db.session.commit()
        return {}
    db.session.delete(book_rating)
    db.session.commit()
    return {}
