from sqlalchemy import Column, String, Integer
from db import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    password = Column(String(64), nullable=False)