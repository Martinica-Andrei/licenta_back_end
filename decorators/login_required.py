from functools import wraps
from flask import session, g
from db import db
from db_models.user import User

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return {"session" : "Session token is required!"}, 401
        g.user = db.session.query(User).filter(User.id == session['user_id']).first()
        return func(*args, **kwargs)
    return wrapper