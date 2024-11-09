from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, autoincrement=False, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    password = Column(String(64), nullable=False)

    book_ratings = relationship('BookRating', back_populates='user')