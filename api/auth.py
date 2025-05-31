from flask import Blueprint, request
from services.auth_service import AuthService
from services.auth_service import AuthError
from .api import api_blueprint
from db import db
from csrf import csrf
from flask_login import logout_user, login_required
from dtos.auths.create_auth_dto import CreateAuthDto
from dtos.auths.get_auth_dto import GetAuthDto

auth_blueprint = Blueprint('auth', __name__,
                           url_prefix='/auth')
api_blueprint.register_blueprint(auth_blueprint)

@auth_blueprint.post("/register")
@csrf.exempt
def register():
    dto, invalid_message = CreateAuthDto.validate(request.get_json())
    if dto is None:
        return invalid_message, 400
    auth_service = AuthService(db.session)
    password = dto.password # store password because it will be hashed
    try:
        dto = auth_service.create_user(dto)
    except AuthError as err:
        return err.to_tuple()
    try:
        dto.password = password # set to initial unhashed password
        return auth_service.login_user(dto)
    except AuthError as err:
        return err.to_tuple()

@auth_blueprint.post("/login")
@csrf.exempt
def login():
    dto, invalid_message = GetAuthDto.validate(request.get_json())
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