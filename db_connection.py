from pathlib import Path
from flask import g
import sqlite3
from app import app

DATABASE = Path('sqlite.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)

    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)

    if db is not None:
        db.close()