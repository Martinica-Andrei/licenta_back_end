from flask import Blueprint, request
from services.auth_service import AuthService
from services.auth_service import AuthError
from .api import api_blueprint
from db import db
from csrf import csrf
from flask_login import logout_user, login_required
from dtos.auths.register_dto import RegisterDto
from dtos.auths.login_dto import LoginDto
from flask_wtf.csrf import generate_csrf

auth_blueprint = Blueprint('auth', __name__,
                           url_prefix='/auth')
api_blueprint.register_blueprint(auth_blueprint)

@auth_blueprint.post("/register")
@csrf.exempt
def register():
    """
    Registers and logins user. If valid returns csrf_token, otherwise returns key: err message.
    """
    dto, invalid_message = RegisterDto.convert_from_dict(request.get_json())
    if dto is None:
        return invalid_message, 400
    auth_service = AuthService(db.session)
    try:
        dto = auth_service.register(dto)
    except AuthError as err:
        return err.to_tuple()
    try:
        return auth_service.login_user(dto)
    except AuthError as err:
        return err.to_tuple()

@auth_blueprint.post("/login")
@csrf.exempt
def login():
    """
    Logins user. If valid returns csrf_token, otherwise returns key: err message.
    """
    dto, invalid_message = LoginDto.convert_from_dict(request.get_json())
    if dto is None:
        return invalid_message, 400
    auth_service = AuthService(db.session)
    try:
        return auth_service.login_user(dto)
    except AuthError as err:
        return err.to_tuple()

@auth_blueprint.get('/logoff')
def logoff():
    """
    Logs off the user and returns nothing.
    """
    logout_user()
    return {}
    
@auth_blueprint.post('/check_session')
@login_required
@csrf.exempt
def check_session():
    """
    Check if user is authenticated using remember me or session.
    Refreshes the csrf_token in case user is authenticated with remember me.
    """
    return {'csrf_token': generate_csrf()}