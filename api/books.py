from flask import request, Blueprint, g
import pandas as pd
import utils
from load_book_recommendation_model import neighbors, item_representations
from .blueprint import api_blueprint
from db_models.book import Book
from db import db
import sqlalchemy as sa
from flask import jsonify
import base64
from pathlib import Path
from decorators.login_required import login_required

books_blueprint = Blueprint('books', __name__,
                            url_prefix='/books')
api_blueprint.register_blueprint(books_blueprint)

def get_image_base64(filename):
    if filename is None:
        return None
    filepath : Path = utils.BOOKS_DATA_IMAGES / filename
    if filepath.is_file():
        with open(filepath ,'rb') as file:
            binary_data = file.read()
            base64_bytes = base64.b64encode(binary_data)
            base64_str = base64_bytes.decode('utf-8')
            return base64_str
    else:
        return None

@books_blueprint.get("/search")
def index():
    title = request.args.get('title', '')
    words_str, words_list = utils.convert_for_word_search(title)
    count = int(request.args.get('count', 5))
    if len(words_str) == 0 or count <= 0:
        return []
    locate_str = ', '.join([f'LOCATE(:pos_{i}, title) AS pos_{i}' for i in range(len(words_list))])
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


@books_blueprint.get("/recommendations")
def books_recommendations():
    try:
        id = int(request.args.get('id'))
    except:
        return {"err": "Query string id is required."}, 400
    if id < 0 or id >= len(item_representations):
        return {"err": f"Invalid id : {id}"}, 400
    target_item = item_representations[id:id+1]
    indices = neighbors.kneighbors(target_item, return_distance=False)[0]
    indices = indices.tolist()
    results = db.session.query(Book).filter(Book.id.in_(indices)).all()
    df = pd.DataFrame([x.to_dict() for x in results])
    df.set_index('id', inplace=True)
    df = df.reindex(index=indices)
    df = df.reset_index(drop=True)
    df.rename(columns={"image_link" : "image"}, inplace=True)
    df["image"] = df["image"].apply(get_image_base64)
    # df.loc[:, ['authors', 'categories']] = df[['authors', 'categories']].fillna(
    #      '[]').map(utils.string_list_to_list)
    return df.to_json(orient='records')

@books_blueprint.post("/rate")
@login_required
def rate_book():
    print('called')
    return g.user.name