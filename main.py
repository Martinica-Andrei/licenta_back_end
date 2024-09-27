from flask import Flask, request, g
import pandas as pd
import sqlite3
import utils

app = Flask(__name__)

DATABASE = 'sqlite.db'


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
    sql = """select * from book_data where title in 
    (select title from book_fts where book_fts match ? limit ?);"""
    df = pd.read_sql(sql, db, params=[f"{title}*", count])
    return df.to_json()


if __name__ == '__main__':
    app.run(debug=True)
