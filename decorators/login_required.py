from functools import wraps
from flask import request, g
from db import db
from db_models.auth_token import AuthToken

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "auth_token" not in request.cookies:
            return {"auth_token" : "Auth token is required!"}, 401
        auth_token = request.cookies['auth_token']
        auth_token = db.session.query(AuthToken).filter(AuthToken.token == AuthToken.hash_token(auth_token)).first()
        if auth_token is None or auth_token.is_expired():
            return {"auth_token" : "Invalid auth token!"}, 401
        g.user = auth_token.user
        return func(*args, **kwargs)
    return wrapper