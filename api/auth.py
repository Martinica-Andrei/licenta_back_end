from flask import Blueprint, request, make_response, Response
from .blueprint import api_blueprint
from flask import jsonify
import re
import hashlib
from db_models.user import User
from db_models.auth_token import AuthToken
from db import db
from decorators.login_required import login_required

auth_blueprint = Blueprint('auth', __name__,
                           url_prefix='/auth')
api_blueprint.register_blueprint(auth_blueprint)


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def register_validation(body):
    if 'name' not in body:
        return {"name": "Name is required!"}, 400
    name = body['name']
    if len(name) == 0 or len(name) > 50:
        return {"name": "Name must have a length between 1 and 50!"}, 400
    if re.search(r'[^a-zA-Z0-9_]', name):
        return {"name": "Name can only contain alphanumerical characters and underscore!"}, 400
    user = db.session.query(User.name).where(User.name == name).first()
    if user is not None:
        return {"name": f'Name "{name}" is already taken!'}, 400
    if 'password' not in body:
        return {"password": "Password is required!"}, 400
    password = body['password']
    if len(password) == 0 or len(password) > 30:
        return {"password": "Password must have a length between 1 and 30"}, 400
    if re.search(r'\s', password):
        return {"password": "Password must not contain spaces!"}, 400
    return True


def login_validation(body):
    if 'name' not in body:
        return {"name": "Name is required!"}, 400
    name = body['name']
    user = db.session.query(User).where(User.name == name).first()
    if user is None:
        return {"name": f'User doesn\'t exist!'}, 400
    if 'password' not in body:
        return {"password": "Password is required!"}, 400
    hashed_password = hash_password(body['password'])
    if user.password != hashed_password:
        return {"password": "Incorrect password!"}, 400
    if "days_until_expiration" in body:
        try:
            body['days_until_expiration'] = int(body['days_until_expiration'])
        except:
            return {"days_until_expiration": "Must be int!"}
        if body['days_until_expiration'] <= 0:
            return {"days_until_expiration": "Must be greater than 0!"}
    else:
        body['days_until_expiration'] = 1
    return user


def set_session_token(response: Response, token: str, days_until_expiration: int):
    response.headers.add('Set-Cookie',
                         f'sessionToken={token};' +
                         f'max_age={86400*days_until_expiration};' +
                         f'HttpOnly;' +
                         f'SameSite=None;' +
                         f'Secure;' +
                         f'Path=/;' +
                         f'Partitioned;')


@auth_blueprint.post("/register")
def register():
    body = request.get_json()
    body = {k.lower(): v for k, v in body.items()}
    validation_result = register_validation(body)
    if validation_result != True:
        return validation_result
    password_hashed = hash_password(body['password'])
    user = User(name=body['name'], password=password_hashed)
    db.session.add(user)
    db.session.commit()

    response = make_response()
    days_until_expiration = 1
    token = AuthToken.authenticate(days_until_expiration, user.id)
    set_session_token(response, token, days_until_expiration)
    return response


@auth_blueprint.post("/login")
def login():
    body = request.get_json()
    body = {k.lower(): v for k, v in body.items()}
    # login_validation returns user if valid, else returns dictionary with error
    user_or_error = login_validation(body)
    if type(user_or_error) is not User:
        return user_or_error
    user = user_or_error
    AuthToken.remove_expired_tokens_from_user(user.id)

    response = make_response()
    days_until_expiration = body['days_until_expiration']
    token = AuthToken.authenticate(days_until_expiration, user.id)
    set_session_token(response, token, days_until_expiration)
    return response

@auth_blueprint.get('/check_session')
@login_required
def check_session():
    return make_response()