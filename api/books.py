from flask import request, Blueprint
import pandas as pd
import utils
import base64
from db_connection import get_db
from load_book_recommendation_models import neighbors, item_representations
from .blueprint import api_blueprint

books_blueprint = Blueprint('books', __name__,
                        url_prefix='/books')
api_blueprint.register_blueprint(books_blueprint)

def get_title_image_base64(title):
    path = utils.convert_str_to_datasets_amazon_images_path(title)
    if path.is_file() == False:
        path = utils.DATASETS_AMAZON_STATIC_IMAGES_PATH / 'no_cover.jpg'
    with open(path, 'rb') as file:
        binary_data = file.read()
        base64_bytes = base64.b64encode(binary_data)
        base64_string = base64_bytes.decode('utf-8')
        return base64_string

@books_blueprint.get("")
def index():
    db = get_db()
    title = request.args.get('title', '')
    title = utils.sanitize_fts(title)
    count = int(request.args.get('count', 5))
    if count <= 0 or len(title) == 0:
        return []
    sql = """select id, title from book_data where title in 
    (select title from book_fts where book_fts match ? limit ?);"""
    df = pd.read_sql(sql, db, params=[f"{title}*", count])
    return df.to_json(orient='records')


@books_blueprint.get("/recommendations")
def books_recommendations():
    try:
        id = int(request.args.get('id'))
    except: 
        return {"err" : "Query string id is required."}, 400
    if id < 0 or id >= len(item_representations):
        return {"err" : f"Invalid id : {id}"}, 400
    target_item = item_representations[id:id+1]
    indices = neighbors.kneighbors(target_item, return_distance=False)[0]
    indices = indices.tolist()
    question_mark_arr = ','.join(['?'] * len(indices))
    sql = f"""select id, title, description, previewlink, infolink, authors, categories from book_data where id in ({question_mark_arr});"""
    db = get_db()
    df = pd.read_sql(sql, db, params=indices, index_col='id')
    df = df.reindex(index=indices)
    df = df.reset_index(drop=True)
    df.loc[:, 'image'] = df['title'].apply(get_title_image_base64)
    df.loc[:, ['authors', 'categories']] = df[['authors', 'categories']].fillna('[]').map(utils.string_list_to_list)
    return df.to_json(orient='records')