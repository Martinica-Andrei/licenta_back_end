from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from alembic.config import Config
from app import app

class Base(DeclarativeBase):
    def to_dict(self):
        return {k : v for k, v in self.__dict__.items() if k.startswith('_') == False}

db = SQLAlchemy(model_class=Base)

alembic_cfg = Config("alembic.ini")
sqlalchemy_url = alembic_cfg.get_main_option("sqlalchemy.url")

app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_url