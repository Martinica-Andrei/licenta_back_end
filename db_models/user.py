from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from db import Base
from flask_login import UserMixin

class User(Base, UserMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    password = Column(String(64), nullable=False)

    book_ratings = relationship('BookRating')