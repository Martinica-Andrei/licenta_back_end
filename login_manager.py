from db_models.user import User
from db import db
from flask_login import LoginManager

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()


@login_manager.unauthorized_handler
def unauthorized():
    return {"session": "Invalid session token!"}, 401
