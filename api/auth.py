from flask import Blueprint, request
from services.auth_service import AuthService
from services.auth_service import AuthError
from .api import api_blueprint
from db import db
from csrf import csrf
from flask_login import logout_user, login_required
from dtos.auths.register_dto import RegisterDto
from dtos.auths.login_dto import LoginDto

auth_blueprint = Blueprint('auth', __name__,
                           url_prefix='/auth')
api_blueprint.register_blueprint(auth_blueprint)

@auth_blueprint.post("/register")
@csrf.exempt
def register():
    dto, invalid_message = RegisterDto.validate(request.get_json())
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
    dto, invalid_message = LoginDto.validate(request.get_json())
    if dto is None:
        return invalid_message, 400
    auth_service = AuthService(db.session)
    try:
        return auth_service.login_user(dto)
    except AuthError as err:
        return err.to_tuple()

@auth_blueprint.get('/logoff')
def logoff():
    logout_user()
    return {}
    
@auth_blueprint.post('/check_session')
@login_required
def check_session():
    return {}