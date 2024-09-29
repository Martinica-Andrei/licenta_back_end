from flask import Flask, request, g
import pandas as pd
import sqlite3
import utils
from lightfm import LightFM
import joblib
import numpy as np
from sklearn.neighbors import NearestNeighbors
from pathlib import Path

app = Flask(__name__)

model : LightFM = joblib.load(Path('models/amazon-book-reviews-no-item-features-model.pkl'))
bias, components = model.get_item_representations() 
item_representations = np.concatenate([bias.reshape(-1,1), components], axis=1)
neighbors = NearestNeighbors(n_neighbors=6).fit(item_representations)

DATABASE = Path('sqlite.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.get("/api/books")
def books():
    db = get_db()
    title = request.args.get('title', '')
    title = utils.escape_fts(title)
    count = int(request.args.get('count', 5))
    if len(title) < 3 or count <= 0:
        return {}
    sql = """select id, title from book_data where title in 
    (select title from book_fts where book_fts match ? limit ?);"""
    df = pd.read_sql(sql, db, params=[f"{title}*", count])
    return df.to_json(index=True)

@app.get("/api/books/recommendations")
def books_recommendations():
    try:
        id = int(request.args.get('id'))
    except: 
        return "Query string id is required."
    if id < 0 or id >= len(item_representations):
        return f"Invalid id : {id}"
    target_item = item_representations[id:id+1]
        
    indices = neighbors.kneighbors(target_item, return_distance=False)[0, 1:]
    indices = indices.tolist()
    question_mark_arr = ','.join(['?'] * len(indices))
    sql = f"""select id, title, image, previewlink, infolink from book_data where id in ({question_mark_arr});"""
    db = get_db()
    df = pd.read_sql(sql, db, params=indices, index_col='id')
    df = df.reindex(index=indices)
    df = df.reset_index(drop=True)
    return df.to_json()

if __name__ == '__main__':
    app.run(debug=True)
