from flask_login import LoginManager
login_manager = LoginManager()
from db import db
from db_models.user import User

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.id == user_id).first()

